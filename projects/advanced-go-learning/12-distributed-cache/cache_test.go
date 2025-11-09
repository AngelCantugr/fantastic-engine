package cache

import (
	"testing"
	"time"
)

func TestLRUCache(t *testing.T) {
	cache := NewLRUCache(2)

	cache.Set("a", 1, time.Hour)
	cache.Set("b", 2, time.Hour)

	if val, ok := cache.Get("a"); !ok || val.(int) != 1 {
		t.Error("Failed to get 'a'")
	}

	cache.Set("c", 3, time.Hour)

	if _, ok := cache.Get("b"); ok {
		t.Error("'b' should have been evicted")
	}
}

func TestLRUCacheTTL(t *testing.T) {
	cache := NewLRUCache(10)

	cache.Set("a", 1, 100*time.Millisecond)

	time.Sleep(150 * time.Millisecond)

	if _, ok := cache.Get("a"); ok {
		t.Error("'a' should have expired")
	}
}

func TestConsistentHash(t *testing.T) {
	ch := NewConsistentHash(3)

	ch.AddNode("node1")
	ch.AddNode("node2")
	ch.AddNode("node3")

	node1 := ch.GetNode("key1")
	node2 := ch.GetNode("key1")

	if node1 != node2 {
		t.Error("Same key should map to same node")
	}

	ch.RemoveNode("node1")

	node3 := ch.GetNode("key1")
	if node3 == node1 {
		t.Error("Key should remap after node removal")
	}
}

func TestDistributedCache(t *testing.T) {
	nodes := []string{"node1", "node2", "node3"}
	dc := NewDistributedCache(nodes, 100)

	dc.Set("key1", "value1", time.Hour)
	dc.Set("key2", "value2", time.Hour)

	if val, ok := dc.Get("key1"); !ok || val.(string) != "value1" {
		t.Error("Failed to get key1")
	}

	dc.Delete("key1")

	if _, ok := dc.Get("key1"); ok {
		t.Error("key1 should be deleted")
	}
}

func BenchmarkLRUCacheSet(b *testing.B) {
	cache := NewLRUCache(1000)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cache.Set("key", i, time.Hour)
	}
}

func BenchmarkLRUCacheGet(b *testing.B) {
	cache := NewLRUCache(1000)
	cache.Set("key", 42, time.Hour)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		cache.Get("key")
	}
}
