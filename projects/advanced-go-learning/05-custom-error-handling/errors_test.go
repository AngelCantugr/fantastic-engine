package errors

import (
	"errors"
	"fmt"
	"strings"
	"testing"
)

func TestNew(t *testing.T) {
	err := New("test error")
	if err == nil {
		t.Fatal("Expected error to be non-nil")
	}

	if !strings.Contains(err.Error(), "test error") {
		t.Errorf("Expected error message to contain 'test error', got: %s", err.Error())
	}

	// Check for stack trace
	if e, ok := err.(*ErrorWithStack); ok {
		if len(e.Stack) == 0 {
			t.Error("Expected stack trace to be captured")
		}
	} else {
		t.Error("Expected error to be *ErrorWithStack")
	}
}

func TestWrap(t *testing.T) {
	original := errors.New("original error")
	wrapped := Wrap(original, "wrapped context")

	if wrapped == nil {
		t.Fatal("Expected wrapped error to be non-nil")
	}

	if !strings.Contains(wrapped.Error(), "wrapped context") {
		t.Errorf("Expected error to contain context, got: %s", wrapped.Error())
	}

	if !strings.Contains(wrapped.Error(), "original error") {
		t.Errorf("Expected error to contain original message, got: %s", wrapped.Error())
	}
}

func TestWrapNil(t *testing.T) {
	wrapped := Wrap(nil, "context")
	if wrapped != nil {
		t.Error("Wrapping nil should return nil")
	}
}

func TestWrapf(t *testing.T) {
	original := errors.New("failed")
	wrapped := Wrapf(original, "operation failed with code %d", 42)

	expected := "operation failed with code 42"
	if !strings.Contains(wrapped.Error(), expected) {
		t.Errorf("Expected error to contain '%s', got: %s", expected, wrapped.Error())
	}
}

func TestErrorUnwrap(t *testing.T) {
	original := errors.New("original")
	wrapped := Wrap(original, "context")

	unwrapped := errors.Unwrap(wrapped)
	if unwrapped != original {
		t.Errorf("Expected unwrapped error to be original, got: %v", unwrapped)
	}
}

func TestErrorChain(t *testing.T) {
	err1 := errors.New("base error")
	err2 := Wrap(err1, "level 2")
	err3 := Wrap(err2, "level 3")

	chain := ErrorChain(err3)
	if len(chain) != 3 {
		t.Errorf("Expected chain length 3, got %d", len(chain))
	}
}

func TestValidationError(t *testing.T) {
	err := NewValidationError("email", "invalid format", "not-an-email")

	if !strings.Contains(err.Error(), "email") {
		t.Errorf("Expected error to contain field name, got: %s", err.Error())
	}

	if !strings.Contains(err.Error(), "invalid format") {
		t.Errorf("Expected error to contain message, got: %s", err.Error())
	}
}

func TestMultiError(t *testing.T) {
	merr := NewMultiError()

	err1 := errors.New("error 1")
	err2 := errors.New("error 2")
	err3 := errors.New("error 3")

	merr.Add(err1)
	merr.Add(err2)
	merr.Add(err3)

	if len(merr.Errors) != 3 {
		t.Errorf("Expected 3 errors, got %d", len(merr.Errors))
	}

	errMsg := merr.Error()
	if !strings.Contains(errMsg, "3 errors occurred") {
		t.Errorf("Expected error count in message, got: %s", errMsg)
	}
}

func TestMultiErrorNil(t *testing.T) {
	merr := NewMultiError()
	merr.Add(nil)

	if len(merr.Errors) != 0 {
		t.Error("Expected nil errors to be ignored")
	}

	if merr.ErrorOrNil() != nil {
		t.Error("Expected ErrorOrNil to return nil for empty MultiError")
	}
}

func TestAPIError(t *testing.T) {
	err := NewAPIError(404, "Not Found", errors.New("resource missing"))

	if !strings.Contains(err.Error(), "404") {
		t.Errorf("Expected status code in error, got: %s", err.Error())
	}

	if !strings.Contains(err.Error(), "Not Found") {
		t.Errorf("Expected message in error, got: %s", err.Error())
	}
}

func TestAPIErrorWithRequestID(t *testing.T) {
	err := NewAPIError(500, "Server Error", nil).WithRequestID("req-123")

	if !strings.Contains(err.Error(), "req-123") {
		t.Errorf("Expected request ID in error, got: %s", err.Error())
	}
}

func TestTemporaryError(t *testing.T) {
	err := Temporary(errors.New("network timeout"))

	if !IsTemporary(err) {
		t.Error("Expected error to be temporary")
	}

	// Test unwrapping
	unwrapped := errors.Unwrap(err)
	if unwrapped.Error() != "network timeout" {
		t.Errorf("Expected unwrapped error message 'network timeout', got: %s", unwrapped.Error())
	}
}

func TestPermanentError(t *testing.T) {
	err := Permanent(errors.New("invalid configuration"))

	if IsTemporary(err) {
		t.Error("Expected error to not be temporary")
	}
}

func TestIs(t *testing.T) {
	baseErr := errors.New("base error")
	wrappedErr := Wrap(baseErr, "wrapped")

	if !Is(wrappedErr, baseErr) {
		t.Error("Expected Is to find base error in chain")
	}

	if Is(wrappedErr, errors.New("different error")) {
		t.Error("Expected Is to not match different error")
	}
}

func TestAs(t *testing.T) {
	apiErr := NewAPIError(404, "Not Found", nil)
	wrappedErr := Wrap(apiErr, "API call failed")

	var target *APIError
	if !As(wrappedErr, &target) {
		t.Error("Expected As to find APIError in chain")
	}

	if target.StatusCode != 404 {
		t.Errorf("Expected status code 404, got %d", target.StatusCode)
	}
}

func TestWithValue(t *testing.T) {
	err := errors.New("base error")
	err = WithValue(err, "userID", "12345")
	err = WithValue(err, "operation", "delete")

	userID, ok := GetValue(err, "userID")
	if !ok {
		t.Fatal("Expected to find userID value")
	}
	if userID != "12345" {
		t.Errorf("Expected userID '12345', got '%v'", userID)
	}

	operation, ok := GetValue(err, "operation")
	if !ok {
		t.Fatal("Expected to find operation value")
	}
	if operation != "delete" {
		t.Errorf("Expected operation 'delete', got '%v'", operation)
	}

	_, ok = GetValue(err, "nonexistent")
	if ok {
		t.Error("Expected not to find nonexistent value")
	}
}

func TestContains(t *testing.T) {
	err := errors.New("database connection failed")

	if !Contains(err, "database") {
		t.Error("Expected Contains to find 'database' in error")
	}

	if Contains(err, "network") {
		t.Error("Expected Contains to not find 'network' in error")
	}

	if Contains(nil, "anything") {
		t.Error("Expected Contains to return false for nil error")
	}
}

func TestRecover(t *testing.T) {
	err := Recover(func() error {
		panic("something went wrong")
	})

	if err == nil {
		t.Fatal("Expected error from Recover")
	}

	if !strings.Contains(err.Error(), "panic recovered") {
		t.Errorf("Expected panic recovered message, got: %s", err.Error())
	}
}

func TestRecoverError(t *testing.T) {
	originalErr := errors.New("original error")
	err := Recover(func() error {
		panic(originalErr)
	})

	if err == nil {
		t.Fatal("Expected error from Recover")
	}

	// Should wrap the original error
	if !errors.Is(err, originalErr) {
		t.Error("Expected recovered error to wrap original error")
	}
}

func TestRecoverNoError(t *testing.T) {
	err := Recover(func() error {
		return errors.New("normal error")
	})

	if err == nil {
		t.Fatal("Expected error to be returned")
	}

	if !strings.Contains(err.Error(), "normal error") {
		t.Errorf("Expected normal error, got: %s", err.Error())
	}
}

func TestMust(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Error("Expected Must to panic on error")
		}
	}()

	Must(errors.New("test error"))
}

func TestMust1(t *testing.T) {
	// Test success case
	result := Must1(42, nil)
	if result != 42 {
		t.Errorf("Expected 42, got %d", result)
	}

	// Test error case
	defer func() {
		if r := recover(); r == nil {
			t.Error("Expected Must1 to panic on error")
		}
	}()

	Must1(0, errors.New("test error"))
}

func TestErrorFormat(t *testing.T) {
	err := New("test error")

	// Test simple format
	simple := fmt.Sprintf("%s", err)
	if !strings.Contains(simple, "test error") {
		t.Errorf("Expected simple format to contain error message, got: %s", simple)
	}

	// Test verbose format (with stack)
	verbose := fmt.Sprintf("%+v", err)
	if !strings.Contains(verbose, "test error") {
		t.Errorf("Expected verbose format to contain error message, got: %s", verbose)
	}

	// Verbose should be longer than simple (contains stack)
	if len(verbose) <= len(simple) {
		t.Error("Expected verbose format to be longer than simple format")
	}
}

func TestJoin(t *testing.T) {
	err1 := errors.New("error 1")
	err2 := errors.New("error 2")
	err3 := errors.New("error 3")

	joined := Join(err1, err2, err3)

	if joined == nil {
		t.Fatal("Expected joined error to be non-nil")
	}

	// All errors should be in the chain
	if !errors.Is(joined, err1) {
		t.Error("Expected joined error to contain err1")
	}
	if !errors.Is(joined, err2) {
		t.Error("Expected joined error to contain err2")
	}
	if !errors.Is(joined, err3) {
		t.Error("Expected joined error to contain err3")
	}
}

// Benchmarks

func BenchmarkNew(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = New("test error")
	}
}

func BenchmarkWrap(b *testing.B) {
	err := errors.New("base error")
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = Wrap(err, "wrapped")
	}
}

func BenchmarkErrorChain(b *testing.B) {
	err := New("base")
	for i := 0; i < 10; i++ {
		err = Wrap(err, fmt.Sprintf("level %d", i))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ErrorChain(err)
	}
}

func BenchmarkIs(b *testing.B) {
	base := errors.New("base")
	err := Wrap(Wrap(Wrap(base, "level 1"), "level 2"), "level 3")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = Is(err, base)
	}
}

func BenchmarkWithValue(b *testing.B) {
	err := errors.New("base error")
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = WithValue(err, "key", "value")
	}
}

func BenchmarkGetValue(b *testing.B) {
	err := errors.New("base")
	for i := 0; i < 5; i++ {
		err = WithValue(err, fmt.Sprintf("key%d", i), i)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = GetValue(err, "key2")
	}
}
