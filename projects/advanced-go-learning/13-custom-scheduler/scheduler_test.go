package scheduler

import (
	"sync/atomic"
	"testing"
	"time"
)

func TestSchedulerBasic(t *testing.T) {
	sched := NewScheduler(4)
	defer sched.Shutdown()

	var counter int64
	for i := 0; i < 100; i++ {
		sched.Submit(func() {
			atomic.AddInt64(&counter, 1)
		})
	}

	time.Sleep(200 * time.Millisecond)

	if atomic.LoadInt64(&counter) != 100 {
		t.Errorf("Expected 100 tasks completed, got %d", counter)
	}
}

func TestSchedulerWorkStealing(t *testing.T) {
	sched := NewScheduler(4)
	defer sched.Shutdown()

	var counter int64
	for i := 0; i < 1000; i++ {
		sched.Submit(func() {
			time.Sleep(time.Millisecond)
			atomic.AddInt64(&counter, 1)
		})
	}

	time.Sleep(2 * time.Second)

	stats := sched.Stats()
	if stats["stolen_tasks"].(uint64) == 0 {
		t.Error("Expected some work stealing to occur")
	}
}

func BenchmarkScheduler(b *testing.B) {
	sched := NewScheduler(4)
	defer sched.Shutdown()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		sched.Submit(func() {
			time.Sleep(time.Microsecond)
		})
	}
}

func BenchmarkGoRoutines(b *testing.B) {
	var wg sync.WaitGroup
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			time.Sleep(time.Microsecond)
		}()
	}
	wg.Wait()
}
