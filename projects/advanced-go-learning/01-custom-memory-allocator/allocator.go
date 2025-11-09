package allocator

import (
	"fmt"
	"sync"
	"unsafe"
)

// Allocator is the interface for custom memory allocators
type Allocator interface {
	Alloc(size int) unsafe.Pointer
	Free(ptr unsafe.Pointer)
	Reset()
	Stats() AllocatorStats
}

// AllocatorStats tracks allocator metrics
type AllocatorStats struct {
	TotalAllocated   int
	TotalFreed       int
	CurrentAllocated int
	AllocationCount  int
	FreeCount        int
}

// PoolAllocator uses sync.Pool for object reuse
type PoolAllocator[T any] struct {
	pool  *sync.Pool
	stats AllocatorStats
	mu    sync.Mutex
}

// NewPoolAllocator creates a new pool-based allocator
func NewPoolAllocator[T any](factory func() *T) *PoolAllocator[T] {
	return &PoolAllocator[T]{
		pool: &sync.Pool{
			New: func() interface{} {
				return factory()
			},
		},
	}
}

// Get retrieves an object from the pool
func (p *PoolAllocator[T]) Get() *T {
	p.mu.Lock()
	p.stats.AllocationCount++
	p.mu.Unlock()

	return p.pool.Get().(*T)
}

// Put returns an object to the pool
func (p *PoolAllocator[T]) Put(obj *T) {
	p.mu.Lock()
	p.stats.FreeCount++
	p.mu.Unlock()

	p.pool.Put(obj)
}

// Stats returns allocator statistics
func (p *PoolAllocator[T]) Stats() AllocatorStats {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.stats
}

// ArenaAllocator implements bump-pointer allocation
type ArenaAllocator struct {
	buffer []byte
	offset int
	mu     sync.Mutex
	stats  AllocatorStats
}

// NewArenaAllocator creates a new arena allocator with the given size
func NewArenaAllocator(size int) *ArenaAllocator {
	return &ArenaAllocator{
		buffer: make([]byte, size),
		offset: 0,
	}
}

// Alloc allocates memory from the arena
func (a *ArenaAllocator) Alloc(size int) unsafe.Pointer {
	a.mu.Lock()
	defer a.mu.Unlock()

	// Align to 8-byte boundary
	aligned := (size + 7) &^ 7

	if a.offset+aligned > len(a.buffer) {
		return nil // Arena exhausted
	}

	ptr := unsafe.Pointer(&a.buffer[a.offset])
	a.offset += aligned

	a.stats.TotalAllocated += aligned
	a.stats.CurrentAllocated += aligned
	a.stats.AllocationCount++

	return ptr
}

// Free is a no-op for arena allocators (use Reset instead)
func (a *ArenaAllocator) Free(ptr unsafe.Pointer) {
	// Arena allocators don't support individual frees
	// All memory is freed at once with Reset()
}

// Reset clears the arena for reuse
func (a *ArenaAllocator) Reset() {
	a.mu.Lock()
	defer a.mu.Unlock()

	a.stats.TotalFreed += a.offset
	a.stats.CurrentAllocated = 0
	a.offset = 0
}

// Stats returns allocator statistics
func (a *ArenaAllocator) Stats() AllocatorStats {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.stats
}

// Remaining returns the number of bytes remaining in the arena
func (a *ArenaAllocator) Remaining() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return len(a.buffer) - a.offset
}

// SlabAllocator implements fixed-size slab allocation
type SlabAllocator struct {
	slabs     map[int]*Slab
	mu        sync.RWMutex
	stats     AllocatorStats
	sizeClass []int // Size classes (e.g., 16, 32, 64, 128, 256, 512, 1024)
}

// Slab represents a single size class
type Slab struct {
	size      int
	blocks    []unsafe.Pointer
	freeList  []unsafe.Pointer
	allocated int
	mu        sync.Mutex
}

// NewSlabAllocator creates a new slab allocator
func NewSlabAllocator(sizeClasses []int, blocksPerSlab int) *SlabAllocator {
	sa := &SlabAllocator{
		slabs:     make(map[int]*Slab),
		sizeClass: sizeClasses,
	}

	for _, size := range sizeClasses {
		sa.slabs[size] = newSlab(size, blocksPerSlab)
	}

	return sa
}

// newSlab creates a new slab with the given size and number of blocks
func newSlab(size, count int) *Slab {
	s := &Slab{
		size:     size,
		blocks:   make([]unsafe.Pointer, count),
		freeList: make([]unsafe.Pointer, 0, count),
	}

	// Pre-allocate all blocks
	for i := 0; i < count; i++ {
		block := make([]byte, size)
		ptr := unsafe.Pointer(&block[0])
		s.blocks[i] = ptr
		s.freeList = append(s.freeList, ptr)
	}

	return s
}

// findSizeClass finds the appropriate size class for the requested size
func (sa *SlabAllocator) findSizeClass(size int) int {
	for _, sc := range sa.sizeClass {
		if sc >= size {
			return sc
		}
	}
	// Return largest size class if requested size is too large
	return sa.sizeClass[len(sa.sizeClass)-1]
}

// Alloc allocates memory from the slab
func (sa *SlabAllocator) Alloc(size int) unsafe.Pointer {
	sizeClass := sa.findSizeClass(size)

	sa.mu.RLock()
	slab, ok := sa.slabs[sizeClass]
	sa.mu.RUnlock()

	if !ok {
		return nil
	}

	slab.mu.Lock()
	defer slab.mu.Unlock()

	if len(slab.freeList) == 0 {
		return nil // No free blocks in this slab
	}

	// Pop from free list
	ptr := slab.freeList[len(slab.freeList)-1]
	slab.freeList = slab.freeList[:len(slab.freeList)-1]
	slab.allocated++

	sa.mu.Lock()
	sa.stats.TotalAllocated += sizeClass
	sa.stats.CurrentAllocated += sizeClass
	sa.stats.AllocationCount++
	sa.mu.Unlock()

	return ptr
}

// Free returns memory to the slab
func (sa *SlabAllocator) Free(ptr unsafe.Pointer) {
	sa.mu.RLock()
	defer sa.mu.RUnlock()

	// Find which slab this pointer belongs to
	for _, slab := range sa.slabs {
		slab.mu.Lock()
		// Check if pointer belongs to this slab
		belongs := false
		for _, block := range slab.blocks {
			if block == ptr {
				belongs = true
				break
			}
		}

		if belongs {
			slab.freeList = append(slab.freeList, ptr)
			slab.allocated--

			sa.mu.Lock()
			sa.stats.TotalFreed += slab.size
			sa.stats.CurrentAllocated -= slab.size
			sa.stats.FreeCount++
			sa.mu.Unlock()

			slab.mu.Unlock()
			return
		}
		slab.mu.Unlock()
	}
}

// Reset clears all slabs
func (sa *SlabAllocator) Reset() {
	sa.mu.Lock()
	defer sa.mu.Unlock()

	for _, slab := range sa.slabs {
		slab.mu.Lock()
		slab.freeList = slab.freeList[:0]
		for _, block := range slab.blocks {
			slab.freeList = append(slab.freeList, block)
		}
		slab.allocated = 0
		slab.mu.Unlock()
	}

	sa.stats.TotalFreed += sa.stats.CurrentAllocated
	sa.stats.CurrentAllocated = 0
}

// Stats returns allocator statistics
func (sa *SlabAllocator) Stats() AllocatorStats {
	sa.mu.RLock()
	defer sa.mu.RUnlock()
	return sa.stats
}

// PrintStats prints detailed statistics
func (sa *SlabAllocator) PrintStats() {
	sa.mu.RLock()
	defer sa.mu.RUnlock()

	fmt.Printf("Slab Allocator Statistics:\n")
	fmt.Printf("  Total Allocated: %d bytes\n", sa.stats.TotalAllocated)
	fmt.Printf("  Total Freed: %d bytes\n", sa.stats.TotalFreed)
	fmt.Printf("  Current Allocated: %d bytes\n", sa.stats.CurrentAllocated)
	fmt.Printf("  Allocation Count: %d\n", sa.stats.AllocationCount)
	fmt.Printf("  Free Count: %d\n", sa.stats.FreeCount)

	fmt.Printf("\nSlab Details:\n")
	for size, slab := range sa.slabs {
		slab.mu.Lock()
		fmt.Printf("  Size %d: %d/%d blocks allocated\n",
			size, slab.allocated, len(slab.blocks))
		slab.mu.Unlock()
	}
}
