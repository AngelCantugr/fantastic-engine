package channels

import (
	"context"
	"testing"
	"time"
)

func TestGenerator(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	ch := Generator(ctx, 1, 2, 3, 4, 5)
	count := 0
	for range ch {
		count++
	}

	if count != 5 {
		t.Errorf("Expected 5 values, got %d", count)
	}
}

func TestFanOutFanIn(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
	workers := FanOut(ctx, input, 3, func(x int) int { return x * 2 })
	result := FanIn(ctx, workers...)

	sum := 0
	for val := range result {
		sum += val
	}

	expected := (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10) * 2
	if sum != expected {
		t.Errorf("Expected sum %d, got %d", expected, sum)
	}
}

func TestOrDone(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	input := make(chan int)

	go func() {
		input <- 1
		input <- 2
		time.Sleep(100 * time.Millisecond)
		cancel()
	}()

	output := OrDone(ctx, input)
	count := 0
	for range output {
		count++
	}

	if count != 2 {
		t.Errorf("Expected 2 values before cancel, got %d", count)
	}
}

func TestTee(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3)
	out1, out2 := Tee(ctx, input)

	sum1 := 0
	sum2 := 0

	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		for val := range out1 {
			sum1 += val
		}
	}()

	go func() {
		defer wg.Done()
		for val := range out2 {
			sum2 += val
		}
	}()

	wg.Wait()

	if sum1 != 6 || sum2 != 6 {
		t.Errorf("Expected both sums to be 6, got %d and %d", sum1, sum2)
	}
}

func TestTake(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
	taken := Take(ctx, input, 3)

	count := 0
	for range taken {
		count++
	}

	if count != 3 {
		t.Errorf("Expected 3 values, got %d", count)
	}
}

func TestSkip(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5)
	skipped := Skip(ctx, input, 2)

	var values []int
	for val := range skipped {
		values = append(values, val)
	}

	expected := []int{3, 4, 5}
	if len(values) != len(expected) {
		t.Errorf("Expected %d values, got %d", len(expected), len(values))
	}

	for i, v := range values {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestMap(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5)
	mapped := Map(ctx, input, func(x int) int { return x * 2 })

	var values []int
	for val := range mapped {
		values = append(values, val)
	}

	expected := []int{2, 4, 6, 8, 10}
	for i, v := range values {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestFilter(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5, 6)
	filtered := Filter(ctx, input, func(x int) bool { return x%2 == 0 })

	var values []int
	for val := range filtered {
		values = append(values, val)
	}

	expected := []int{2, 4, 6}
	if len(values) != len(expected) {
		t.Errorf("Expected %d values, got %d", len(expected), len(values))
	}
}

func TestBatch(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	input := Generator(ctx, 1, 2, 3, 4, 5, 6, 7)
	batched := Batch(ctx, input, 3)

	var batches [][]int
	for batch := range batched {
		batches = append(batches, batch)
	}

	if len(batches) != 3 {
		t.Errorf("Expected 3 batches, got %d", len(batches))
	}

	if len(batches[0]) != 3 || len(batches[1]) != 3 || len(batches[2]) != 1 {
		t.Error("Unexpected batch sizes")
	}
}

func BenchmarkFanOut(b *testing.B) {
	ctx := context.Background()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		input := Generator(ctx, 1, 2, 3, 4, 5)
		workers := FanOut(ctx, input, 3, func(x int) int { return x * 2 })
		result := FanIn(ctx, workers...)
		for range result {
		}
	}
}
