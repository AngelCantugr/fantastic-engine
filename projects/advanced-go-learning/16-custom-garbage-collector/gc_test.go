package gc

import (
	"testing"
)

func TestMarkSweepGC(t *testing.T) {
	gc := NewGarbageCollector()

	// Create objects
	obj1 := gc.Allocate("obj1")
	obj2 := gc.Allocate("obj2")
	obj3 := gc.Allocate("obj3")

	// obj1 -> obj2
	gc.SetReference(obj1, obj2)

	// obj1 is root
	gc.AddRoot(obj1)

	// Before collection
	stats := gc.Stats()
	if stats["objects"].(int) != 3 {
		t.Errorf("Expected 3 objects, got %d", stats["objects"])
	}

	// Collect (obj3 should be collected)
	gc.Collect()

	stats = gc.Stats()
	if stats["objects"].(int) != 2 {
		t.Errorf("Expected 2 objects after GC, got %d", stats["objects"])
	}

	if stats["collected"].(uint64) != 1 {
		t.Errorf("Expected 1 collected, got %d", stats["collected"])
	}
}

func TestMarkSweepChain(t *testing.T) {
	gc := NewGarbageCollector()

	// Create chain: root -> obj1 -> obj2 -> obj3
	root := gc.Allocate("root")
	obj1 := gc.Allocate("obj1")
	obj2 := gc.Allocate("obj2")
	obj3 := gc.Allocate("obj3")

	gc.SetReference(root, obj1)
	gc.SetReference(obj1, obj2)
	gc.SetReference(obj2, obj3)

	gc.AddRoot(root)

	// Create unreachable object
	_ = gc.Allocate("unreachable")

	gc.Collect()

	stats := gc.Stats()
	if stats["objects"].(int) != 4 {
		t.Errorf("Expected 4 reachable objects, got %d", stats["objects"])
	}
}

func TestRefCountCollector(t *testing.T) {
	rc := NewRefCountCollector()

	obj := rc.Allocate("test")

	if obj.RefCount != 1 {
		t.Errorf("Expected initial refcount 1, got %d", obj.RefCount)
	}

	rc.Retain(obj)
	if obj.RefCount != 2 {
		t.Errorf("Expected refcount 2, got %d", obj.RefCount)
	}

	rc.Release(obj)
	if obj.RefCount != 1 {
		t.Errorf("Expected refcount 1, got %d", obj.RefCount)
	}

	rc.Release(obj)
	// Object should be collected (refcount = 0)
}

func TestRefCountCircularReference(t *testing.T) {
	rc := NewRefCountCollector()

	obj1 := rc.Allocate("obj1")
	obj2 := rc.Allocate("obj2")

	// Create circular reference
	obj1.References = append(obj1.References, obj2)
	obj2.References = append(obj2.References, obj1)

	rc.Retain(obj2)

	// This demonstrates the limitation of ref counting
	// Circular references won't be collected
	rc.Release(obj1)
	rc.Release(obj2)
}

func BenchmarkMarkSweep(b *testing.B) {
	gc := NewGarbageCollector()

	// Create some objects
	for i := 0; i < 100; i++ {
		obj := gc.Allocate(i)
		if i%10 == 0 {
			gc.AddRoot(obj)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		gc.Collect()
	}
}

func BenchmarkRefCount(b *testing.B) {
	rc := NewRefCountCollector()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		obj := rc.Allocate(i)
		rc.Release(obj)
	}
}
