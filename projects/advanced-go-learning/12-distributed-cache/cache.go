package cache

import (
	"container/list"
	"hash/fnv"
	"sort"
	"sync"
	"time"
)

type entry struct {
	key       string
	value     interface{}
	expiresAt time.Time
}

// LRUCache implements LRU cache with TTL
type LRUCache struct {
	capacity int
	items    map[string]*list.Element
	eviction *list.List
	mu       sync.RWMutex
}

func NewLRUCache(capacity int) *LRUCache {
	c := &LRUCache{
		capacity: capacity,
		items:    make(map[string]*list.Element),
		eviction: list.New(),
	}
	go c.cleanup()
	return c
}

func (c *LRUCache) Get(key string) (interface{}, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()

	elem, ok := c.items[key]
	if !ok {
		return nil, false
	}

	ent := elem.Value.(*entry)
	if time.Now().After(ent.expiresAt) {
		c.removeElement(elem)
		return nil, false
	}

	c.eviction.MoveToFront(elem)
	return ent.value, true
}

func (c *LRUCache) Set(key string, value interface{}, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if elem, ok := c.items[key]; ok {
		c.eviction.MoveToFront(elem)
		ent := elem.Value.(*entry)
		ent.value = value
		ent.expiresAt = time.Now().Add(ttl)
		return
	}

	if c.eviction.Len() >= c.capacity {
		c.removeOldest()
	}

	ent := &entry{
		key:       key,
		value:     value,
		expiresAt: time.Now().Add(ttl),
	}

	elem := c.eviction.PushFront(ent)
	c.items[key] = elem
}

func (c *LRUCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if elem, ok := c.items[key]; ok {
		c.removeElement(elem)
	}
}

func (c *LRUCache) removeOldest() {
	elem := c.eviction.Back()
	if elem != nil {
		c.removeElement(elem)
	}
}

func (c *LRUCache) removeElement(elem *list.Element) {
	c.eviction.Remove(elem)
	ent := elem.Value.(*entry)
	delete(c.items, ent.key)
}

func (c *LRUCache) cleanup() {
	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		c.mu.Lock()
		now := time.Now()
		var toRemove []*list.Element

		for elem := c.eviction.Back(); elem != nil; elem = elem.Prev() {
			ent := elem.Value.(*entry)
			if now.After(ent.expiresAt) {
				toRemove = append(toRemove, elem)
			}
		}

		for _, elem := range toRemove {
			c.removeElement(elem)
		}
		c.mu.Unlock()
	}
}

// ConsistentHash implements consistent hashing
type ConsistentHash struct {
	ring     map[uint32]string
	keys     []uint32
	replicas int
	mu       sync.RWMutex
}

func NewConsistentHash(replicas int) *ConsistentHash {
	return &ConsistentHash{
		ring:     make(map[uint32]string),
		replicas: replicas,
	}
}

func (ch *ConsistentHash) AddNode(node string) {
	ch.mu.Lock()
	defer ch.mu.Unlock()

	for i := 0; i < ch.replicas; i++ {
		key := ch.hash(node + string(rune(i)))
		ch.ring[key] = node
		ch.keys = append(ch.keys, key)
	}

	sort.Slice(ch.keys, func(i, j int) bool {
		return ch.keys[i] < ch.keys[j]
	})
}

func (ch *ConsistentHash) RemoveNode(node string) {
	ch.mu.Lock()
	defer ch.mu.Unlock()

	for i := 0; i < ch.replicas; i++ {
		key := ch.hash(node + string(rune(i)))
		delete(ch.ring, key)
	}

	newKeys := make([]uint32, 0)
	for _, k := range ch.keys {
		if _, ok := ch.ring[k]; ok {
			newKeys = append(newKeys, k)
		}
	}
	ch.keys = newKeys
}

func (ch *ConsistentHash) GetNode(key string) string {
	ch.mu.RLock()
	defer ch.mu.RUnlock()

	if len(ch.keys) == 0 {
		return ""
	}

	hash := ch.hash(key)
	idx := sort.Search(len(ch.keys), func(i int) bool {
		return ch.keys[i] >= hash
	})

	if idx == len(ch.keys) {
		idx = 0
	}

	return ch.ring[ch.keys[idx]]
}

func (ch *ConsistentHash) hash(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

// DistributedCache combines LRU cache with consistent hashing
type DistributedCache struct {
	caches map[string]*LRUCache
	hash   *ConsistentHash
	mu     sync.RWMutex
}

func NewDistributedCache(nodes []string, cacheSize int) *DistributedCache {
	dc := &DistributedCache{
		caches: make(map[string]*LRUCache),
		hash:   NewConsistentHash(150),
	}

	for _, node := range nodes {
		dc.caches[node] = NewLRUCache(cacheSize)
		dc.hash.AddNode(node)
	}

	return dc
}

func (dc *DistributedCache) Get(key string) (interface{}, bool) {
	node := dc.hash.GetNode(key)
	if node == "" {
		return nil, false
	}

	dc.mu.RLock()
	cache, ok := dc.caches[node]
	dc.mu.RUnlock()

	if !ok {
		return nil, false
	}

	return cache.Get(key)
}

func (dc *DistributedCache) Set(key string, value interface{}, ttl time.Duration) {
	node := dc.hash.GetNode(key)
	if node == "" {
		return
	}

	dc.mu.RLock()
	cache, ok := dc.caches[node]
	dc.mu.RUnlock()

	if ok {
		cache.Set(key, value, ttl)
	}
}

func (dc *DistributedCache) Delete(key string) {
	node := dc.hash.GetNode(key)
	if node == "" {
		return
	}

	dc.mu.RLock()
	cache, ok := dc.caches[node]
	dc.mu.RUnlock()

	if ok {
		cache.Delete(key)
	}
}
