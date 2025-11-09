package lockfree

import (
	"sync"
	"testing"
)

func TestLockFreeStack(t *testing.T) {
	stack := NewLockFreeStack[int]()

	stack.Push(1)
	stack.Push(2)
	stack.Push(3)

	val, ok := stack.Pop()
	if !ok || val != 3 {
		t.Errorf("Expected 3, got %d", val)
	}

	val, ok = stack.Pop()
	if !ok || val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}
}

func TestLockFreeStackConcurrent(t *testing.T) {
	stack := NewLockFreeStack[int]()
	var wg sync.WaitGroup

	// Push concurrently
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			stack.Push(val)
		}(i)
	}

	wg.Wait()

	// Pop all
	count := 0
	for {
		if _, ok := stack.Pop(); !ok {
			break
		}
		count++
	}

	if count != 100 {
		t.Errorf("Expected 100 items, got %d", count)
	}
}

func TestLockFreeQueue(t *testing.T) {
	queue := NewLockFreeQueue[int]()

	queue.Enqueue(1)
	queue.Enqueue(2)
	queue.Enqueue(3)

	val, ok := queue.Dequeue()
	if !ok || val != 1 {
		t.Errorf("Expected 1, got %d", val)
	}

	val, ok = queue.Dequeue()
	if !ok || val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}
}

func TestLockFreeQueueConcurrent(t *testing.T) {
	queue := NewLockFreeQueue[int]()
	var wg sync.WaitGroup

	// Enqueue concurrently
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(val int) {
			defer wg.Done()
			queue.Enqueue(val)
		}(i)
	}

	wg.Wait()

	// Dequeue all
	count := 0
	for {
		if _, ok := queue.Dequeue(); !ok {
			break
		}
		count++
	}

	if count != 100 {
		t.Errorf("Expected 100 items, got %d", count)
	}
}

func TestLockFreeCounter(t *testing.T) {
	counter := NewLockFreeCounter()

	counter.Increment()
	counter.Increment()
	counter.Increment()

	if counter.Get() != 3 {
		t.Errorf("Expected 3, got %d", counter.Get())
	}

	counter.Decrement()

	if counter.Get() != 2 {
		t.Errorf("Expected 2, got %d", counter.Get())
	}
}

func TestLockFreeCounterConcurrent(t *testing.T) {
	counter := NewLockFreeCounter()
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	wg.Wait()

	if counter.Get() != 1000 {
		t.Errorf("Expected 1000, got %d", counter.Get())
	}
}

func BenchmarkLockFreeStack(b *testing.B) {
	stack := NewLockFreeStack[int]()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		stack.Push(i)
		stack.Pop()
	}
}

func BenchmarkMutexStack(b *testing.B) {
	type mutexStack struct {
		items []int
		mu    sync.Mutex
	}

	stack := &mutexStack{}
	push := func(val int) {
		stack.mu.Lock()
		stack.items = append(stack.items, val)
		stack.mu.Unlock()
	}

	pop := func() (int, bool) {
		stack.mu.Lock()
		defer stack.mu.Unlock()
		if len(stack.items) == 0 {
			return 0, false
		}
		val := stack.items[len(stack.items)-1]
		stack.items = stack.items[:len(stack.items)-1]
		return val, true
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		push(i)
		pop()
	}
}

func BenchmarkLockFreeCounter(b *testing.B) {
	counter := NewLockFreeCounter()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		counter.Increment()
	}
}

func BenchmarkMutexCounter(b *testing.B) {
	var counter int
	var mu sync.Mutex

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		mu.Lock()
		counter++
		mu.Unlock()
	}
}
