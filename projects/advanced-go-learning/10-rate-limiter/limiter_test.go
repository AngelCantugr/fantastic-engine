package ratelimiter

import (
	"testing"
	"time"
)

func TestTokenBucket(t *testing.T) {
	tb := NewTokenBucket(5, 1, 100*time.Millisecond)

	// Should allow 5 requests immediately
	for i := 0; i < 5; i++ {
		if !tb.Allow() {
			t.Errorf("Request %d should be allowed", i)
		}
	}

	// 6th request should be denied
	if tb.Allow() {
		t.Error("6th request should be denied")
	}

	// Wait for refill
	time.Sleep(150 * time.Millisecond)

	// Should allow one more request
	if !tb.Allow() {
		t.Error("Request after refill should be allowed")
	}
}

func TestLeakyBucket(t *testing.T) {
	lb := NewLeakyBucket(3, 1, 100*time.Millisecond)
	defer time.Sleep(200 * time.Millisecond) // cleanup

	// Should allow 3 requests
	for i := 0; i < 3; i++ {
		if !lb.Allow() {
			t.Errorf("Request %d should be allowed", i)
		}
	}

	// 4th request should be denied
	if lb.Allow() {
		t.Error("4th request should be denied")
	}

	// Wait for leak
	time.Sleep(150 * time.Millisecond)

	// Should allow one more request
	if !lb.Allow() {
		t.Error("Request after leak should be allowed")
	}
}

func TestSlidingWindow(t *testing.T) {
	sw := NewSlidingWindow(3, 200*time.Millisecond)

	// Allow 3 requests
	for i := 0; i < 3; i++ {
		if !sw.Allow() {
			t.Errorf("Request %d should be allowed", i)
		}
	}

	// 4th should be denied
	if sw.Allow() {
		t.Error("4th request should be denied")
	}

	// Wait for window to slide
	time.Sleep(250 * time.Millisecond)

	// Should allow 3 more requests
	for i := 0; i < 3; i++ {
		if !sw.Allow() {
			t.Errorf("Request %d after window should be allowed", i)
		}
	}
}

func TestFixedWindow(t *testing.T) {
	fw := NewFixedWindow(3, 200*time.Millisecond)

	// Allow 3 requests
	for i := 0; i < 3; i++ {
		if !fw.Allow() {
			t.Errorf("Request %d should be allowed", i)
		}
	}

	// 4th should be denied
	if fw.Allow() {
		t.Error("4th request should be denied")
	}

	// Wait for new window
	time.Sleep(250 * time.Millisecond)

	// Should allow requests in new window
	if !fw.Allow() {
		t.Error("Request in new window should be allowed")
	}
}

func TestPerUserRateLimiter(t *testing.T) {
	pul := NewPerUserRateLimiter(2, 1, 100*time.Millisecond)

	// User A: allow 2 requests
	if !pul.Allow("userA") {
		t.Error("First request for userA should be allowed")
	}
	if !pul.Allow("userA") {
		t.Error("Second request for userA should be allowed")
	}
	if pul.Allow("userA") {
		t.Error("Third request for userA should be denied")
	}

	// User B: independent limit
	if !pul.Allow("userB") {
		t.Error("First request for userB should be allowed")
	}
}

func BenchmarkTokenBucket(b *testing.B) {
	tb := NewTokenBucket(1000, 100, time.Millisecond)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tb.Allow()
	}
}

func BenchmarkSlidingWindow(b *testing.B) {
	sw := NewSlidingWindow(1000, time.Second)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		sw.Allow()
	}
}
