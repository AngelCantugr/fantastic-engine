package contextpatterns

import (
	"context"
	"errors"
	"sync/atomic"
	"testing"
	"time"
)

func TestWithRequestID(t *testing.T) {
	ctx := WithRequestID(context.Background(), "test-123")

	id, ok := GetRequestID(ctx)
	if !ok {
		t.Fatal("Expected request ID to be present")
	}
	if id != "test-123" {
		t.Errorf("Expected request ID 'test-123', got '%s'", id)
	}
}

func TestWithUserID(t *testing.T) {
	ctx := WithUserID(context.Background(), "user-456")

	id, ok := GetUserID(ctx)
	if !ok {
		t.Fatal("Expected user ID to be present")
	}
	if id != "user-456" {
		t.Errorf("Expected user ID 'user-456', got '%s'", id)
	}
}

func TestGenerator(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	values := []interface{}{1, 2, 3, 4, 5}
	ch := Generator(ctx, values...)

	var results []interface{}
	for v := range ch {
		results = append(results, v)
	}

	if len(results) != len(values) {
		t.Errorf("Expected %d values, got %d", len(values), len(results))
	}
}

func TestGeneratorCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	values := make([]interface{}, 1000)
	for i := range values {
		values[i] = i
	}

	ch := Generator(ctx, values...)

	// Read a few values then cancel
	<-ch
	<-ch
	cancel()

	// Channel should close
	count := 2
	for range ch {
		count++
	}

	if count >= len(values) {
		t.Errorf("Expected early termination, got %d values", count)
	}
}

func TestFanOutFanIn(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Generate input
	input := Generator(ctx, 1, 2, 3, 4, 5)

	// Fan out to 3 workers
	processor := func(ctx context.Context, val interface{}) interface{} {
		return val.(int) * 2
	}
	workers := FanOut(ctx, input, 3, processor)

	// Fan in results
	results := FanIn(ctx, workers...)

	// Collect results
	var sum int
	for result := range results {
		sum += result.(int)
	}

	expected := (1 + 2 + 3 + 4 + 5) * 2
	if sum != expected {
		t.Errorf("Expected sum %d, got %d", expected, sum)
	}
}

func TestRetry(t *testing.T) {
	ctx := context.Background()

	// Test successful retry
	attempts := 0
	err := Retry(ctx, 3, 10*time.Millisecond, func(ctx context.Context) error {
		attempts++
		if attempts < 2 {
			return errors.New("temporary error")
		}
		return nil
	})

	if err != nil {
		t.Errorf("Expected success after retry, got error: %v", err)
	}
	if attempts != 2 {
		t.Errorf("Expected 2 attempts, got %d", attempts)
	}
}

func TestRetryFailure(t *testing.T) {
	ctx := context.Background()

	// Test all retries fail
	attempts := 0
	err := Retry(ctx, 3, 10*time.Millisecond, func(ctx context.Context) error {
		attempts++
		return errors.New("persistent error")
	})

	if err == nil {
		t.Error("Expected error after all retries failed")
	}
	if attempts != 3 {
		t.Errorf("Expected 3 attempts, got %d", attempts)
	}
}

func TestRetryCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	// Cancel after first attempt
	go func() {
		time.Sleep(50 * time.Millisecond)
		cancel()
	}()

	attempts := 0
	err := Retry(ctx, 10, 100*time.Millisecond, func(ctx context.Context) error {
		attempts++
		return errors.New("error")
	})

	if err != context.Canceled {
		t.Errorf("Expected context.Canceled, got %v", err)
	}
	if attempts >= 10 {
		t.Errorf("Expected early termination, got %d attempts", attempts)
	}
}

func TestTimeout(t *testing.T) {
	// Test successful execution
	err := Timeout(100*time.Millisecond, func(ctx context.Context) error {
		time.Sleep(10 * time.Millisecond)
		return nil
	})

	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	// Test timeout
	err = Timeout(50*time.Millisecond, func(ctx context.Context) error {
		time.Sleep(200 * time.Millisecond)
		return nil
	})

	if err != ErrTimeout {
		t.Errorf("Expected ErrTimeout, got %v", err)
	}
}

func TestWithDeadlinePropagation(t *testing.T) {
	// Parent has earlier deadline
	parentDeadline := time.Now().Add(100 * time.Millisecond)
	parent, cancel := context.WithDeadline(context.Background(), parentDeadline)
	defer cancel()

	childDeadline := time.Now().Add(200 * time.Millisecond)
	child, childCancel := WithDeadlinePropagation(parent, childDeadline)
	defer childCancel()

	// Child should inherit parent's earlier deadline
	deadline, ok := child.Deadline()
	if !ok {
		t.Fatal("Expected child to have deadline")
	}

	if deadline.After(parentDeadline.Add(time.Millisecond)) {
		t.Error("Child deadline should not be later than parent")
	}
}

func TestOrDone(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	input := make(chan interface{})
	output := OrDone(ctx, input)

	// Send some values
	go func() {
		input <- 1
		input <- 2
		time.Sleep(50 * time.Millisecond)
		cancel()
	}()

	count := 0
	for range output {
		count++
	}

	// Should receive exactly 2 values before cancellation
	if count != 2 {
		t.Errorf("Expected 2 values, got %d", count)
	}
}

func TestBridge(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	// Create channel of channels
	chanStream := make(chan (<-chan interface{}))

	go func() {
		defer close(chanStream)
		for i := 0; i < 3; i++ {
			ch := make(chan interface{})
			chanStream <- ch
			go func(c chan interface{}, start int) {
				defer close(c)
				for j := 0; j < 3; j++ {
					c <- start + j
				}
			}(ch, i*10)
		}
	}()

	results := Bridge(ctx, chanStream)

	count := 0
	for range results {
		count++
	}

	expected := 9 // 3 channels * 3 values each
	if count != expected {
		t.Errorf("Expected %d values, got %d", expected, count)
	}
}

func TestDebounce(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	var counter int32
	increment := func() {
		atomic.AddInt32(&counter, 1)
	}

	debounced := Debounce(ctx, 100*time.Millisecond, increment)

	// Call multiple times rapidly
	for i := 0; i < 10; i++ {
		debounced()
		time.Sleep(10 * time.Millisecond)
	}

	// Wait for debounce period
	time.Sleep(150 * time.Millisecond)

	// Should only execute once after the last call
	count := atomic.LoadInt32(&counter)
	if count != 1 {
		t.Errorf("Expected 1 execution, got %d", count)
	}
}

func TestThrottle(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	var counter int32
	increment := func() {
		atomic.AddInt32(&counter, 1)
	}

	throttled := Throttle(ctx, 100*time.Millisecond, increment)

	// Call multiple times rapidly
	for i := 0; i < 10; i++ {
		throttled()
		time.Sleep(10 * time.Millisecond)
	}

	// Should execute only once since interval hasn't passed
	count := atomic.LoadInt32(&counter)
	if count != 1 {
		t.Errorf("Expected 1 execution, got %d", count)
	}

	// Wait for interval and call again
	time.Sleep(100 * time.Millisecond)
	throttled()

	count = atomic.LoadInt32(&counter)
	if count != 2 {
		t.Errorf("Expected 2 executions, got %d", count)
	}
}

func TestBatch(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	input := make(chan interface{})
	batches := Batch(ctx, input, 3, 100*time.Millisecond)

	go func() {
		defer close(input)
		for i := 0; i < 7; i++ {
			input <- i
		}
	}()

	var allBatches [][]interface{}
	for batch := range batches {
		allBatches = append(allBatches, batch)
	}

	// Should get 3 batches: [0,1,2], [3,4,5], [6]
	if len(allBatches) != 3 {
		t.Errorf("Expected 3 batches, got %d", len(allBatches))
	}

	if len(allBatches[0]) != 3 {
		t.Errorf("Expected first batch size 3, got %d", len(allBatches[0]))
	}
}

func TestMerge(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	fn1 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(10 * time.Millisecond)
		return "result1", nil
	}

	fn2 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(20 * time.Millisecond)
		return "result2", nil
	}

	fn3 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(15 * time.Millisecond)
		return "result3", nil
	}

	results, err := Merge(ctx, fn1, fn2, fn3)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	if len(results) != 3 {
		t.Errorf("Expected 3 results, got %d", len(results))
	}
}

func TestMergeWithError(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	fn1 := func(ctx context.Context) (interface{}, error) {
		return "result1", nil
	}

	fn2 := func(ctx context.Context) (interface{}, error) {
		return nil, errors.New("error in fn2")
	}

	_, err := Merge(ctx, fn1, fn2)
	if err == nil {
		t.Error("Expected error from merge")
	}
}

func TestFirstSuccess(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	fn1 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(100 * time.Millisecond)
		return nil, errors.New("error1")
	}

	fn2 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(50 * time.Millisecond)
		return "success", nil
	}

	fn3 := func(ctx context.Context) (interface{}, error) {
		time.Sleep(200 * time.Millisecond)
		return "late success", nil
	}

	result, err := FirstSuccess(ctx, fn1, fn2, fn3)
	if err != nil {
		t.Fatalf("Expected success, got error: %v", err)
	}

	if result != "success" {
		t.Errorf("Expected 'success', got %v", result)
	}
}

func TestCancellationReason(t *testing.T) {
	cr := NewCancellationReason()

	testErr := errors.New("test error")
	cr.SetReason(testErr)

	if cr.Reason() != testErr {
		t.Errorf("Expected reason %v, got %v", testErr, cr.Reason())
	}

	// Second set should be ignored
	cr.SetReason(errors.New("another error"))
	if cr.Reason() != testErr {
		t.Error("Reason should not change after first set")
	}
}

// Benchmark tests

func BenchmarkContextValue(b *testing.B) {
	ctx := WithRequestID(context.Background(), "test-123")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		GetRequestID(ctx)
	}
}

func BenchmarkGenerator(b *testing.B) {
	ctx := context.Background()
	values := make([]interface{}, 100)
	for i := range values {
		values[i] = i
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ch := Generator(ctx, values...)
		for range ch {
		}
	}
}

func BenchmarkFanOutFanIn(b *testing.B) {
	ctx := context.Background()
	processor := func(ctx context.Context, val interface{}) interface{} {
		return val.(int) * 2
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		input := Generator(ctx, 1, 2, 3, 4, 5)
		workers := FanOut(ctx, input, 3, processor)
		results := FanIn(ctx, workers...)
		for range results {
		}
	}
}
