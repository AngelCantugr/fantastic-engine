package middleware

import (
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

func TestChain(t *testing.T) {
	called := []string{}

	m1 := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			called = append(called, "m1-before")
			next.ServeHTTP(w, r)
			called = append(called, "m1-after")
		})
	}

	m2 := func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			called = append(called, "m2-before")
			next.ServeHTTP(w, r)
			called = append(called, "m2-after")
		})
	}

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		called = append(called, "handler")
	})

	chain := Chain(m1, m2)
	req := httptest.NewRequest("GET", "/", nil)
	rec := httptest.NewRecorder()

	chain(handler).ServeHTTP(rec, req)

	expected := []string{"m1-before", "m2-before", "handler", "m2-after", "m1-after"}
	if len(called) != len(expected) {
		t.Fatalf("Expected %d calls, got %d", len(expected), len(called))
	}

	for i, call := range called {
		if call != expected[i] {
			t.Errorf("At index %d, expected %s, got %s", i, expected[i], call)
		}
	}
}

func TestRequestID(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := r.Context().Value("requestID")
		if requestID == nil {
			t.Error("Request ID not found in context")
		}
	})

	req := httptest.NewRequest("GET", "/", nil)
	rec := httptest.NewRecorder()

	RequestID()(handler).ServeHTTP(rec, req)

	if rec.Header().Get("X-Request-ID") == "" {
		t.Error("X-Request-ID header not set")
	}
}

func TestRecovery(t *testing.T) {
	logger := log.New(os.Stdout, "", log.LstdFlags)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		panic("test panic")
	})

	req := httptest.NewRequest("GET", "/", nil)
	rec := httptest.NewRecorder()

	Recovery(logger)(handler).ServeHTTP(rec, req)

	if rec.Code != http.StatusInternalServerError {
		t.Errorf("Expected status 500, got %d", rec.Code)
	}
}

func TestBasicAuth(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	middleware := BasicAuth("user", "pass")

	// Test with valid credentials
	req := httptest.NewRequest("GET", "/", nil)
	req.SetBasicAuth("user", "pass")
	rec := httptest.NewRecorder()

	middleware(handler).ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", rec.Code)
	}

	// Test with invalid credentials
	req = httptest.NewRequest("GET", "/", nil)
	req.SetBasicAuth("user", "wrong")
	rec = httptest.NewRecorder()

	middleware(handler).ServeHTTP(rec, req)

	if rec.Code != http.StatusUnauthorized {
		t.Errorf("Expected status 401, got %d", rec.Code)
	}
}

func TestCORS(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	middleware := CORS([]string{"http://example.com"})

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Set("Origin", "http://example.com")
	rec := httptest.NewRecorder()

	middleware(handler).ServeHTTP(rec, req)

	if rec.Header().Get("Access-Control-Allow-Origin") != "http://example.com" {
		t.Error("CORS header not set correctly")
	}
}

func TestRateLimiter(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	rl := NewRateLimiter(2, time.Second)
	middleware := rl.Middleware()

	// First request should succeed
	req := httptest.NewRequest("GET", "/", nil)
	rec := httptest.NewRecorder()
	middleware(handler).ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", rec.Code)
	}

	// Second request should succeed
	req = httptest.NewRequest("GET", "/", nil)
	rec = httptest.NewRecorder()
	middleware(handler).ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", rec.Code)
	}

	// Third request should be rate limited
	req = httptest.NewRequest("GET", "/", nil)
	rec = httptest.NewRecorder()
	middleware(handler).ServeHTTP(rec, req)
	if rec.Code != http.StatusTooManyRequests {
		t.Errorf("Expected status 429, got %d", rec.Code)
	}
}

func BenchmarkMiddlewareChain(b *testing.B) {
	logger := log.New(os.Stdout, "", log.LstdFlags)
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {})

	chain := Chain(
		RequestID(),
		Logger(logger),
		Recovery(logger),
	)

	wrapped := chain(handler)
	req := httptest.NewRequest("GET", "/", nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rec := httptest.NewRecorder()
		wrapped.ServeHTTP(rec, req)
	}
}
