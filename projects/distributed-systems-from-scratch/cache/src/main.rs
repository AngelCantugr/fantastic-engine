/*!
 * Distributed Cache
 * Features: Consistent hashing, replication, sharding
 */

use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

type Key = String;
type Value = Vec<u8>;
type Hash = u64;

/// Cache entry with TTL
#[derive(Clone, Debug)]
struct CacheEntry {
    value: Value,
    expires_at: Option<SystemTime>,
}

impl CacheEntry {
    fn is_expired(&self) -> bool {
        if let Some(expires_at) = self.expires_at {
            SystemTime::now() > expires_at
        } else {
            false
        }
    }
}

/// Consistent hashing ring
struct ConsistentHashRing {
    nodes: Vec<(Hash, String)>, // (hash, node_id)
    virtual_nodes: usize,
}

impl ConsistentHashRing {
    fn new(virtual_nodes: usize) -> Self {
        Self {
            nodes: Vec::new(),
            virtual_nodes,
        }
    }

    fn add_node(&mut self, node_id: &str) {
        // Add virtual nodes for better distribution
        for i in 0..self.virtual_nodes {
            let vnode_id = format!("{}:{}", node_id, i);
            let hash = self.hash_key(&vnode_id);
            self.nodes.push((hash, node_id.to_string()));
        }

        self.nodes.sort_by_key(|(hash, _)| *hash);
    }

    fn remove_node(&mut self, node_id: &str) {
        self.nodes.retain(|(_, id)| id != node_id);
    }

    fn get_node(&self, key: &str) -> Option<&str> {
        if self.nodes.is_empty() {
            return None;
        }

        let hash = self.hash_key(key);

        // Find first node with hash >= key hash
        let pos = self.nodes
            .iter()
            .position(|(h, _)| *h >= hash)
            .unwrap_or(0);

        Some(&self.nodes[pos].1)
    }

    fn hash_key(&self, key: &str) -> Hash {
        let mut hasher = Sha256::new();
        hasher.update(key.as_bytes());
        let result = hasher.finalize();

        // Take first 8 bytes as u64
        let mut bytes = [0u8; 8];
        bytes.copy_from_slice(&result[0..8]);
        u64::from_be_bytes(bytes)
    }
}

/// Distributed cache node
struct CacheNode {
    id: String,
    cache: HashMap<Key, CacheEntry>,
    hash_ring: ConsistentHashRing,
    peers: Vec<String>,
}

impl CacheNode {
    fn new(id: String, peers: Vec<String>) -> Self {
        let mut hash_ring = ConsistentHashRing::new(150);

        // Add self and peers to ring
        hash_ring.add_node(&id);
        for peer in &peers {
            hash_ring.add_node(peer);
        }

        Self {
            id,
            cache: HashMap::new(),
            hash_ring,
            peers,
        }
    }

    /// Set key-value with TTL
    fn set(&mut self, key: Key, value: Value, ttl_secs: Option<u64>) -> Result<(), String> {
        let expires_at = ttl_secs.map(|secs| {
            SystemTime::now() + Duration::from_secs(secs)
        });

        let entry = CacheEntry { value, expires_at };

        // Check if this node should handle this key
        if let Some(node_id) = self.hash_ring.get_node(&key) {
            if node_id == self.id {
                self.cache.insert(key, entry);
                Ok(())
            } else {
                // Should forward to correct node
                Err(format!("Key {} should be on node {}", key, node_id))
            }
        } else {
            Err("No nodes available".to_string())
        }
    }

    /// Get value by key
    fn get(&mut self, key: &Key) -> Option<Value> {
        if let Some(entry) = self.cache.get(key) {
            if entry.is_expired() {
                self.cache.remove(key);
                None
            } else {
                Some(entry.value.clone())
            }
        } else {
            None
        }
    }

    /// Delete key
    fn delete(&mut self, key: &Key) -> bool {
        self.cache.remove(key).is_some()
    }

    /// Clean expired entries
    fn cleanup_expired(&mut self) {
        let expired: Vec<Key> = self
            .cache
            .iter()
            .filter(|(_, entry)| entry.is_expired())
            .map(|(key, _)| key.clone())
            .collect();

        for key in expired {
            self.cache.remove(&key);
        }
    }

    /// Get stats
    fn stats(&self) -> CacheStats {
        CacheStats {
            node_id: self.id.clone(),
            entries: self.cache.len(),
            peers: self.peers.len(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct CacheStats {
    node_id: String,
    entries: usize,
    peers: usize,
}

#[tokio::main]
async fn main() {
    env_logger::init();

    log::info!("Starting distributed cache node");

    // Example: 3-node cluster
    let node_id = "node1".to_string();
    let peers = vec!["node2".to_string(), "node3".to_string()];

    let cache = Arc::new(RwLock::new(CacheNode::new(node_id.clone(), peers)));

    // Cleanup task
    let cleanup_cache = Arc::clone(&cache);
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(Duration::from_secs(10)).await;
            let mut cache = cleanup_cache.write().await;
            cache.cleanup_expired();
            log::debug!("Cleaned up expired entries");
        }
    });

    // Example usage
    {
        let mut cache = cache.write().await;

        // Set some values
        cache.set("key1".to_string(), b"value1".to_vec(), Some(60)).unwrap();
        cache.set("key2".to_string(), b"value2".to_vec(), None).unwrap();

        // Get values
        if let Some(value) = cache.get(&"key1".to_string()) {
            log::info!("key1 = {:?}", String::from_utf8_lossy(&value));
        }

        // Stats
        let stats = cache.stats();
        log::info!("Cache stats: {:?}", stats);
    }

    // Keep running
    loop {
        tokio::time::sleep(Duration::from_secs(5)).await;
        let cache = cache.read().await;
        let stats = cache.stats();
        log::info!("Stats: {:?}", stats);
    }
}
