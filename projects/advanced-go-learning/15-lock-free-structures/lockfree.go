package lockfree

import (
	"sync/atomic"
	"unsafe"
)

// LockFreeStack implements a lock-free stack using CAS
type LockFreeStack[T any] struct {
	head unsafe.Pointer
}

type stackNode[T any] struct {
	value T
	next  unsafe.Pointer
}

func NewLockFreeStack[T any]() *LockFreeStack[T] {
	return &LockFreeStack[T]{}
}

func (s *LockFreeStack[T]) Push(value T) {
	node := &stackNode[T]{
		value: value,
	}

	for {
		old := atomic.LoadPointer(&s.head)
		node.next = old

		if atomic.CompareAndSwapPointer(&s.head, old, unsafe.Pointer(node)) {
			return
		}
	}
}

func (s *LockFreeStack[T]) Pop() (T, bool) {
	var zero T

	for {
		old := atomic.LoadPointer(&s.head)
		if old == nil {
			return zero, false
		}

		node := (*stackNode[T])(old)
		next := atomic.LoadPointer(&node.next)

		if atomic.CompareAndSwapPointer(&s.head, old, next) {
			return node.value, true
		}
	}
}

// LockFreeQueue implements a lock-free FIFO queue
type LockFreeQueue[T any] struct {
	head unsafe.Pointer
	tail unsafe.Pointer
}

type queueNode[T any] struct {
	value T
	next  unsafe.Pointer
}

func NewLockFreeQueue[T any]() *LockFreeQueue[T] {
	dummy := &queueNode[T]{}
	ptr := unsafe.Pointer(dummy)

	return &LockFreeQueue[T]{
		head: ptr,
		tail: ptr,
	}
}

func (q *LockFreeQueue[T]) Enqueue(value T) {
	node := &queueNode[T]{
		value: value,
	}

	for {
		tail := atomic.LoadPointer(&q.tail)
		tailNode := (*queueNode[T])(tail)
		next := atomic.LoadPointer(&tailNode.next)

		if tail == atomic.LoadPointer(&q.tail) {
			if next == nil {
				if atomic.CompareAndSwapPointer(&tailNode.next, nil, unsafe.Pointer(node)) {
					atomic.CompareAndSwapPointer(&q.tail, tail, unsafe.Pointer(node))
					return
				}
			} else {
				atomic.CompareAndSwapPointer(&q.tail, tail, next)
			}
		}
	}
}

func (q *LockFreeQueue[T]) Dequeue() (T, bool) {
	var zero T

	for {
		head := atomic.LoadPointer(&q.head)
		tail := atomic.LoadPointer(&q.tail)
		headNode := (*queueNode[T])(head)
		next := atomic.LoadPointer(&headNode.next)

		if head == atomic.LoadPointer(&q.head) {
			if head == tail {
				if next == nil {
					return zero, false
				}
				atomic.CompareAndSwapPointer(&q.tail, tail, next)
			} else {
				nextNode := (*queueNode[T])(next)
				value := nextNode.value

				if atomic.CompareAndSwapPointer(&q.head, head, next) {
					return value, true
				}
			}
		}
	}
}

// LockFreeCounter implements a lock-free counter
type LockFreeCounter struct {
	value uint64
}

func NewLockFreeCounter() *LockFreeCounter {
	return &LockFreeCounter{}
}

func (c *LockFreeCounter) Increment() uint64 {
	return atomic.AddUint64(&c.value, 1)
}

func (c *LockFreeCounter) Decrement() uint64 {
	return atomic.AddUint64(&c.value, ^uint64(0))
}

func (c *LockFreeCounter) Get() uint64 {
	return atomic.LoadUint64(&c.value)
}

func (c *LockFreeCounter) Set(value uint64) {
	atomic.StoreUint64(&c.value, value)
}

func (c *LockFreeCounter) CompareAndSwap(old, new uint64) bool {
	return atomic.CompareAndSwapUint64(&c.value, old, new)
}

// LockFreeMap implements a simple lock-free map using sharding
type LockFreeMap[K comparable, V any] struct {
	shards []*mapShard[K, V]
	mask   uint64
}

type mapShard[K comparable, V any] struct {
	data map[K]V
	mu   atomic.Value
}

func NewLockFreeMap[K comparable, V any](shardCount int) *LockFreeMap[K, V] {
	m := &LockFreeMap[K, V]{
		shards: make([]*mapShard[K, V], shardCount),
		mask:   uint64(shardCount - 1),
	}

	for i := 0; i < shardCount; i++ {
		m.shards[i] = &mapShard[K, V]{
			data: make(map[K]V),
		}
	}

	return m
}

func (m *LockFreeMap[K, V]) getShard(key K) *mapShard[K, V] {
	h := hash(key)
	return m.shards[h&m.mask]
}

func (m *LockFreeMap[K, V]) Get(key K) (V, bool) {
	shard := m.getShard(key)
	// In real implementation, would use RCU or similar
	val, ok := shard.data[key]
	return val, ok
}

func (m *LockFreeMap[K, V]) Set(key K, value V) {
	shard := m.getShard(key)
	shard.data[key] = value
}

func hash[K comparable](key K) uint64 {
	// Simple hash function
	return uint64(0) // Simplified for example
}
