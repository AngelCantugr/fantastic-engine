package gc

import (
	"runtime"
	"sync"
	"sync/atomic"
)

// Color represents the tri-color marking state
type Color int

const (
	White Color = iota // Not visited
	Gray               // Visited but not scanned
	Black              // Visited and scanned
)

// Object represents a heap-allocated object
type Object struct {
	ID        uint64
	Data      interface{}
	Color     Color
	RefCount  int32
	References []*Object
}

// GarbageCollector implements a simple mark-sweep collector
type GarbageCollector struct {
	objects    map[uint64]*Object
	roots      []*Object
	mu         sync.RWMutex
	nextID     uint64

	// Metrics
	collections uint64
	collected   uint64
}

func NewGarbageCollector() *GarbageCollector {
	return &GarbageCollector{
		objects: make(map[uint64]*Object),
		roots:   make([]*Object, 0),
	}
}

// Allocate creates a new object
func (gc *GarbageCollector) Allocate(data interface{}) *Object {
	gc.mu.Lock()
	defer gc.mu.Unlock()

	obj := &Object{
		ID:         atomic.AddUint64(&gc.nextID, 1),
		Data:       data,
		Color:      White,
		References: make([]*Object, 0),
	}

	gc.objects[obj.ID] = obj
	return obj
}

// AddRoot adds an object as a GC root
func (gc *GarbageCollector) AddRoot(obj *Object) {
	gc.mu.Lock()
	defer gc.mu.Unlock()
	gc.roots = append(gc.roots, obj)
}

// RemoveRoot removes an object from GC roots
func (gc *GarbageCollector) RemoveRoot(obj *Object) {
	gc.mu.Lock()
	defer gc.mu.Unlock()

	for i, root := range gc.roots {
		if root.ID == obj.ID {
			gc.roots = append(gc.roots[:i], gc.roots[i+1:]...)
			break
		}
	}
}

// SetReference creates a reference from one object to another
func (gc *GarbageCollector) SetReference(from, to *Object) {
	from.References = append(from.References, to)
	atomic.AddInt32(&to.RefCount, 1)
}

// Collect runs the mark-sweep garbage collection
func (gc *GarbageCollector) Collect() {
	gc.mu.Lock()
	defer gc.mu.Unlock()

	atomic.AddUint64(&gc.collections, 1)

	// Mark phase
	gc.mark()

	// Sweep phase
	collected := gc.sweep()

	atomic.AddUint64(&gc.collected, uint64(collected))
}

// mark implements the marking phase using tri-color algorithm
func (gc *GarbageCollector) mark() {
	// Reset all objects to white
	for _, obj := range gc.objects {
		obj.Color = White
	}

	// Mark roots as gray
	graySet := make([]*Object, 0)
	for _, root := range gc.roots {
		if root.Color == White {
			root.Color = Gray
			graySet = append(graySet, root)
		}
	}

	// Process gray objects
	for len(graySet) > 0 {
		obj := graySet[0]
		graySet = graySet[1:]

		// Mark all referenced objects as gray
		for _, ref := range obj.References {
			if ref.Color == White {
				ref.Color = Gray
				graySet = append(graySet, ref)
			}
		}

		// Mark this object as black
		obj.Color = Black
	}
}

// sweep collects white (unreachable) objects
func (gc *GarbageCollector) sweep() int {
	collected := 0

	for id, obj := range gc.objects {
		if obj.Color == White {
			delete(gc.objects, id)
			collected++
		}
	}

	return collected
}

// Stats returns GC statistics
func (gc *GarbageCollector) Stats() map[string]interface{} {
	gc.mu.RLock()
	defer gc.mu.RUnlock()

	return map[string]interface{}{
		"objects":     len(gc.objects),
		"roots":       len(gc.roots),
		"collections": atomic.LoadUint64(&gc.collections),
		"collected":   atomic.LoadUint64(&gc.collected),
	}
}

// RefCountCollector implements reference counting GC
type RefCountCollector struct {
	objects map[uint64]*Object
	mu      sync.RWMutex
	nextID  uint64
}

func NewRefCountCollector() *RefCountCollector {
	return &RefCountCollector{
		objects: make(map[uint64]*Object),
	}
}

func (rc *RefCountCollector) Allocate(data interface{}) *Object {
	rc.mu.Lock()
	defer rc.mu.Unlock()

	obj := &Object{
		ID:       atomic.AddUint64(&rc.nextID, 1),
		Data:     data,
		RefCount: 1, // Start with one reference
	}

	rc.objects[obj.ID] = obj
	return obj
}

func (rc *RefCountCollector) Retain(obj *Object) {
	atomic.AddInt32(&obj.RefCount, 1)
}

func (rc *RefCountCollector) Release(obj *Object) {
	newCount := atomic.AddInt32(&obj.RefCount, -1)
	if newCount == 0 {
		rc.collect(obj)
	}
}

func (rc *RefCountCollector) collect(obj *Object) {
	rc.mu.Lock()
	defer rc.mu.Unlock()

	// Release references to other objects
	for _, ref := range obj.References {
		rc.Release(ref)
	}

	delete(rc.objects, obj.ID)
}

// ForceGC triggers Go's garbage collector
func ForceGC() {
	runtime.GC()
}

// MemStats returns memory statistics
func MemStats() *runtime.MemStats {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	return &m
}
