# 🔗 URL Shortener - Scalable URL Shortening Service

**Status:** 🧪 Experimental

**Tech Stack:**
- **Backend:** Python 3.11+ / FastAPI
- **Database:** PostgreSQL 15+ (with replication)
- **Cache:** Redis 7+
- **Containerization:** Docker & Docker Compose
- **Monitoring:** Prometheus + Grafana (optional)

**Performance Requirements:**
- ✅ Handle 1000 requests/second
- ✅ Response latency < 100ms
- ✅ 99.9% uptime
- ✅ Horizontal scalability

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Scalability Considerations](#scalability-considerations)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Performance Testing](#performance-testing)
- [Deployment](#deployment)
- [Graduation Criteria](#graduation-criteria)

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Client] -->|HTTP Request| B[Load Balancer]
    B --> C[FastAPI Instance 1]
    B --> D[FastAPI Instance 2]
    B --> E[FastAPI Instance N]

    C --> F[Redis Cache]
    D --> F
    E --> F

    F -->|Cache Miss| G[PostgreSQL Primary]
    G -->|Replication| H[PostgreSQL Replica 1]
    G -->|Replication| I[PostgreSQL Replica 2]

    C --> J[Metrics Exporter]
    D --> J
    E --> J
    J --> K[Prometheus]
    K --> L[Grafana Dashboard]

    style A fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style F fill:#ff6b6b,stroke:#00ffff,stroke-width:2px
    style G fill:#4ecdc4,stroke:#00ffff,stroke-width:2px
    style K fill:#ffe66d,stroke:#00ffff,stroke-width:2px
```

### System Components

1. **FastAPI Application** - High-performance async web framework
2. **PostgreSQL** - Durable storage with replication for read scaling
3. **Redis** - In-memory cache for hot URLs (80/20 rule)
4. **Connection Pooling** - Efficient database connection management
5. **Load Balancer** - Distribute traffic across multiple instances

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant PostgreSQL

    Client->>API: GET /{short_code}
    API->>Redis: Check cache
    alt Cache Hit
        Redis-->>API: Return URL
        API-->>Client: 301 Redirect
    else Cache Miss
        API->>PostgreSQL: Query URL
        PostgreSQL-->>API: Return URL
        API->>Redis: Store in cache
        API-->>Client: 301 Redirect
    end

    Note over API,Redis: Cache TTL: 24 hours
    Note over API,PostgreSQL: Connection pool: 20 connections
```

---

## 📊 Database Schema

```mermaid
erDiagram
    URLS ||--o{ URL_ANALYTICS : tracks

    URLS {
        bigserial id PK
        varchar short_code UK "6-character unique code"
        text original_url "Original long URL"
        timestamp created_at "Creation timestamp"
        timestamp expires_at "Expiration timestamp (nullable)"
        integer click_count "Total clicks"
        boolean is_active "Active status"
        varchar created_by "User ID (for future auth)"
    }

    URL_ANALYTICS {
        bigserial id PK
        bigint url_id FK
        timestamp clicked_at "Click timestamp"
        varchar ip_address "Client IP (hashed)"
        varchar user_agent "User agent string"
        varchar referer "HTTP referer"
        varchar country "GeoIP country"
    }
```

### Indexes for Performance

```sql
-- Primary key index (automatic)
CREATE INDEX idx_urls_short_code ON urls(short_code);

-- Compound index for active URL lookups
CREATE INDEX idx_urls_active_code ON urls(short_code, is_active) WHERE is_active = true;

-- Index for expiration cleanup
CREATE INDEX idx_urls_expires_at ON urls(expires_at) WHERE expires_at IS NOT NULL;

-- Analytics query optimization
CREATE INDEX idx_analytics_url_id_time ON url_analytics(url_id, clicked_at DESC);
```

---

## 🔌 API Endpoints

### 1. Create Short URL

**Endpoint:** `POST /api/shorten`

**Request:**
```json
{
  "url": "https://www.example.com/very/long/path/to/resource",
  "custom_code": "mycode",
  "expires_in_days": 30
}
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/mycode",
  "short_code": "mycode",
  "original_url": "https://www.example.com/very/long/path/to/resource",
  "created_at": "2025-11-16T10:30:00Z",
  "expires_at": "2025-12-16T10:30:00Z"
}
```

**Status Codes:**
- `201 Created` - URL shortened successfully
- `400 Bad Request` - Invalid URL or custom code already exists
- `422 Unprocessable Entity` - Validation error

---

### 2. Redirect to Original URL

**Endpoint:** `GET /{short_code}`

**Response:**
- `301 Moved Permanently` - Redirects to original URL
- `404 Not Found` - Short code doesn't exist or expired
- `410 Gone` - URL has been deactivated

**Headers:**
```
Location: https://www.example.com/very/long/path/to/resource
Cache-Control: public, max-age=300
```

---

### 3. Get URL Statistics

**Endpoint:** `GET /api/stats/{short_code}`

**Response:**
```json
{
  "short_code": "mycode",
  "original_url": "https://www.example.com/very/long/path/to/resource",
  "total_clicks": 1547,
  "created_at": "2025-11-16T10:30:00Z",
  "last_clicked_at": "2025-11-16T15:45:22Z",
  "is_active": true,
  "clicks_by_day": [
    {"date": "2025-11-16", "clicks": 234},
    {"date": "2025-11-15", "clicks": 456}
  ]
}
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "timestamp": "2025-11-16T10:30:00Z"
}
```

---

## 🚀 Scalability Considerations

### 1. Short Code Generation Strategy

**Base62 Encoding** (a-z, A-Z, 0-9):
- 6 characters = 62^6 = ~56.8 billion possible URLs
- Collision probability extremely low

**Generation Algorithm:**
```python
import secrets
import string

BASE62 = string.ascii_letters + string.digits

def generate_short_code(length=6):
    """Generate cryptographically secure random short code"""
    return ''.join(secrets.choice(BASE62) for _ in range(length))
```

**Collision Handling:**
- Unique constraint on `short_code` column
- Retry with new code on conflict (< 0.001% probability)
- Custom codes validated for availability

---

### 2. Caching Strategy

**Cache Invalidation:**
```python
# Write-through cache on creation
await redis.setex(f"url:{short_code}", 86400, original_url)

# Cache warming for popular URLs
# Top 20% of URLs account for 80% of traffic
```

**Cache Hit Ratio Target:** > 90%

**Redis Configuration:**
- `maxmemory-policy: allkeys-lru` (Least Recently Used eviction)
- `maxmemory: 2gb` (adjust based on traffic)

---

### 3. Database Optimization

**Connection Pooling:**
```python
DATABASE_URL = "postgresql://user:pass@localhost/urlshortener"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Base connections
    max_overflow=10,       # Additional connections under load
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600      # Recycle connections every hour
)
```

**Read Replicas:**
- Write operations → Primary database
- Read operations (stats, analytics) → Replicas
- Horizontal read scaling

**Partitioning Strategy (Future):**
```sql
-- Partition by creation date for analytics
CREATE TABLE url_analytics_2025_11 PARTITION OF url_analytics
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

---

### 4. Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Per-IP rate limiting
@app.post("/api/shorten", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def shorten_url(...):
    pass
```

**Limits:**
- Anonymous: 10 requests/minute
- Authenticated (future): 100 requests/minute

---

### 5. Horizontal Scaling

**Stateless Application Design:**
- No in-memory session storage
- All state in PostgreSQL/Redis
- Can run N instances behind load balancer

**Docker Compose Scaling:**
```bash
docker-compose up --scale api=3
```

---

## ⚙️ Environment Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

### Installation Steps

1. **Clone and Navigate:**
```bash
cd /home/user/fantastic-engine/projects/url-shortener
```

2. **Create Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start Dependencies:**
```bash
docker-compose up -d postgres redis
```

6. **Initialize Database:**
```bash
python -m app.db.init_db
```

---

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

### Production Mode (Docker Compose)

```bash
docker-compose up -d
```

**Services:**
- `api` - FastAPI application (3 replicas)
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `nginx` - Load balancer (optional)

---

## 🧪 Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def redirect(self):
        # Simulate URL redirects (most common operation)
        self.client.get("/abc123", allow_redirects=False)

    @task(1)
    def shorten(self):
        self.client.post("/api/shorten", json={
            "url": "https://example.com/test"
        })
```

**Run Load Test:**
```bash
locust --host=http://localhost:8000 --users 1000 --spawn-rate 50
```

**Performance Targets:**
- ✅ 1000 req/sec sustained
- ✅ p95 latency < 100ms
- ✅ p99 latency < 200ms
- ✅ Error rate < 0.1%

---

### Database Performance Testing

```sql
-- Explain query plans
EXPLAIN ANALYZE SELECT original_url FROM urls
WHERE short_code = 'abc123' AND is_active = true;

-- Expected: Index Scan, execution time < 5ms
```

---

## 🚢 Deployment

### Docker Image Build

```bash
docker build -t url-shortener:latest .
```

### Deployment Options

1. **Cloud VM** (DigitalOcean, AWS EC2, GCP Compute)
2. **Container Platform** (AWS ECS, Google Cloud Run, Azure Container Apps)
3. **Kubernetes** (for large-scale deployments)

### Environment Variables

```bash
# Production settings
DATABASE_URL=postgresql://user:pass@db.example.com/urlshortener
REDIS_URL=redis://cache.example.com:6379/0
BASE_URL=https://short.example.com
ALLOWED_ORIGINS=https://example.com,https://app.example.com
```

---

## 🎓 Graduation Criteria

**This project is ready to graduate when:**

### ✅ Functionality
- [x] Short URL creation with custom codes
- [x] Redirect functionality with caching
- [x] URL expiration support
- [x] Click tracking and analytics
- [x] Health check endpoint

### ✅ Performance
- [ ] Load tested at 1000 req/sec
- [ ] p95 latency < 100ms verified
- [ ] Cache hit ratio > 90%
- [ ] Database query optimization confirmed

### ✅ Production Readiness
- [ ] Comprehensive error handling
- [ ] Logging and monitoring setup
- [ ] Database backups configured
- [ ] Security headers implemented
- [ ] Rate limiting active
- [ ] CORS properly configured

### ✅ Documentation
- [x] Architecture diagrams
- [x] API documentation
- [x] Setup instructions
- [x] Deployment guide

### ✅ Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Load tests passing
- [ ] Security audit completed

### ✅ Deployment
- [ ] Deployed to production environment
- [ ] Monitoring dashboards active
- [ ] Alerting configured
- [ ] Backup/restore tested

---

## 📚 Learning Resources

**Scalability Concepts:**
- Database indexing and query optimization
- Caching strategies (write-through, cache-aside)
- Connection pooling
- Horizontal scaling patterns
- Rate limiting techniques

**Tools & Technologies:**
- FastAPI async capabilities
- PostgreSQL replication
- Redis data structures
- Docker multi-stage builds
- Load balancing with Nginx

---

## 🔗 Related Projects

- **realtime-chat** - Real-time systems with WebSockets
- **graphql-api** - GraphQL API design patterns

---

## 📝 Learning Log

### What I Learned
- (Document your learnings here)

### Challenges Faced
- (Document challenges and solutions)

### Next Steps
- (Document future improvements)

---

**Created:** 2025-11-16
**Last Updated:** 2025-11-16
**Owner:** Backend Engineering Practice
