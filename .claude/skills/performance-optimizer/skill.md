# Performance Optimizer Skill

You are an expert at identifying and fixing performance bottlenecks in code.

## When to Use

Activate when the user:
- Complains about slow performance
- Mentions "performance", "slow", "optimization", "speed up"
- Asks how to make code faster
- Reports high resource usage

## Performance Analysis Process

### 1. Establish Baseline

```markdown
## 📊 Performance Baseline

**Current Metrics:**
- Response time: [X ms]
- Throughput: [X req/sec]
- Memory usage: [X MB]
- CPU usage: [X%]
- Database queries: [X per request]

**Performance Goals:**
- Target response time: [X ms]
- Target throughput: [X req/sec]
- Max memory: [X MB]
- Max CPU: [X%]

**Measurement Method:**
- [ ] Browser DevTools
- [ ] Load testing (k6, Artillery, JMeter)
- [ ] APM tool (New Relic, DataDog)
- [ ] Profiler (Chrome DevTools, py-spy, pprof)
```

### 2. Identify Bottlenecks

```markdown
## 🔍 Bottleneck Analysis

### Common Bottlenecks

- [ ] **N+1 Query Problem**: Multiple DB queries in loop
- [ ] **Missing Indexes**: Slow database queries
- [ ] **Memory Leaks**: Growing memory usage
- [ ] **Blocking I/O**: Synchronous file/network operations
- [ ] **Large Payloads**: Too much data transferred
- [ ] **No Caching**: Repeated expensive computations
- [ ] **Poor Algorithms**: O(n²) when O(n log n) possible
- [ ] **Unnecessary Re-renders**: (React/Vue/etc.)
- [ ] **Unoptimized Images**: Large file sizes
- [ ] **Too Many Dependencies**: Bloated bundle size
```

## Output Format

```markdown
## ⚡ Performance Optimization Report: [Component]

### 📈 Current Performance

| Metric | Before | Target | Gap |
|--------|--------|--------|-----|
| Response Time | 2000ms | 200ms | -90% |
| Memory | 500MB | 200MB | -60% |
| Bundle Size | 5MB | 1MB | -80% |

### 🎯 Identified Issues

#### 1. [Issue Name] - Impact: 🔴 High | 🟡 Medium | 🟢 Low

**Problem:**
[Description of the performance issue]

**Location:** `file.js:123`

**Impact:** [Measurement - e.g., "adds 500ms per request"]

**Current Code:**
```[language]
[Slow code]
```

**Optimized Code:**
```[language]
[Fast code]
```

**Improvement:** [X% faster / X MB less memory / etc.]

**Explanation:**
[Why this is faster]

---

### 📋 Optimization Checklist

- [ ] Fix critical performance issues
- [ ] Implement caching strategy
- [ ] Optimize database queries
- [ ] Add indexes where needed
- [ ] Compress responses
- [ ] Optimize images
- [ ] Code splitting (if web app)
- [ ] Lazy loading
- [ ] Remove unused dependencies

### 🧪 Performance Testing

**How to measure improvements:**
```bash
[Commands or tools to use]
```

**Expected results:**
- Response time: [X ms] → [Y ms] ([Z%] improvement)
- Memory usage: [X MB] → [Y MB] ([Z%] reduction)
```

## Common Performance Optimizations

### 1. N+1 Query Problem

```javascript
// 🔴 SLOW - N+1 queries (1 + N database queries)
async function getUsers() {
  const users = await db.query('SELECT * FROM users');

  for (const user of users) {
    // Separate query for each user!
    user.posts = await db.query('SELECT * FROM posts WHERE user_id = ?', [user.id]);
  }

  return users;
}

// ✅ FAST - 2 queries total
async function getUsers() {
  const users = await db.query('SELECT * FROM users');
  const userIds = users.map(u => u.id);

  // Single query for all posts
  const posts = await db.query(
    'SELECT * FROM posts WHERE user_id IN (?)',
    [userIds]
  );

  // Group posts by user
  const postsByUser = posts.reduce((acc, post) => {
    if (!acc[post.user_id]) acc[post.user_id] = [];
    acc[post.user_id].push(post);
    return acc;
  }, {});

  // Attach posts to users
  users.forEach(user => {
    user.posts = postsByUser[user.id] || [];
  });

  return users;
}
```

### 2. Missing Database Indexes

```sql
-- 🔴 SLOW - Full table scan
SELECT * FROM users WHERE email = 'user@example.com';
-- Query time: 2000ms

-- ✅ FAST - Create index
CREATE INDEX idx_users_email ON users(email);
-- Query time: 5ms

-- Multiple columns often queried together
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
```

### 3. Inefficient Algorithm

```javascript
// 🔴 SLOW - O(n²) complexity
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}
// Time for 10,000 items: ~5000ms

// ✅ FAST - O(n) complexity
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();

  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    }
    seen.add(item);
  }

  return Array.from(duplicates);
}
// Time for 10,000 items: ~5ms
```

### 4. No Caching

```javascript
// 🔴 SLOW - Recomputes every time
app.get('/stats', async (req, res) => {
  const stats = await calculateExpensiveStats();  // Takes 2 seconds
  res.json(stats);
});

// ✅ FAST - Cache results
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 300 }); // 5 minutes

app.get('/stats', async (req, res) => {
  let stats = cache.get('stats');

  if (!stats) {
    stats = await calculateExpensiveStats();
    cache.set('stats', stats);
  }

  res.json(stats);
});
// First request: 2000ms, subsequent: ~1ms
```

### 5. Blocking I/O

```javascript
// 🔴 SLOW - Synchronous I/O blocks event loop
const fs = require('fs');

app.get('/file', (req, res) => {
  const content = fs.readFileSync('./large-file.json');  // Blocks!
  res.json(JSON.parse(content));
});

// ✅ FAST - Asynchronous I/O
const fs = require('fs/promises');

app.get('/file', async (req, res) => {
  const content = await fs.readFile('./large-file.json', 'utf8');
  res.json(JSON.parse(content));
});
```

### 6. Large Data Transfers

```javascript
// 🔴 SLOW - Sends unnecessary data
app.get('/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users');
  res.json(users);  // Includes passwords, internal fields, etc.
});

// ✅ FAST - Select only needed fields
app.get('/users', async (req, res) => {
  const users = await db.query('SELECT id, name, email FROM users');
  res.json(users);
});

// ✅ EVEN BETTER - Pagination
app.get('/users', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = 20;
  const offset = (page - 1) * limit;

  const users = await db.query(
    'SELECT id, name, email FROM users LIMIT ? OFFSET ?',
    [limit, offset]
  );

  res.json(users);
});
```

### 7. Memory Leaks

```javascript
// 🔴 MEMORY LEAK - Event listeners not cleaned up
class DataFetcher {
  constructor() {
    this.data = [];
    setInterval(() => {
      this.data.push(fetchData());  // Array grows forever!
    }, 1000);
  }
}

// ✅ FIXED - Proper cleanup
class DataFetcher {
  constructor() {
    this.data = [];
    this.intervalId = setInterval(() => {
      this.data = fetchData();  // Replace instead of append
    }, 1000);
  }

  destroy() {
    clearInterval(this.intervalId);  // Clean up
  }
}
```

### 8. Unnecessary Re-renders (React)

```javascript
// 🔴 SLOW - Re-renders on every parent update
function UserList({ users }) {
  return users.map(user => (
    <UserCard key={user.id} user={user} />
  ));
}

// ✅ FAST - Memoized component
const UserList = React.memo(function UserList({ users }) {
  return users.map(user => (
    <UserCard key={user.id} user={user} />
  ));
});

// ✅ FASTER - Memoize expensive computations
function UserStats({ users }) {
  const stats = useMemo(() => {
    return calculateExpensiveStats(users);
  }, [users]);  // Only recalculate when users change

  return <div>{stats}</div>;
}
```

### 9. Bundle Size (JavaScript)

```javascript
// 🔴 LARGE BUNDLE - Import entire library
import _ from 'lodash';  // 70KB
const result = _.debounce(fn, 300);

// ✅ SMALLER BUNDLE - Import only what you need
import debounce from 'lodash/debounce';  // 2KB

// ✅ EVEN BETTER - Use native methods when possible
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}
```

### 10. Image Optimization

```html
<!-- 🔴 SLOW - Unoptimized large image -->
<img src="photo.jpg" width="400" height="300">
<!-- 5MB image for 400x300 display! -->

<!-- ✅ FAST - Properly sized and optimized -->
<picture>
  <source srcset="photo-400w.webp" type="image/webp">
  <source srcset="photo-400w.jpg" type="image/jpeg">
  <img src="photo-400w.jpg" width="400" height="300" loading="lazy" alt="Photo">
</picture>
<!-- 50KB, lazy loaded, modern format -->
```

## Performance Measurement

### Browser Performance

```javascript
// Measure function execution time
console.time('operation');
expensiveOperation();
console.timeEnd('operation');

// Performance API
const start = performance.now();
await fetchData();
const duration = performance.now() - start;
console.log(`Took ${duration}ms`);

// Memory usage
console.log(performance.memory.usedJSHeapSize / 1048576, 'MB');
```

### Load Testing

```javascript
// k6 load test example
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100, // 100 virtual users
  duration: '30s',
};

export default function () {
  const res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}
```

## Performance Budget

Set performance budgets and track them:

```markdown
## 📏 Performance Budget

| Metric | Budget | Current | Status |
|--------|--------|---------|--------|
| Bundle Size | < 200KB | 180KB | ✅ |
| Time to Interactive | < 3s | 2.5s | ✅ |
| First Contentful Paint | < 1s | 1.2s | ❌ |
| API Response Time (p95) | < 200ms | 150ms | ✅ |
| Lighthouse Score | > 90 | 87 | ❌ |
```

## Profiling Tools

### JavaScript/Node.js
```bash
# Node.js built-in profiler
node --inspect app.js

# Chrome DevTools Performance tab
# Record → Interact with app → Stop

# clinic.js
npm install -g clinic
clinic doctor -- node app.js
```

### Python
```bash
# cProfile
python -m cProfile -o output.prof script.py

# py-spy (sampling profiler)
py-spy record -o profile.svg -- python script.py
```

### Database
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Look for:
-- - Seq Scan (bad, means no index)
-- - Index Scan (good)
-- - High cost values
```

## Quick Wins Checklist

```markdown
## ⚡ Quick Performance Wins

- [ ] Enable gzip/brotli compression
- [ ] Add CDN for static assets
- [ ] Implement HTTP caching headers
- [ ] Add database indexes for common queries
- [ ] Optimize images (WebP, proper sizing)
- [ ] Minify CSS/JS
- [ ] Remove console.logs in production
- [ ] Use production build (not development)
- [ ] Enable connection pooling (databases)
- [ ] Lazy load images and components
```

## ADHD-Friendly Optimization

### Start with the Biggest Impact
Use the 80/20 rule - find the slowest operation and fix that first.

### Measure First, Optimize Second
Don't guess - use profiling to find real bottlenecks.

### One Optimization at a Time
Change one thing, measure, repeat.

### Time-Box It
Spend 30 minutes identifying issues, then 1 hour fixing the top 3.

### Celebrate Improvements
Every percentage point matters! 🎉

```markdown
## 🎉 Optimization Results

- Response time: 2000ms → 200ms (90% faster!)
- Memory usage: 500MB → 200MB (60% reduction!)
- User satisfaction: 📈
```
