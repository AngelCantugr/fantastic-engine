package allocator

import (
	"sync"
	"testing"
	"unsafe"
)

// Test object for pool allocator
type TestObject struct {
	ID   int
	Data [64]byte
}

func TestPoolAllocator(t *testing.T) {
	pool := NewPoolAllocator(func() *TestObject {
		return &TestObject{}
	})

	// Get an object
	obj1 := pool.Get()
	if obj1 == nil {
		t.Fatal("Expected non-nil object")
	}

	obj1.ID = 42

	// Put it back
	pool.Put(obj1)

	// Get another object (might be the same one)
	obj2 := pool.Get()
	if obj2 == nil {
		t.Fatal("Expected non-nil object")
	}

	// Stats should show allocations
	stats := pool.Stats()
	if stats.AllocationCount != 2 {
		t.Errorf("Expected 2 allocations, got %d", stats.AllocationCount)
	}
	if stats.FreeCount != 1 {
		t.Errorf("Expected 1 free, got %d", stats.FreeCount)
	}
}

func TestPoolAllocatorConcurrent(t *testing.T) {
	pool := NewPoolAllocator(func() *TestObject {
		return &TestObject{}
	})

	const goroutines = 100
	const iterations = 1000

	var wg sync.WaitGroup
	wg.Add(goroutines)

	for i := 0; i < goroutines; i++ {
		go func(id int) {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				obj := pool.Get()
				obj.ID = id
				pool.Put(obj)
			}
		}(i)
	}

	wg.Wait()

	stats := pool.Stats()
	expected := goroutines * iterations
	if stats.AllocationCount != expected {
		t.Errorf("Expected %d allocations, got %d", expected, stats.AllocationCount)
	}
}

func TestArenaAllocator(t *testing.T) {
	arena := NewArenaAllocator(1024)

	// Allocate some memory
	ptr1 := arena.Alloc(64)
	if ptr1 == nil {
		t.Fatal("Expected non-nil pointer")
	}

	ptr2 := arena.Alloc(128)
	if ptr2 == nil {
		t.Fatal("Expected non-nil pointer")
	}

	// Check stats
	stats := arena.Stats()
	if stats.AllocationCount != 2 {
		t.Errorf("Expected 2 allocations, got %d", stats.AllocationCount)
	}

	// Allocate too much (should fail)
	ptr3 := arena.Alloc(2048)
	if ptr3 != nil {
		t.Error("Expected nil pointer for oversized allocation")
	}

	// Reset and allocate again
	arena.Reset()
	ptr4 := arena.Alloc(64)
	if ptr4 == nil {
		t.Fatal("Expected non-nil pointer after reset")
	}

	stats = arena.Stats()
	if stats.CurrentAllocated == 0 {
		t.Error("Expected non-zero current allocation after reset")
	}
}

func TestArenaAlignment(t *testing.T) {
	arena := NewArenaAllocator(1024)

	// Allocate various sizes and check alignment
	sizes := []int{1, 7, 15, 31, 63}
	for _, size := range sizes {
		ptr := arena.Alloc(size)
		if ptr == nil {
			t.Fatalf("Failed to allocate %d bytes", size)
		}

		// Check 8-byte alignment
		addr := uintptr(ptr)
		if addr%8 != 0 {
			t.Errorf("Pointer %p not 8-byte aligned for size %d", ptr, size)
		}
	}
}

func TestSlabAllocator(t *testing.T) {
	sizeClasses := []int{16, 32, 64, 128, 256}
	slab := NewSlabAllocator(sizeClasses, 10)

	// Allocate from different size classes
	ptr1 := slab.Alloc(20) // Should use 32-byte class
	if ptr1 == nil {
		t.Fatal("Expected non-nil pointer")
	}

	ptr2 := slab.Alloc(100) // Should use 128-byte class
	if ptr2 == nil {
		t.Fatal("Expected non-nil pointer")
	}

	// Free and reallocate
	slab.Free(ptr1)
	ptr3 := slab.Alloc(25) // Should reuse freed block
	if ptr3 == nil {
		t.Fatal("Expected non-nil pointer")
	}

	stats := slab.Stats()
	if stats.AllocationCount != 3 {
		t.Errorf("Expected 3 allocations, got %d", stats.AllocationCount)
	}
	if stats.FreeCount != 1 {
		t.Errorf("Expected 1 free, got %d", stats.FreeCount)
	}
}

func TestSlabExhaustion(t *testing.T) {
	sizeClasses := []int{64}
	slab := NewSlabAllocator(sizeClasses, 5) // Only 5 blocks

	// Allocate all blocks
	ptrs := make([]unsafe.Pointer, 5)
	for i := 0; i < 5; i++ {
		ptrs[i] = slab.Alloc(64)
		if ptrs[i] == nil {
			t.Fatalf("Failed to allocate block %d", i)
		}
	}

	// Try to allocate one more (should fail)
	ptr := slab.Alloc(64)
	if ptr != nil {
		t.Error("Expected nil pointer when slab exhausted")
	}

	// Free one and try again
	slab.Free(ptrs[0])
	ptr = slab.Alloc(64)
	if ptr == nil {
		t.Error("Expected non-nil pointer after freeing")
	}
}

// Benchmarks

func BenchmarkStandardAlloc(b *testing.B) {
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		obj := &TestObject{ID: i}
		_ = obj
	}
}

func BenchmarkPoolAlloc(b *testing.B) {
	pool := NewPoolAllocator(func() *TestObject {
		return &TestObject{}
	})

	b.ReportAllocs()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		obj := pool.Get()
		obj.ID = i
		pool.Put(obj)
	}
}

func BenchmarkArenaAlloc(b *testing.B) {
	// Use large arena to avoid exhaustion
	arena := NewArenaAllocator(b.N * 72) // 72 bytes aligned size

	b.ReportAllocs()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		ptr := arena.Alloc(64)
		_ = ptr
	}
}

func BenchmarkSlabAlloc(b *testing.B) {
	sizeClasses := []int{64}
	slab := NewSlabAllocator(sizeClasses, b.N)

	b.ReportAllocs()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		ptr := slab.Alloc(64)
		_ = ptr
	}
}

func BenchmarkPoolAllocParallel(b *testing.B) {
	pool := NewPoolAllocator(func() *TestObject {
		return &TestObject{}
	})

	b.ReportAllocs()
	b.ResetTimer()

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			obj := pool.Get()
			pool.Put(obj)
		}
	})
}

func BenchmarkSlabAllocParallel(b *testing.B) {
	sizeClasses := []int{64}
	slab := NewSlabAllocator(sizeClasses, 1000000)

	b.ReportAllocs()
	b.ResetTimer()

	b.RunParallel(func(pb *testing.PB) {
		allocated := make([]unsafe.Pointer, 0, 100)
		for pb.Next() {
			ptr := slab.Alloc(64)
			allocated = append(allocated, ptr)

			if len(allocated) >= 100 {
				for _, p := range allocated {
					slab.Free(p)
				}
				allocated = allocated[:0]
			}
		}
	})
}

// Memory allocation comparison
func BenchmarkComparison(b *testing.B) {
	b.Run("Standard", func(b *testing.B) {
		b.ReportAllocs()
		for i := 0; i < b.N; i++ {
			data := make([]byte, 64)
			_ = data
		}
	})

	b.Run("Pool", func(b *testing.B) {
		pool := sync.Pool{
			New: func() interface{} {
				return make([]byte, 64)
			},
		}
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			data := pool.Get().([]byte)
			pool.Put(data)
		}
	})

	b.Run("Arena", func(b *testing.B) {
		arena := NewArenaAllocator(b.N * 72)
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			ptr := arena.Alloc(64)
			_ = ptr
		}
	})

	b.Run("Slab", func(b *testing.B) {
		slab := NewSlabAllocator([]int{64}, b.N)
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			ptr := slab.Alloc(64)
			_ = ptr
		}
	})
}
