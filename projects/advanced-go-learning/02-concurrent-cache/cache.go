package cache

import (
	"container/list"
	"hash/fnv"
	"sync"
	"time"
)

// Cache is the interface for all cache implementations
type Cache interface {
	Get(key string) (interface{}, bool)
	Set(key string, value interface{})
	SetWithTTL(key string, value interface{}, ttl time.Duration)
	Delete(key string)
	Clear()
	Len() int
	Stats() CacheStats
}

// CacheStats tracks cache performance metrics
type CacheStats struct {
	Hits   int64
	Misses int64
	Evictions int64
}

// entry represents a cache entry with metadata
type entry struct {
	key       string
	value     interface{}
	expiresAt time.Time
	listElem  *list.Element
}

// shard represents a single cache shard
type shard struct {
	mu      sync.RWMutex
	items   map[string]*entry
	lruList *list.List
	maxSize int
	hits    int64
	misses  int64
	evictions int64
}

// ShardedLRUCache implements a sharded LRU cache
type ShardedLRUCache struct {
	shards    []*shard
	shardMask uint32
}

// NewShardedLRUCache creates a new sharded LRU cache
func NewShardedLRUCache(shardCount, maxSizePerShard int) *ShardedLRUCache {
	// Ensure shard count is power of 2 for efficient modulo
	if shardCount&(shardCount-1) != 0 {
		panic("shard count must be power of 2")
	}

	c := &ShardedLRUCache{
		shards:    make([]*shard, shardCount),
		shardMask: uint32(shardCount - 1),
	}

	for i := 0; i < shardCount; i++ {
		c.shards[i] = &shard{
			items:   make(map[string]*entry),
			lruList: list.New(),
			maxSize: maxSizePerShard,
		}
	}

	return c
}

// getShard returns the shard for a given key
func (c *ShardedLRUCache) getShard(key string) *shard {
	h := fnv.New32a()
	h.Write([]byte(key))
	hash := h.Sum32()
	return c.shards[hash&c.shardMask]
}

// Get retrieves a value from the cache
func (c *ShardedLRUCache) Get(key string) (interface{}, bool) {
	s := c.getShard(key)
	s.mu.Lock()
	defer s.mu.Unlock()

	e, ok := s.items[key]
	if !ok {
		s.misses++
		return nil, false
	}

	// Check TTL expiration
	if !e.expiresAt.IsZero() && time.Now().After(e.expiresAt) {
		s.removeEntry(e)
		s.misses++
		return nil, false
	}

	// Move to front (most recently used)
	s.lruList.MoveToFront(e.listElem)
	s.hits++
	return e.value, true
}

// Set adds a value to the cache
func (c *ShardedLRUCache) Set(key string, value interface{}) {
	c.SetWithTTL(key, value, 0)
}

// SetWithTTL adds a value with expiration time
func (c *ShardedLRUCache) SetWithTTL(key string, value interface{}, ttl time.Duration) {
	s := c.getShard(key)
	s.mu.Lock()
	defer s.mu.Unlock()

	var expiresAt time.Time
	if ttl > 0 {
		expiresAt = time.Now().Add(ttl)
	}

	// Update existing entry
	if e, ok := s.items[key]; ok {
		e.value = value
		e.expiresAt = expiresAt
		s.lruList.MoveToFront(e.listElem)
		return
	}

	// Add new entry
	e := &entry{
		key:       key,
		value:     value,
		expiresAt: expiresAt,
	}
	e.listElem = s.lruList.PushFront(e)
	s.items[key] = e

	// Evict if necessary
	if s.lruList.Len() > s.maxSize {
		s.evictOldest()
	}
}

// Delete removes a key from the cache
func (c *ShardedLRUCache) Delete(key string) {
	s := c.getShard(key)
	s.mu.Lock()
	defer s.mu.Unlock()

	if e, ok := s.items[key]; ok {
		s.removeEntry(e)
	}
}

// Clear removes all entries
func (c *ShardedLRUCache) Clear() {
	for _, s := range c.shards {
		s.mu.Lock()
		s.items = make(map[string]*entry)
		s.lruList.Init()
		s.mu.Unlock()
	}
}

// Len returns the total number of items
func (c *ShardedLRUCache) Len() int {
	count := 0
	for _, s := range c.shards {
		s.mu.RLock()
		count += len(s.items)
		s.mu.RUnlock()
	}
	return count
}

// Stats returns cache statistics
func (c *ShardedLRUCache) Stats() CacheStats {
	var stats CacheStats
	for _, s := range c.shards {
		s.mu.RLock()
		stats.Hits += s.hits
		stats.Misses += s.misses
		stats.Evictions += s.evictions
		s.mu.RUnlock()
	}
	return stats
}

// removeEntry removes an entry from the shard
func (s *shard) removeEntry(e *entry) {
	s.lruList.Remove(e.listElem)
	delete(s.items, e.key)
}

// evictOldest removes the least recently used entry
func (s *shard) evictOldest() {
	elem := s.lruList.Back()
	if elem != nil {
		e := elem.Value.(*entry)
		s.removeEntry(e)
		s.evictions++
	}
}

// SimpleLRUCache is a non-sharded LRU cache (for comparison)
type SimpleLRUCache struct {
	mu       sync.RWMutex
	items    map[string]*entry
	lruList  *list.List
	maxSize  int
	hits     int64
	misses   int64
	evictions int64
}

// NewSimpleLRUCache creates a simple LRU cache
func NewSimpleLRUCache(maxSize int) *SimpleLRUCache {
	return &SimpleLRUCache{
		items:   make(map[string]*entry),
		lruList: list.New(),
		maxSize: maxSize,
	}
}

// Get retrieves a value
func (c *SimpleLRUCache) Get(key string) (interface{}, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	e, ok := c.items[key]
	if !ok {
		c.misses++
		return nil, false
	}

	if !e.expiresAt.IsZero() && time.Now().After(e.expiresAt) {
		c.removeEntry(e)
		c.misses++
		return nil, false
	}

	c.lruList.MoveToFront(e.listElem)
	c.hits++
	return e.value, true
}

// Set adds a value
func (c *SimpleLRUCache) Set(key string, value interface{}) {
	c.SetWithTTL(key, value, 0)
}

// SetWithTTL adds a value with TTL
func (c *SimpleLRUCache) SetWithTTL(key string, value interface{}, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()

	var expiresAt time.Time
	if ttl > 0 {
		expiresAt = time.Now().Add(ttl)
	}

	if e, ok := c.items[key]; ok {
		e.value = value
		e.expiresAt = expiresAt
		c.lruList.MoveToFront(e.listElem)
		return
	}

	e := &entry{
		key:       key,
		value:     value,
		expiresAt: expiresAt,
	}
	e.listElem = c.lruList.PushFront(e)
	c.items[key] = e

	if c.lruList.Len() > c.maxSize {
		c.evictOldest()
	}
}

// Delete removes a key
func (c *SimpleLRUCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if e, ok := c.items[key]; ok {
		c.removeEntry(e)
	}
}

// Clear removes all entries
func (c *SimpleLRUCache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.items = make(map[string]*entry)
	c.lruList.Init()
}

// Len returns count
func (c *SimpleLRUCache) Len() int {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return len(c.items)
}

// Stats returns statistics
func (c *SimpleLRUCache) Stats() CacheStats {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return CacheStats{
		Hits:   c.hits,
		Misses: c.misses,
		Evictions: c.evictions,
	}
}

func (c *SimpleLRUCache) removeEntry(e *entry) {
	c.lruList.Remove(e.listElem)
	delete(c.items, e.key)
}

func (c *SimpleLRUCache) evictOldest() {
	elem := c.lruList.Back()
	if elem != nil {
		e := elem.Value.(*entry)
		c.removeEntry(e)
		c.evictions++
	}
}
