package main

import (
	"fmt"
	"runtime"
	"strings"
	"time"
	"unsafe"

	allocator "github.com/AngelCantugr/advanced-go-learning/01-custom-memory-allocator"
)

// LogEntry represents a log entry
type LogEntry struct {
	Timestamp time.Time
	Level     string
	Message   string
	Fields    map[string]interface{}
}

// Reset clears the log entry for reuse
func (l *LogEntry) Reset() {
	l.Timestamp = time.Time{}
	l.Level = ""
	l.Message = ""
	for k := range l.Fields {
		delete(l.Fields, k)
	}
}

func main() {
	fmt.Println("🚀 Custom Memory Allocator Examples\n")

	// Example 1: Pool Allocator for Log Entries
	fmt.Println("Example 1: Pool Allocator for High-Throughput Logging")
	fmt.Println(strings.Repeat("=", 60))
	poolExample()

	fmt.Println()

	// Example 2: Arena Allocator for Frame Processing
	fmt.Println("Example 2: Arena Allocator for Frame-Based Processing")
	fmt.Println(strings.Repeat("=", 60))
	arenaExample()

	fmt.Println()

	// Example 3: Slab Allocator for Mixed Sizes
	fmt.Println("Example 3: Slab Allocator for Network Packets")
	fmt.Println(strings.Repeat("=", 60))
	slabExample()

	fmt.Println()

	// Example 4: Performance Comparison
	fmt.Println("Example 4: Performance Comparison")
	fmt.Println(strings.Repeat("=", 60))
	performanceComparison()
}

func poolExample() {
	// Create pool for log entries
	logPool := allocator.NewPoolAllocator(func() *LogEntry {
		return &LogEntry{
			Fields: make(map[string]interface{}, 8),
		}
	})

	// Simulate high-throughput logging
	const iterations = 100000

	start := time.Now()
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)

	for i := 0; i < iterations; i++ {
		entry := logPool.Get()
		entry.Timestamp = time.Now()
		entry.Level = "INFO"
		entry.Message = "Processing request"
		entry.Fields["request_id"] = i
		entry.Fields["user_id"] = i % 1000

		// Simulate using the entry
		_ = entry

		// Return to pool
		entry.Reset()
		logPool.Put(entry)
	}

	duration := time.Since(start)
	var memAfter runtime.MemStats
	runtime.ReadMemStats(&memAfter)

	stats := logPool.Stats()
	fmt.Printf("Processed %d log entries in %v\n", iterations, duration)
	fmt.Printf("Allocations: %d\n", stats.AllocationCount)
	fmt.Printf("Returns: %d\n", stats.FreeCount)
	fmt.Printf("Total Allocs: %d\n", memAfter.TotalAlloc-memBefore.TotalAlloc)
	fmt.Printf("Heap Objects: %d\n", memAfter.HeapObjects-memBefore.HeapObjects)
	fmt.Printf("Throughput: %.2f ops/sec\n", float64(iterations)/duration.Seconds())
}

func arenaExample() {
	// Simulate frame-based processing (like a game or animation)
	const frameCount = 1000
	const entitiesPerFrame = 100
	const entitySize = 128

	// Create arena large enough for one frame
	arenaSize := entitiesPerFrame * entitySize * 2 // 2x buffer
	arena := allocator.NewArenaAllocator(arenaSize)

	start := time.Now()
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)

	for frame := 0; frame < frameCount; frame++ {
		// Allocate entities for this frame
		for i := 0; i < entitiesPerFrame; i++ {
			entity := arena.Alloc(entitySize)
			if entity == nil {
				fmt.Printf("Arena exhausted at frame %d, entity %d\n", frame, i)
				break
			}
			// Simulate using the entity
			_ = entity
		}

		// Reset arena for next frame
		arena.Reset()
	}

	duration := time.Since(start)
	var memAfter runtime.MemStats
	runtime.ReadMemStats(&memAfter)

	stats := arena.Stats()
	totalEntities := frameCount * entitiesPerFrame

	fmt.Printf("Processed %d frames (%d entities) in %v\n", frameCount, totalEntities, duration)
	fmt.Printf("Allocations: %d\n", stats.AllocationCount)
	fmt.Printf("Total Allocated: %d bytes\n", stats.TotalAllocated)
	fmt.Printf("Total Freed: %d bytes\n", stats.TotalFreed)
	fmt.Printf("Heap Allocs: %d\n", memAfter.TotalAlloc-memBefore.TotalAlloc)
	fmt.Printf("Frame Time: %v\n", duration/time.Duration(frameCount))
	fmt.Printf("FPS: %.2f\n", float64(frameCount)/duration.Seconds())
}

func slabExample() {
	// Simulate network packet processing with different packet sizes
	sizeClasses := []int{64, 128, 256, 512, 1024}
	blocksPerClass := 1000
	slab := allocator.NewSlabAllocator(sizeClasses, blocksPerClass)

	// Simulate different packet sizes
	packetSizes := []int{50, 100, 200, 450, 900}
	packetsPerSize := 1000

	start := time.Now()
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)

	for _, size := range packetSizes {
		for i := 0; i < packetsPerSize; i++ {
			packet := slab.Alloc(size)
			if packet == nil {
				fmt.Printf("Slab exhausted for size %d at iteration %d\n", size, i)
				break
			}
			// Simulate processing packet
			_ = packet

			// Free packet after processing
			slab.Free(packet)
		}
	}

	duration := time.Since(start)
	var memAfter runtime.MemStats
	runtime.ReadMemStats(&memAfter)

	totalPackets := len(packetSizes) * packetsPerSize
	fmt.Printf("Processed %d packets in %v\n", totalPackets, duration)
	slab.PrintStats()
	fmt.Printf("Heap Allocs: %d bytes\n", memAfter.TotalAlloc-memBefore.TotalAlloc)
	fmt.Printf("Throughput: %.2f packets/sec\n", float64(totalPackets)/duration.Seconds())
}

func performanceComparison() {
	const iterations = 10000

	// Standard allocation
	fmt.Println("\n1. Standard Allocation:")
	start := time.Now()
	var memBefore runtime.MemStats
	runtime.ReadMemStats(&memBefore)

	for i := 0; i < iterations; i++ {
		data := make([]byte, 128)
		_ = data
	}

	standardDuration := time.Since(start)
	var memStandard runtime.MemStats
	runtime.ReadMemStats(&memStandard)
	standardAllocs := memStandard.TotalAlloc - memBefore.TotalAlloc

	fmt.Printf("   Time: %v\n", standardDuration)
	fmt.Printf("   Allocs: %d bytes\n", standardAllocs)

	// Pool allocation
	fmt.Println("\n2. Pool Allocation:")
	type Buffer struct {
		Data [128]byte
	}
	pool := allocator.NewPoolAllocator(func() *Buffer {
		return &Buffer{}
	})

	runtime.ReadMemStats(&memBefore)
	start = time.Now()

	for i := 0; i < iterations; i++ {
		buf := pool.Get()
		pool.Put(buf)
	}

	poolDuration := time.Since(start)
	var memPool runtime.MemStats
	runtime.ReadMemStats(&memPool)
	poolAllocs := memPool.TotalAlloc - memBefore.TotalAlloc

	fmt.Printf("   Time: %v (%.2fx faster)\n", poolDuration, float64(standardDuration)/float64(poolDuration))
	fmt.Printf("   Allocs: %d bytes (%.2fx reduction)\n", poolAllocs, float64(standardAllocs)/float64(poolAllocs))

	// Arena allocation
	fmt.Println("\n3. Arena Allocation:")
	arena := allocator.NewArenaAllocator(iterations * 128 * 2)

	runtime.ReadMemStats(&memBefore)
	start = time.Now()

	for i := 0; i < iterations; i++ {
		ptr := arena.Alloc(128)
		_ = ptr
	}

	arenaDuration := time.Since(start)
	var memArena runtime.MemStats
	runtime.ReadMemStats(&memArena)
	arenaAllocs := memArena.TotalAlloc - memBefore.TotalAlloc

	fmt.Printf("   Time: %v (%.2fx faster)\n", arenaDuration, float64(standardDuration)/float64(arenaDuration))
	fmt.Printf("   Allocs: %d bytes (%.2fx reduction)\n", arenaAllocs, float64(standardAllocs)/float64(max(arenaAllocs, 1)))

	// Slab allocation
	fmt.Println("\n4. Slab Allocation:")
	slab := allocator.NewSlabAllocator([]int{128}, iterations)

	runtime.ReadMemStats(&memBefore)
	start = time.Now()

	ptrs := make([]unsafe.Pointer, 0, 100)
	for i := 0; i < iterations; i++ {
		ptr := slab.Alloc(128)
		ptrs = append(ptrs, ptr)

		if len(ptrs) >= 100 {
			for _, p := range ptrs {
				slab.Free(p)
			}
			ptrs = ptrs[:0]
		}
	}

	slabDuration := time.Since(start)
	var memSlab runtime.MemStats
	runtime.ReadMemStats(&memSlab)
	slabAllocs := memSlab.TotalAlloc - memBefore.TotalAlloc

	fmt.Printf("   Time: %v (%.2fx faster)\n", slabDuration, float64(standardDuration)/float64(slabDuration))
	fmt.Printf("   Allocs: %d bytes (%.2fx reduction)\n", slabAllocs, float64(standardAllocs)/float64(max(slabAllocs, 1)))

	// Summary
	fmt.Println("\n📊 Summary:")
	fmt.Println("   Best for reusable objects: Pool")
	fmt.Println("   Best for bulk same-lifetime: Arena")
	fmt.Println("   Best for mixed sizes: Slab")
	fmt.Println("   Most flexible: Standard (but slowest)")
}

func max(a, b uint64) uint64 {
	if a > b {
		return a
	}
	return b
}
