# Docker Composer Skill

You are an expert at creating Docker configurations and Docker Compose setups for applications.

## When to Use

Activate when the user:
- Wants to containerize an application
- Mentions "Docker", "container", "docker-compose"
- Needs to set up development environment
- Wants to deploy with containers

## Docker Fundamentals

### Dockerfile
Defines how to build a container image

### Docker Compose
Orchestrates multiple containers together

### Images vs Containers
- **Image**: Template (like a class)
- **Container**: Running instance (like an object)

## Output Format

```markdown
## 🐳 Docker Configuration: [Application Name]

### Architecture

```
[Brief description of container setup]
```

### Files Created

- `Dockerfile` - Main application container
- `docker-compose.yml` - Multi-container orchestration
- `.dockerignore` - Files to exclude
- `docker-compose.dev.yml` - Development overrides (if applicable)

---

## Dockerfile

```dockerfile
[Dockerfile content]
```

## docker-compose.yml

```yaml
[Docker Compose content]
```

## .dockerignore

```
[Dockerignore content]
```

---

## Usage

**Build and run:**
```bash
docker-compose up --build
```

**Run in background:**
```bash
docker-compose up -d
```

**Stop containers:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Run commands in container:**
```bash
docker-compose exec app [command]
```

---

## Customization

[Tips for adapting the configuration]
```

## Dockerfile Examples

### Node.js Application

```dockerfile
# Multi-stage build for smaller image
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build if needed
# RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node healthcheck.js || exit 1

# Start application
CMD ["node", "index.js"]
```

### Python Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
```

### Go Application

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Production stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

### Static Site (Nginx)

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Docker Compose Examples

### Full Stack Application

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
      - /app/node_modules
    networks:
      - app-network

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

volumes:
  postgres-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

### Microservices Setup

```yaml
version: '3.8'

services:
  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "80:80"
    environment:
      - USER_SERVICE_URL=http://user-service:3000
      - ORDER_SERVICE_URL=http://order-service:3001
      - PRODUCT_SERVICE_URL=http://product-service:3002
    depends_on:
      - user-service
      - order-service
      - product-service
    networks:
      - microservices

  # User Service
  user-service:
    build: ./services/user
    environment:
      - DB_HOST=user-db
      - DB_NAME=users
    depends_on:
      - user-db
    networks:
      - microservices

  user-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=users
      - POSTGRES_PASSWORD=password
    volumes:
      - user-db-data:/var/lib/postgresql/data
    networks:
      - microservices

  # Order Service
  order-service:
    build: ./services/order
    environment:
      - DB_HOST=order-db
      - DB_NAME=orders
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - order-db
      - rabbitmq
    networks:
      - microservices

  order-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=orders
      - POSTGRES_PASSWORD=password
    volumes:
      - order-db-data:/var/lib/postgresql/data
    networks:
      - microservices

  # Product Service
  product-service:
    build: ./services/product
    environment:
      - MONGODB_URL=mongodb://product-db:27017/products
    depends_on:
      - product-db
    networks:
      - microservices

  product-db:
    image: mongo:7
    volumes:
      - product-db-data:/data/db
    networks:
      - microservices

  # Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - microservices

volumes:
  user-db-data:
  order-db-data:
  product-db-data:

networks:
  microservices:
    driver: bridge
```

### Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=*
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js debugger
    command: npm run dev

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=dev_password
    volumes:
      - db-data:/var/lib/postgresql/data

  # Development tools
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    environment:
      - ADMINER_DEFAULT_SERVER=db

volumes:
  db-data:
```

## .dockerignore

```
# Dependencies
node_modules/
vendor/
venv/
__pycache__/

# Build outputs
dist/
build/
*.pyc
*.pyo

# Version control
.git/
.gitignore
.github/

# Documentation
README.md
CHANGELOG.md
docs/

# Development files
.env
.env.local
*.log
.DS_Store
.vscode/
.idea/

# Tests
tests/
test/
*.test.js
*.spec.js
coverage/

# CI/CD
.gitlab-ci.yml
.github/
Jenkinsfile
```

## Docker Best Practices

### 1. Multi-stage Builds

```dockerfile
# Build stage - includes dev dependencies
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage - only runtime dependencies
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 2. Layer Caching

```dockerfile
# ✅ Good - Dependencies cached separately
COPY package*.json ./
RUN npm install
COPY . .

# ❌ Bad - Changes to any file invalidate cache
COPY . .
RUN npm install
```

### 3. Minimize Layers

```dockerfile
# ✅ Good - Combined into one layer
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/*

# ❌ Bad - Multiple layers
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
```

### 4. Use Specific Tags

```dockerfile
# ✅ Good - Specific version
FROM node:20.10.0-alpine

# ❌ Bad - Latest tag (unpredictable)
FROM node:latest
```

### 5. Security Practices

```dockerfile
# Run as non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

USER appuser

# Scan for vulnerabilities
# Use `docker scan imagename`

# Keep base images updated
FROM node:20-alpine  # Alpine is smaller and more secure
```

## Common Docker Commands

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -p 3000:3000 myapp:latest

# Run with environment variables
docker run -e NODE_ENV=production -p 3000:3000 myapp

# Run in background
docker run -d -p 3000:3000 myapp

# View running containers
docker ps

# View all containers
docker ps -a

# Stop container
docker stop container_id

# Remove container
docker rm container_id

# View logs
docker logs container_id
docker logs -f container_id  # Follow logs

# Execute command in container
docker exec -it container_id sh

# Remove image
docker rmi image_id

# Clean up
docker system prune -a  # Remove all unused images/containers
```

## Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs
docker-compose logs -f service_name

# Execute command
docker-compose exec service_name sh

# Run one-time command
docker-compose run service_name npm test

# Restart service
docker-compose restart service_name

# Scale service
docker-compose up -d --scale worker=3
```

## Debugging Containers

### Check Container Status

```bash
docker ps  # Running containers
docker logs container_id  # View logs
docker inspect container_id  # Detailed info
docker stats  # Resource usage
```

### Enter Container

```bash
docker exec -it container_id sh
# or
docker exec -it container_id bash
```

### Check Network

```bash
docker network ls
docker network inspect network_name
```

### Check Volumes

```bash
docker volume ls
docker volume inspect volume_name
```

## Production Considerations

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

```yaml
# In docker-compose.yml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
```

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Restart Policies

```yaml
services:
  app:
    restart: unless-stopped
    # Options: no, always, on-failure, unless-stopped
```

### Logging

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## ADHD-Friendly Docker

### Start Simple

```dockerfile
# Minimal Dockerfile to get started
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
```

Then optimize later!

### Use Templates

Copy from working examples and modify

### Test Locally First

```bash
# Quick test without compose
docker run -p 3000:3000 myapp
```

### One Service at a Time

Don't try to dockerize entire stack at once

### Use Docker Desktop

Visual interface helps understand what's running
