package contextpatterns

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"
)

// Common errors
var (
	ErrTimeout    = errors.New("operation timed out")
	ErrCancelled  = errors.New("operation cancelled")
	ErrNoValue    = errors.New("value not found in context")
)

// ContextKey is a type-safe key for context values
type ContextKey string

// Common context keys
const (
	RequestIDKey  ContextKey = "requestID"
	UserIDKey     ContextKey = "userID"
	TraceIDKey    ContextKey = "traceID"
	SessionIDKey  ContextKey = "sessionID"
)

// WithRequestID adds a request ID to the context
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, RequestIDKey, requestID)
}

// GetRequestID retrieves the request ID from context
func GetRequestID(ctx context.Context) (string, bool) {
	id, ok := ctx.Value(RequestIDKey).(string)
	return id, ok
}

// WithUserID adds a user ID to the context
func WithUserID(ctx context.Context, userID string) context.Context {
	return context.WithValue(ctx, UserIDKey, userID)
}

// GetUserID retrieves the user ID from context
func GetUserID(ctx context.Context) (string, bool) {
	id, ok := ctx.Value(UserIDKey).(string)
	return id, ok
}

// Pipeline creates a processing pipeline with context support
func Pipeline(ctx context.Context, stages ...func(context.Context, <-chan interface{}) <-chan interface{}) <-chan interface{} {
	var c <-chan interface{}
	for _, stage := range stages {
		c = stage(ctx, c)
	}
	return c
}

// Generator creates a channel that generates values until context is cancelled
func Generator(ctx context.Context, values ...interface{}) <-chan interface{} {
	out := make(chan interface{})
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

// FanOut distributes work across multiple workers
func FanOut(ctx context.Context, input <-chan interface{}, workers int,
	processor func(context.Context, interface{}) interface{}) []<-chan interface{} {

	outputs := make([]<-chan interface{}, workers)

	for i := 0; i < workers; i++ {
		outputs[i] = worker(ctx, input, processor)
	}

	return outputs
}

// worker processes items from input channel
func worker(ctx context.Context, input <-chan interface{},
	processor func(context.Context, interface{}) interface{}) <-chan interface{} {

	out := make(chan interface{})
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
				result := processor(ctx, item)
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
func FanIn(ctx context.Context, channels ...<-chan interface{}) <-chan interface{} {
	var wg sync.WaitGroup
	out := make(chan interface{})

	// Start a goroutine for each input channel
	multiplex := func(c <-chan interface{}) {
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

	// Close output channel when all inputs are done
	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// Retry executes a function with retries and exponential backoff
func Retry(ctx context.Context, maxRetries int, baseDelay time.Duration,
	fn func(context.Context) error) error {

	var err error
	for i := 0; i < maxRetries; i++ {
		if i > 0 {
			delay := baseDelay * time.Duration(1<<uint(i-1))
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(delay):
			}
		}

		err = fn(ctx)
		if err == nil {
			return nil
		}

		// Check if context was cancelled
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}
	}

	return fmt.Errorf("failed after %d retries: %w", maxRetries, err)
}

// Timeout executes a function with a timeout
func Timeout(timeout time.Duration, fn func(context.Context) error) error {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	errChan := make(chan error, 1)
	go func() {
		errChan <- fn(ctx)
	}()

	select {
	case <-ctx.Done():
		return ErrTimeout
	case err := <-errChan:
		return err
	}
}

// WithDeadlinePropagation creates a child context with a deadline
// that respects the parent's deadline if it's sooner
func WithDeadlinePropagation(parent context.Context, deadline time.Time) (context.Context, context.CancelFunc) {
	if parentDeadline, ok := parent.Deadline(); ok {
		if parentDeadline.Before(deadline) {
			// Parent deadline is sooner, use it
			return context.WithCancel(parent)
		}
	}
	return context.WithDeadline(parent, deadline)
}

// OrDone wraps a channel to close when context is done
func OrDone(ctx context.Context, c <-chan interface{}) <-chan interface{} {
	out := make(chan interface{})
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

// Bridge creates a channel of channels into a single channel
func Bridge(ctx context.Context, chanStream <-chan <-chan interface{}) <-chan interface{} {
	out := make(chan interface{})
	go func() {
		defer close(out)
		for {
			var stream <-chan interface{}
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

// Debounce creates a debounced function that delays execution
func Debounce(ctx context.Context, delay time.Duration, fn func()) func() {
	var timer *time.Timer
	var mu sync.Mutex

	return func() {
		mu.Lock()
		defer mu.Unlock()

		if timer != nil {
			timer.Stop()
		}

		timer = time.AfterFunc(delay, func() {
			select {
			case <-ctx.Done():
				return
			default:
				fn()
			}
		})

		// Ensure timer is cancelled if context is done
		go func() {
			<-ctx.Done()
			mu.Lock()
			if timer != nil {
				timer.Stop()
			}
			mu.Unlock()
		}()
	}
}

// Throttle creates a throttled function that limits execution rate
func Throttle(ctx context.Context, interval time.Duration, fn func()) func() {
	var last time.Time
	var mu sync.Mutex

	return func() {
		mu.Lock()
		defer mu.Unlock()

		now := time.Now()
		if now.Sub(last) < interval {
			return
		}

		select {
		case <-ctx.Done():
			return
		default:
			last = now
			fn()
		}
	}
}

// Batch processes items in batches with context support
func Batch(ctx context.Context, input <-chan interface{}, batchSize int,
	maxWait time.Duration) <-chan []interface{} {

	out := make(chan []interface{})

	go func() {
		defer close(out)

		var batch []interface{}
		timer := time.NewTimer(maxWait)
		defer timer.Stop()

		flush := func() {
			if len(batch) > 0 {
				select {
				case <-ctx.Done():
					return
				case out <- batch:
					batch = nil
				}
			}
			timer.Reset(maxWait)
		}

		for {
			select {
			case <-ctx.Done():
				flush()
				return
			case <-timer.C:
				flush()
			case item, ok := <-input:
				if !ok {
					flush()
					return
				}
				batch = append(batch, item)
				if len(batch) >= batchSize {
					flush()
				}
			}
		}
	}()

	return out
}

// Merge combines results from multiple goroutines
func Merge(ctx context.Context, fns ...func(context.Context) (interface{}, error)) ([]interface{}, error) {
	results := make([]interface{}, len(fns))
	errors := make([]error, len(fns))
	var wg sync.WaitGroup

	for i, fn := range fns {
		wg.Add(1)
		go func(index int, f func(context.Context) (interface{}, error)) {
			defer wg.Done()
			results[index], errors[index] = f(ctx)
		}(i, fn)
	}

	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-ctx.Done():
		return nil, ctx.Err()
	case <-done:
		// Check for errors
		for _, err := range errors {
			if err != nil {
				return results, err
			}
		}
		return results, nil
	}
}

// FirstSuccess returns the first successful result from multiple operations
func FirstSuccess(ctx context.Context, fns ...func(context.Context) (interface{}, error)) (interface{}, error) {
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	type result struct {
		value interface{}
		err   error
	}

	results := make(chan result, len(fns))

	for _, fn := range fns {
		go func(f func(context.Context) (interface{}, error)) {
			value, err := f(ctx)
			select {
			case <-ctx.Done():
			case results <- result{value, err}:
			}
		}(fn)
	}

	var lastErr error
	for i := 0; i < len(fns); i++ {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case r := <-results:
			if r.err == nil {
				return r.value, nil
			}
			lastErr = r.err
		}
	}

	if lastErr != nil {
		return nil, lastErr
	}
	return nil, errors.New("all operations failed")
}

// WithCancellationReason creates a context that can store a cancellation reason
type CancellationReason struct {
	mu     sync.RWMutex
	reason error
}

func (cr *CancellationReason) SetReason(err error) {
	cr.mu.Lock()
	defer cr.mu.Unlock()
	if cr.reason == nil {
		cr.reason = err
	}
}

func (cr *CancellationReason) Reason() error {
	cr.mu.RLock()
	defer cr.mu.RUnlock()
	return cr.reason
}

// NewCancellationReason creates a new cancellation reason tracker
func NewCancellationReason() *CancellationReason {
	return &CancellationReason{}
}
