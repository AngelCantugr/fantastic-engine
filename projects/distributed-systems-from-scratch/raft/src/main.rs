/*!
 * Raft Consensus Implementation
 * Based on "In Search of an Understandable Consensus Algorithm"
 */

use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::{mpsc, RwLock};
use tokio::time;
use serde::{Deserialize, Serialize};
use rand::Rng;

/// Node ID type
type NodeId = u64;

/// Term number
type Term = u64;

/// Log index
type LogIndex = u64;

/// Raft node state
#[derive(Debug, Clone, PartialEq)]
enum NodeState {
    Follower,
    Candidate,
    Leader,
}

/// Log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
struct LogEntry {
    term: Term,
    index: LogIndex,
    command: Vec<u8>,
}

/// RPC: RequestVote
#[derive(Debug, Serialize, Deserialize)]
struct RequestVoteRequest {
    term: Term,
    candidate_id: NodeId,
    last_log_index: LogIndex,
    last_log_term: Term,
}

#[derive(Debug, Serialize, Deserialize)]
struct RequestVoteResponse {
    term: Term,
    vote_granted: bool,
}

/// RPC: AppendEntries
#[derive(Debug, Serialize, Deserialize)]
struct AppendEntriesRequest {
    term: Term,
    leader_id: NodeId,
    prev_log_index: LogIndex,
    prev_log_term: Term,
    entries: Vec<LogEntry>,
    leader_commit: LogIndex,
}

#[derive(Debug, Serialize, Deserialize)]
struct AppendEntriesResponse {
    term: Term,
    success: bool,
}

/// Raft node
struct RaftNode {
    // Persistent state
    id: NodeId,
    current_term: Term,
    voted_for: Option<NodeId>,
    log: Vec<LogEntry>,

    // Volatile state
    commit_index: LogIndex,
    last_applied: LogIndex,
    state: NodeState,

    // Leader state
    next_index: HashMap<NodeId, LogIndex>,
    match_index: HashMap<NodeId, LogIndex>,

    // Cluster configuration
    peers: Vec<NodeId>,

    // Election timeout
    election_timeout_ms: (u64, u64),
}

impl RaftNode {
    fn new(id: NodeId, peers: Vec<NodeId>) -> Self {
        Self {
            id,
            current_term: 0,
            voted_for: None,
            log: vec![],
            commit_index: 0,
            last_applied: 0,
            state: NodeState::Follower,
            next_index: HashMap::new(),
            match_index: HashMap::new(),
            peers,
            election_timeout_ms: (150, 300),
        }
    }

    /// Get random election timeout
    fn random_election_timeout(&self) -> Duration {
        let mut rng = rand::thread_rng();
        let timeout_ms = rng.gen_range(self.election_timeout_ms.0..=self.election_timeout_ms.1);
        Duration::from_millis(timeout_ms)
    }

    /// Start election (become candidate)
    fn start_election(&mut self) {
        self.state = NodeState::Candidate;
        self.current_term += 1;
        self.voted_for = Some(self.id);

        log::info!(
            "Node {} starting election for term {}",
            self.id,
            self.current_term
        );
    }

    /// Handle RequestVote RPC
    fn handle_request_vote(&mut self, request: RequestVoteRequest) -> RequestVoteResponse {
        let mut vote_granted = false;

        // Update term if necessary
        if request.term > self.current_term {
            self.current_term = request.term;
            self.voted_for = None;
            self.state = NodeState::Follower;
        }

        // Grant vote if:
        // 1. Haven't voted this term OR already voted for this candidate
        // 2. Candidate's log is at least as up-to-date as ours
        if request.term == self.current_term {
            let can_vote = self.voted_for.is_none() || self.voted_for == Some(request.candidate_id);

            let (last_log_index, last_log_term) = self.last_log_info();
            let log_ok = request.last_log_term > last_log_term
                || (request.last_log_term == last_log_term
                    && request.last_log_index >= last_log_index);

            if can_vote && log_ok {
                self.voted_for = Some(request.candidate_id);
                vote_granted = true;
            }
        }

        RequestVoteResponse {
            term: self.current_term,
            vote_granted,
        }
    }

    /// Handle AppendEntries RPC
    fn handle_append_entries(&mut self, request: AppendEntriesRequest) -> AppendEntriesResponse {
        // Update term
        if request.term > self.current_term {
            self.current_term = request.term;
            self.voted_for = None;
            self.state = NodeState::Follower;
        }

        let mut success = false;

        if request.term == self.current_term {
            // Convert to follower if we were candidate/leader
            self.state = NodeState::Follower;

            // Check if log matches at prev_log_index
            if request.prev_log_index == 0
                || (request.prev_log_index as usize <= self.log.len()
                    && self.log[request.prev_log_index as usize - 1].term == request.prev_log_term)
            {
                // Append entries
                for entry in request.entries {
                    if entry.index as usize <= self.log.len() {
                        // Overwrite conflicting entry
                        self.log[entry.index as usize - 1] = entry;
                    } else {
                        // Append new entry
                        self.log.push(entry);
                    }
                }

                // Update commit index
                if request.leader_commit > self.commit_index {
                    self.commit_index = std::cmp::min(request.leader_commit, self.log.len() as u64);
                }

                success = true;
            }
        }

        AppendEntriesResponse {
            term: self.current_term,
            success,
        }
    }

    /// Get last log info
    fn last_log_info(&self) -> (LogIndex, Term) {
        self.log
            .last()
            .map(|entry| (entry.index, entry.term))
            .unwrap_or((0, 0))
    }

    /// Become leader
    fn become_leader(&mut self) {
        log::info!("Node {} became leader for term {}", self.id, self.current_term);
        self.state = NodeState::Leader;

        // Initialize leader state
        let next_index = self.log.len() as u64 + 1;
        for peer_id in &self.peers {
            self.next_index.insert(*peer_id, next_index);
            self.match_index.insert(*peer_id, 0);
        }
    }
}

#[tokio::main]
async fn main() {
    env_logger::init();

    log::info!("Starting Raft node");

    // Example: 3-node cluster
    let node_id = 1;
    let peers = vec![2, 3];

    let node = Arc::new(RwLock::new(RaftNode::new(node_id, peers)));

    // Election timeout task
    let election_node = Arc::clone(&node);
    tokio::spawn(async move {
        loop {
            let timeout = {
                let node = election_node.read().await;
                node.random_election_timeout()
            };

            time::sleep(timeout).await;

            let mut node = election_node.write().await;
            if node.state == NodeState::Follower || node.state == NodeState::Candidate {
                node.start_election();
            }
        }
    });

    // Heartbeat task (leader only)
    let heartbeat_node = Arc::clone(&node);
    tokio::spawn(async move {
        loop {
            time::sleep(Duration::from_millis(50)).await;

            let node = heartbeat_node.read().await;
            if node.state == NodeState::Leader {
                log::debug!("Sending heartbeats");
                // Send AppendEntries to all peers
            }
        }
    });

    // Keep running
    loop {
        time::sleep(Duration::from_secs(1)).await;
        let node = node.read().await;
        log::info!("Node {} - State: {:?}, Term: {}", node.id, node.state, node.current_term);
    }
}
