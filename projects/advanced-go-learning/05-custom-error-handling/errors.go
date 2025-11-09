package errors

import (
	"errors"
	"fmt"
	"io"
	"runtime"
	"strings"
)

// Sentinel errors
var (
	ErrNotFound      = errors.New("resource not found")
	ErrUnauthorized  = errors.New("unauthorized access")
	ErrInvalidInput  = errors.New("invalid input")
	ErrTimeout       = errors.New("operation timed out")
	ErrAlreadyExists = errors.New("resource already exists")
)

// ErrorWithStack wraps an error with a stack trace
type ErrorWithStack struct {
	Err   error
	msg   string
	Stack []uintptr
}

// New creates a new error with a stack trace
func New(message string) error {
	return &ErrorWithStack{
		Err:   errors.New(message),
		msg:   message,
		Stack: captureStackTrace(2),
	}
}

// Wrap wraps an error with additional context and stack trace
func Wrap(err error, message string) error {
	if err == nil {
		return nil
	}
	return &ErrorWithStack{
		Err:   err,
		msg:   message,
		Stack: captureStackTrace(2),
	}
}

// Wrapf wraps an error with a formatted message
func Wrapf(err error, format string, args ...interface{}) error {
	if err == nil {
		return nil
	}
	return &ErrorWithStack{
		Err:   err,
		msg:   fmt.Sprintf(format, args...),
		Stack: captureStackTrace(2),
	}
}

func (e *ErrorWithStack) Error() string {
	if e.msg != "" {
		return e.msg + ": " + e.Err.Error()
	}
	return e.Err.Error()
}

func (e *ErrorWithStack) Unwrap() error {
	return e.Err
}

// Format implements fmt.Formatter
func (e *ErrorWithStack) Format(s fmt.State, verb rune) {
	switch verb {
	case 'v':
		if s.Flag('+') {
			// Full format with stack trace
			fmt.Fprintf(s, "%s\n", e.Error())
			e.formatStack(s)
			return
		}
		fallthrough
	case 's':
		io.WriteString(s, e.Error())
	case 'q':
		fmt.Fprintf(s, "%q", e.Error())
	}
}

func (e *ErrorWithStack) formatStack(s fmt.State) {
	frames := runtime.CallersFrames(e.Stack)
	for {
		frame, more := frames.Next()
		if !strings.Contains(frame.File, "runtime/") {
			fmt.Fprintf(s, "  %s\n", frame.Function)
			fmt.Fprintf(s, "    %s:%d\n", frame.File, frame.Line)
		}
		if !more {
			break
		}
	}
}

// captureStackTrace captures the current stack trace
func captureStackTrace(skip int) []uintptr {
	const depth = 32
	var pcs [depth]uintptr
	n := runtime.Callers(skip, pcs[:])
	return pcs[0:n]
}

// ValidationError represents a validation error
type ValidationError struct {
	Field   string
	Message string
	Value   interface{}
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation failed on field '%s': %s (value: %v)",
		e.Field, e.Message, e.Value)
}

// NewValidationError creates a new validation error
func NewValidationError(field, message string, value interface{}) error {
	return &ValidationError{
		Field:   field,
		Message: message,
		Value:   value,
	}
}

// MultiError aggregates multiple errors
type MultiError struct {
	Errors []error
}

func (e *MultiError) Error() string {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("%d errors occurred:\n", len(e.Errors)))
	for i, err := range e.Errors {
		sb.WriteString(fmt.Sprintf("  %d. %s\n", i+1, err.Error()))
	}
	return sb.String()
}

// Add adds an error to the multi-error
func (e *MultiError) Add(err error) {
	if err != nil {
		e.Errors = append(e.Errors, err)
	}
}

// ErrorOrNil returns nil if no errors, otherwise returns the MultiError
func (e *MultiError) ErrorOrNil() error {
	if len(e.Errors) == 0 {
		return nil
	}
	return e
}

// NewMultiError creates a new MultiError
func NewMultiError() *MultiError {
	return &MultiError{
		Errors: make([]error, 0),
	}
}

// APIError represents an API-specific error
type APIError struct {
	StatusCode int
	Message    string
	Err        error
	RequestID  string
}

func (e *APIError) Error() string {
	if e.RequestID != "" {
		return fmt.Sprintf("API error %d: %s (request: %s)",
			e.StatusCode, e.Message, e.RequestID)
	}
	return fmt.Sprintf("API error %d: %s", e.StatusCode, e.Message)
}

func (e *APIError) Unwrap() error {
	return e.Err
}

// NewAPIError creates a new API error
func NewAPIError(statusCode int, message string, err error) *APIError {
	return &APIError{
		StatusCode: statusCode,
		Message:    message,
		Err:        err,
	}
}

// WithRequestID adds a request ID to the API error
func (e *APIError) WithRequestID(id string) *APIError {
	e.RequestID = id
	return e
}

// TemporaryError marks an error as temporary/retryable
type TemporaryError struct {
	Err error
}

func (e *TemporaryError) Error() string {
	return e.Err.Error()
}

func (e *TemporaryError) Unwrap() error {
	return e.Err
}

func (e *TemporaryError) Temporary() bool {
	return true
}

// IsTemporary checks if an error is temporary
func IsTemporary(err error) bool {
	type temporary interface {
		Temporary() bool
	}
	te, ok := err.(temporary)
	return ok && te.Temporary()
}

// Temporary wraps an error as temporary
func Temporary(err error) error {
	if err == nil {
		return nil
	}
	return &TemporaryError{Err: err}
}

// PermanentError marks an error as permanent/non-retryable
type PermanentError struct {
	Err error
}

func (e *PermanentError) Error() string {
	return e.Err.Error()
}

func (e *PermanentError) Unwrap() error {
	return e.Err
}

// Permanent wraps an error as permanent
func Permanent(err error) error {
	if err == nil {
		return nil
	}
	return &PermanentError{Err: err}
}

// Is reports whether any error in err's chain matches target
func Is(err, target error) bool {
	return errors.Is(err, target)
}

// As finds the first error in err's chain that matches target
func As(err error, target interface{}) bool {
	return errors.As(err, target)
}

// Cause returns the root cause of an error
func Cause(err error) error {
	type causer interface {
		Cause() error
	}

	for err != nil {
		cause, ok := err.(causer)
		if !ok {
			break
		}
		err = cause.Cause()
	}
	return err
}

// ErrorChain returns all errors in the error chain
func ErrorChain(err error) []error {
	var chain []error
	for err != nil {
		chain = append(chain, err)
		err = errors.Unwrap(err)
	}
	return chain
}

// Join combines multiple errors into a single error
func Join(errs ...error) error {
	return errors.Join(errs...)
}

// Must panics if err is not nil
func Must(err error) {
	if err != nil {
		panic(err)
	}
}

// Must1 returns the value if err is nil, otherwise panics
func Must1[T any](val T, err error) T {
	if err != nil {
		panic(err)
	}
	return val
}

// Recover recovers from a panic and converts it to an error
func Recover(fn func() error) (err error) {
	defer func() {
		if r := recover(); r != nil {
			switch v := r.(type) {
			case error:
				err = Wrap(v, "panic recovered")
			default:
				err = New(fmt.Sprintf("panic recovered: %v", r))
			}
		}
	}()
	return fn()
}

// WithValue adds a key-value pair to an error
type ErrorWithValue struct {
	Err   error
	Key   string
	Value interface{}
}

func (e *ErrorWithValue) Error() string {
	return e.Err.Error()
}

func (e *ErrorWithValue) Unwrap() error {
	return e.Err
}

// WithValue attaches a key-value pair to an error
func WithValue(err error, key string, value interface{}) error {
	if err == nil {
		return nil
	}
	return &ErrorWithValue{
		Err:   err,
		Key:   key,
		Value: value,
	}
}

// GetValue retrieves a value from an error chain
func GetValue(err error, key string) (interface{}, bool) {
	for err != nil {
		if ev, ok := err.(*ErrorWithValue); ok && ev.Key == key {
			return ev.Value, true
		}
		err = errors.Unwrap(err)
	}
	return nil, false
}

// Contains checks if an error message contains a substring
func Contains(err error, substr string) bool {
	if err == nil {
		return false
	}
	return strings.Contains(err.Error(), substr)
}
