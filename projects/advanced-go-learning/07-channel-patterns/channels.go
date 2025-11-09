package channels

import (
	"context"
	"sync"
)

// Generator creates a channel that emits values
func Generator[T any](ctx context.Context, values ...T) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for _, v := range values {
			select {
			case <-ctx.Done():
				return
			case out <- v:
			}
		}
	}()
	return out
}

// Pipeline chains multiple stages together
func Pipeline[T any](ctx context.Context, stages ...func(context.Context, <-chan T) <-chan T) func(<-chan T) <-chan T {
	return func(in <-chan T) <-chan T {
		c := in
		for _, stage := range stages {
			c = stage(ctx, c)
		}
		return c
	}
}

// FanOut distributes work across multiple goroutines
func FanOut[T, U any](ctx context.Context, input <-chan T, workers int, process func(T) U) []<-chan U {
	outputs := make([]<-chan U, workers)
	for i := 0; i < workers; i++ {
		outputs[i] = worker(ctx, input, process)
	}
	return outputs
}

// worker processes items from input channel
func worker[T, U any](ctx context.Context, input <-chan T, process func(T) U) <-chan U {
	out := make(chan U)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case item, ok := <-input:
				if !ok {
					return
				}
				result := process(item)
				select {
				case <-ctx.Done():
					return
				case out <- result:
				}
			}
		}
	}()
	return out
}

// FanIn merges multiple channels into one
func FanIn[T any](ctx context.Context, channels ...<-chan T) <-chan T {
	var wg sync.WaitGroup
	out := make(chan T)

	multiplex := func(c <-chan T) {
		defer wg.Done()
		for {
			select {
			case <-ctx.Done():
				return
			case val, ok := <-c:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- val:
				}
			}
		}
	}

	wg.Add(len(channels))
	for _, c := range channels {
		go multiplex(c)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// OrDone wraps a channel to respect context cancellation
func OrDone[T any](ctx context.Context, c <-chan T) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case val, ok := <-c:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- val:
				}
			}
		}
	}()
	return out
}

// Tee splits one channel into two
func Tee[T any](ctx context.Context, in <-chan T) (<-chan T, <-chan T) {
	out1 := make(chan T)
	out2 := make(chan T)

	go func() {
		defer close(out1)
		defer close(out2)
		for val := range OrDone(ctx, in) {
			var out1, out2 = out1, out2
			for i := 0; i < 2; i++ {
				select {
				case <-ctx.Done():
					return
				case out1 <- val:
					out1 = nil
				case out2 <- val:
					out2 = nil
				}
			}
		}
	}()

	return out1, out2
}

// Bridge converts channel of channels into single channel
func Bridge[T any](ctx context.Context, chanStream <-chan <-chan T) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for {
			var stream <-chan T
			select {
			case <-ctx.Done():
				return
			case maybeStream, ok := <-chanStream:
				if !ok {
					return
				}
				stream = maybeStream
			}

			for val := range OrDone(ctx, stream) {
				select {
				case <-ctx.Done():
					return
				case out <- val:
				}
			}
		}
	}()
	return out
}

// Take takes first n values from channel
func Take[T any](ctx context.Context, in <-chan T, n int) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for i := 0; i < n; i++ {
			select {
			case <-ctx.Done():
				return
			case val, ok := <-in:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- val:
				}
			}
		}
	}()
	return out
}

// Skip skips first n values from channel
func Skip[T any](ctx context.Context, in <-chan T, n int) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for i := 0; i < n; i++ {
			select {
			case <-ctx.Done():
				return
			case _, ok := <-in:
				if !ok {
					return
				}
			}
		}
		for val := range OrDone(ctx, in) {
			select {
			case <-ctx.Done():
				return
			case out <- val:
			}
		}
	}()
	return out
}

// Repeat repeats a value n times
func Repeat[T any](ctx context.Context, value T, times int) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for i := 0; i < times; i++ {
			select {
			case <-ctx.Done():
				return
			case out <- value:
			}
		}
	}()
	return out
}

// Map transforms values in a channel
func Map[T, U any](ctx context.Context, in <-chan T, fn func(T) U) <-chan U {
	out := make(chan U)
	go func() {
		defer close(out)
		for val := range OrDone(ctx, in) {
			select {
			case <-ctx.Done():
				return
			case out <- fn(val):
			}
		}
	}()
	return out
}

// Filter filters values in a channel
func Filter[T any](ctx context.Context, in <-chan T, predicate func(T) bool) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for val := range OrDone(ctx, in) {
			if predicate(val) {
				select {
				case <-ctx.Done():
					return
				case out <- val:
				}
			}
		}
	}()
	return out
}

// Batch groups values into batches
func Batch[T any](ctx context.Context, in <-chan T, size int) <-chan []T {
	out := make(chan []T)
	go func() {
		defer close(out)
		batch := make([]T, 0, size)
		for val := range OrDone(ctx, in) {
			batch = append(batch, val)
			if len(batch) == size {
				select {
				case <-ctx.Done():
					return
				case out <- batch:
					batch = make([]T, 0, size)
				}
			}
		}
		if len(batch) > 0 {
			select {
			case <-ctx.Done():
				return
			case out <- batch:
			}
		}
	}()
	return out
}
