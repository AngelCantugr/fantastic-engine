package ratelimiter

import (
	"sync"
	"time"
)

// TokenBucket implements token bucket algorithm
type TokenBucket struct {
	capacity      int
	tokens        int
	refillRate    int
	refillPeriod  time.Duration
	lastRefill    time.Time
	mu            sync.Mutex
}

func NewTokenBucket(capacity, refillRate int, refillPeriod time.Duration) *TokenBucket {
	return &TokenBucket{
		capacity:     capacity,
		tokens:       capacity,
		refillRate:   refillRate,
		refillPeriod: refillPeriod,
		lastRefill:   time.Now(),
	}
}

func (tb *TokenBucket) Allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()

	if tb.tokens > 0 {
		tb.tokens--
		return true
	}
	return false
}

func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastRefill)
	periods := int(elapsed / tb.refillPeriod)

	if periods > 0 {
		tokensToAdd := periods * tb.refillRate
		tb.tokens = min(tb.capacity, tb.tokens+tokensToAdd)
		tb.lastRefill = now
	}
}

// LeakyBucket implements leaky bucket algorithm
type LeakyBucket struct {
	capacity     int
	leakRate     int
	leakPeriod   time.Duration
	queue        []time.Time
	mu           sync.Mutex
}

func NewLeakyBucket(capacity, leakRate int, leakPeriod time.Duration) *LeakyBucket {
	lb := &LeakyBucket{
		capacity:   capacity,
		leakRate:   leakRate,
		leakPeriod: leakPeriod,
		queue:      make([]time.Time, 0, capacity),
	}
	go lb.leak()
	return lb
}

func (lb *LeakyBucket) Allow() bool {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if len(lb.queue) < lb.capacity {
		lb.queue = append(lb.queue, time.Now())
		return true
	}
	return false
}

func (lb *LeakyBucket) leak() {
	ticker := time.NewTicker(lb.leakPeriod)
	defer ticker.Stop()

	for range ticker.C {
		lb.mu.Lock()
		if len(lb.queue) > 0 {
			toRemove := min(lb.leakRate, len(lb.queue))
			lb.queue = lb.queue[toRemove:]
		}
		lb.mu.Unlock()
	}
}

// SlidingWindow implements sliding window counter
type SlidingWindow struct {
	maxRequests  int
	windowSize   time.Duration
	requests     []time.Time
	mu           sync.Mutex
}

func NewSlidingWindow(maxRequests int, windowSize time.Duration) *SlidingWindow {
	return &SlidingWindow{
		maxRequests: maxRequests,
		windowSize:  windowSize,
		requests:    make([]time.Time, 0),
	}
}

func (sw *SlidingWindow) Allow() bool {
	sw.mu.Lock()
	defer sw.mu.Unlock()

	now := time.Now()
	cutoff := now.Add(-sw.windowSize)

	// Remove old requests
	valid := make([]time.Time, 0)
	for _, req := range sw.requests {
		if req.After(cutoff) {
			valid = append(valid, req)
		}
	}
	sw.requests = valid

	if len(sw.requests) < sw.maxRequests {
		sw.requests = append(sw.requests, now)
		return true
	}
	return false
}

// FixedWindow implements fixed window counter
type FixedWindow struct {
	maxRequests  int
	windowSize   time.Duration
	currentCount int
	windowStart  time.Time
	mu           sync.Mutex
}

func NewFixedWindow(maxRequests int, windowSize time.Duration) *FixedWindow {
	return &FixedWindow{
		maxRequests: maxRequests,
		windowSize:  windowSize,
		windowStart: time.Now(),
	}
}

func (fw *FixedWindow) Allow() bool {
	fw.mu.Lock()
	defer fw.mu.Unlock()

	now := time.Now()
	if now.Sub(fw.windowStart) >= fw.windowSize {
		fw.currentCount = 0
		fw.windowStart = now
	}

	if fw.currentCount < fw.maxRequests {
		fw.currentCount++
		return true
	}
	return false
}

// PerUserRateLimiter manages rate limits per user
type PerUserRateLimiter struct {
	limiters map[string]*TokenBucket
	capacity int
	rate     int
	period   time.Duration
	mu       sync.RWMutex
}

func NewPerUserRateLimiter(capacity, rate int, period time.Duration) *PerUserRateLimiter {
	return &PerUserRateLimiter{
		limiters: make(map[string]*TokenBucket),
		capacity: capacity,
		rate:     rate,
		period:   period,
	}
}

func (pul *PerUserRateLimiter) Allow(userID string) bool {
	pul.mu.RLock()
	limiter, exists := pul.limiters[userID]
	pul.mu.RUnlock()

	if !exists {
		pul.mu.Lock()
		limiter = NewTokenBucket(pul.capacity, pul.rate, pul.period)
		pul.limiters[userID] = limiter
		pul.mu.Unlock()
	}

	return limiter.Allow()
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
