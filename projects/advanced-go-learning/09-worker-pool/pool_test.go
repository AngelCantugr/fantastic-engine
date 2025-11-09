package workerpool

import (
	"context"
	"errors"
	"sync/atomic"
	"testing"
	"time"
)

func TestPoolBasic(t *testing.T) {
	pool := NewPool(3, 10)
	defer pool.Shutdown(true)

	var counter int32
	for i := 0; i < 10; i++ {
		pool.Submit(func(ctx context.Context) error {
			atomic.AddInt32(&counter, 1)
			return nil
		})
	}

	time.Sleep(100 * time.Millisecond)

	if atomic.LoadInt32(&counter) != 10 {
		t.Errorf("Expected 10 jobs completed, got %d", counter)
	}
}

func TestPoolWithErrors(t *testing.T) {
	pool := NewPool(2, 5)
	defer pool.Shutdown(true)

	for i := 0; i < 5; i++ {
		pool.Submit(func(ctx context.Context) error {
			return errors.New("test error")
		})
	}

	time.Sleep(100 * time.Millisecond)
	stats := pool.Stats()

	if stats["failed"].(uint64) != 5 {
		t.Errorf("Expected 5 failed jobs, got %d", stats["failed"])
	}
}

func TestPoolShutdown(t *testing.T) {
	pool := NewPool(2, 5)

	pool.Submit(func(ctx context.Context) error {
		time.Sleep(50 * time.Millisecond)
		return nil
	})

	pool.Shutdown(true)

	err := pool.Submit(func(ctx context.Context) error {
		return nil
	})

	if err == nil {
		t.Error("Expected error when submitting to closed pool")
	}
}

func BenchmarkPool(b *testing.B) {
	pool := NewPool(10, 1000)
	defer pool.Shutdown(true)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pool.Submit(func(ctx context.Context) error {
			time.Sleep(time.Microsecond)
			return nil
		})
	}
}
