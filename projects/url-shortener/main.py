"""
URL Shortener - Main Application
Production-ready URL shortening service with Redis caching and PostgreSQL storage
"""

import secrets
import string
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text, DateTime, Boolean, Integer, select
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# ============================================================================
# Configuration
# ============================================================================

# In production, load from environment variables
DATABASE_URL = "postgresql+asyncpg://urlshortener:password@localhost:5432/urlshortener"
REDIS_URL = "redis://localhost:6379/0"
BASE_URL = "http://localhost:8000"
SHORT_CODE_LENGTH = 6
CACHE_TTL = 86400  # 24 hours
ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

# Base62 alphabet for short code generation
BASE62 = string.ascii_letters + string.digits

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Database Models
# ============================================================================

class Base(DeclarativeBase):
    pass


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


# ============================================================================
# Pydantic Models
# ============================================================================

class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = Field(None, min_length=4, max_length=10)
    expires_in_days: Optional[int] = Field(None, gt=0, le=365)

    @validator('custom_code')
    def validate_custom_code(cls, v):
        if v is not None:
            # Only allow alphanumeric characters
            if not all(c in BASE62 for c in v):
                raise ValueError('Custom code must contain only letters and numbers')
        return v


class ShortenResponse(BaseModel):
    short_url: str
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class URLStats(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    created_at: datetime
    is_active: bool


class HealthResponse(BaseModel):
    status: str
    database: str
    cache: str
    timestamp: datetime


# ============================================================================
# Database Setup
# ============================================================================

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        yield session


# ============================================================================
# Redis Setup
# ============================================================================

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service unavailable"
        )
    return redis_client


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_client

    # Startup
    logger.info("Starting URL Shortener application...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    # Connect to Redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()
    logger.info("Redis connection established")

    yield

    # Shutdown
    logger.info("Shutting down URL Shortener application...")
    if redis_client:
        await redis_client.close()
    await engine.dispose()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="URL Shortener API",
    description="Scalable URL shortening service with Redis caching and PostgreSQL storage",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)


# ============================================================================
# Utility Functions
# ============================================================================

def generate_short_code(length: int = SHORT_CODE_LENGTH) -> str:
    """Generate cryptographically secure random short code"""
    return ''.join(secrets.choice(BASE62) for _ in range(length))


async def get_url_from_cache(short_code: str, redis_conn: redis.Redis) -> Optional[str]:
    """Get URL from Redis cache"""
    try:
        return await redis_conn.get(f"url:{short_code}")
    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None


async def set_url_in_cache(short_code: str, url: str, redis_conn: redis.Redis, ttl: int = CACHE_TTL):
    """Store URL in Redis cache"""
    try:
        await redis_conn.setex(f"url:{short_code}", ttl, url)
    except Exception as e:
        logger.error(f"Cache write error: {e}")


async def increment_click_count(short_code: str, db: AsyncSession):
    """Increment click count for a URL (async)"""
    try:
        stmt = select(URL).where(URL.short_code == short_code)
        result = await db.execute(stmt)
        url = result.scalar_one_or_none()
        if url:
            url.click_count += 1
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to increment click count: {e}")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to API docs"""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint for monitoring"""
    db_status = "connected"
    cache_status = "connected"

    # Check database connection
    try:
        await db.execute(select(1))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    # Check Redis connection
    try:
        if redis_client:
            await redis_client.ping()
        else:
            cache_status = "disconnected"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        cache_status = "disconnected"

    overall_status = "healthy" if db_status == "connected" and cache_status == "connected" else "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        cache=cache_status,
        timestamp=datetime.utcnow()
    )


@app.post("/api/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    request: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    redis_conn: redis.Redis = Depends(get_redis)
):
    """Create a shortened URL"""

    # Generate or use custom short code
    short_code = request.custom_code if request.custom_code else generate_short_code()

    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

    # Create URL record
    url_record = URL(
        short_code=short_code,
        original_url=str(request.url),
        expires_at=expires_at
    )

    try:
        db.add(url_record)
        await db.commit()
        await db.refresh(url_record)

        # Cache the URL
        await set_url_in_cache(short_code, str(request.url), redis_conn)

        logger.info(f"Created short URL: {short_code} -> {request.url}")

        return ShortenResponse(
            short_url=f"{BASE_URL}/{short_code}",
            short_code=short_code,
            original_url=str(request.url),
            created_at=url_record.created_at,
            expires_at=url_record.expires_at
        )

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Short code '{short_code}' already exists. Please try a different custom code."
        )


@app.get("/{short_code}")
async def redirect_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis_conn: redis.Redis = Depends(get_redis)
):
    """Redirect to original URL"""

    # Try cache first
    original_url = await get_url_from_cache(short_code, redis_conn)

    if original_url:
        logger.info(f"Cache hit: {short_code}")
        # Increment click count asynchronously (don't wait)
        await increment_click_count(short_code, db)
        return RedirectResponse(url=original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    # Cache miss - query database
    logger.info(f"Cache miss: {short_code}")
    stmt = select(URL).where(
        URL.short_code == short_code,
        URL.is_active == True
    )
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    # Check expiration
    if url.expires_at and url.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This short URL has expired"
        )

    # Cache the URL for future requests
    await set_url_in_cache(short_code, url.original_url, redis_conn)

    # Increment click count
    url.click_count += 1
    await db.commit()

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.get("/api/stats/{short_code}", response_model=URLStats)
async def get_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """Get statistics for a short URL"""

    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    return URLStats(
        short_code=url.short_code,
        original_url=url.original_url,
        total_clicks=url.click_count,
        created_at=url.created_at,
        is_active=url.is_active
    )


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
