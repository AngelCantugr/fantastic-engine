# API Designer Skill

You are an expert at designing clean, consistent, and developer-friendly APIs.

## When to Use

Activate when the user:
- Asks to design an API
- Mentions "REST API", "GraphQL", "API endpoints"
- Wants to create or improve API structure
- Asks about API best practices

## API Design Process

### 1. Understand Requirements

```markdown
## 📋 API Requirements

**Purpose:** [What problem does this API solve?]

**Users:** [Who will use this API?]
- [ ] Internal services
- [ ] External developers
- [ ] Mobile apps
- [ ] Web apps
- [ ] Third-party integrations

**Resources:** [What entities/data will be exposed?]
1. [Resource 1]
2. [Resource 2]

**Operations:** [What actions are needed?]
- [ ] Create (POST)
- [ ] Read (GET)
- [ ] Update (PUT/PATCH)
- [ ] Delete (DELETE)
- [ ] List/Search
- [ ] Batch operations
```

### 2. Choose API Style

```markdown
## 🎨 API Style Selection

**REST API** - Best for:
- CRUD operations
- Resource-based architecture
- HTTP-native clients
- Public APIs

**GraphQL** - Best for:
- Complex data requirements
- Mobile apps (reduce over-fetching)
- Flexible querying
- Rapid frontend iteration

**RPC/gRPC** - Best for:
- Microservices communication
- High performance needed
- Strong typing required
- Internal APIs
```

## REST API Design

### Resource Naming Conventions

```
✅ Good:
GET    /users
GET    /users/123
POST   /users
PUT    /users/123
DELETE /users/123
GET    /users/123/orders
POST   /users/123/orders

❌ Bad:
GET    /getUsers
POST   /createUser
GET    /user/123
GET    /users/123/getAllOrders
```

### Rules:
- Use **plural nouns** for collections: `/users`, `/products`
- Use **hyphens** for multi-word: `/order-items`
- **Lowercase** only
- **Nested resources** for relationships: `/users/123/orders`
- **Actions** via HTTP methods, not URLs
- **Filters** via query params: `/users?role=admin&status=active`

### HTTP Status Codes

```markdown
## Status Code Guide

### Success (2xx)
- **200 OK** - Successful GET, PUT, PATCH, DELETE
- **201 Created** - Successful POST
- **202 Accepted** - Request accepted for async processing
- **204 No Content** - Successful DELETE with no response body

### Client Errors (4xx)
- **400 Bad Request** - Invalid request syntax
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Conflict with current state (duplicate, version mismatch)
- **422 Unprocessable Entity** - Validation errors
- **429 Too Many Requests** - Rate limit exceeded

### Server Errors (5xx)
- **500 Internal Server Error** - Generic server error
- **502 Bad Gateway** - Invalid response from upstream
- **503 Service Unavailable** - Server temporarily unavailable
- **504 Gateway Timeout** - Upstream timeout
```

### Endpoint Design Template

```markdown
## Endpoint: [Name]

### `[METHOD] /path/to/resource`

**Description:** [What this endpoint does]

**Authentication:** Required / Optional / None

**Rate Limit:** [requests per minute]

**Request:**

Headers:
```http
Content-Type: application/json
Authorization: Bearer {token}
```

Path Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | string | Yes | User ID |

Query Parameters:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| limit | integer | No | 20 | Items per page |

Body:
```json
{
  "name": "string",
  "email": "string",
  "role": "user|admin"
}
```

**Response:**

Success (200):
```json
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

Error (400):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

**Example:**

```bash
curl -X POST https://api.example.com/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{"name":"John Doe","email":"john@example.com"}'
```
```

## Output Format

```markdown
## 🎯 API Design: [API Name]

### Overview

**Base URL:** `https://api.example.com/v1`

**Authentication:** Bearer Token / API Key / OAuth2

**Rate Limiting:** [limits]

**Versioning:** URL path (`/v1/`) / Header

---

## 📚 Resources & Endpoints

### Resource: Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| GET | `/users/{id}` | Get user by ID |
| POST | `/users` | Create new user |
| PUT | `/users/{id}` | Update user |
| PATCH | `/users/{id}` | Partial update |
| DELETE | `/users/{id}` | Delete user |

### Resource: [Another Resource]

[Repeat pattern]

---

## 🔐 Authentication

[Authentication scheme details]

**Example:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📊 Pagination

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## 🔍 Filtering & Sorting

**Filtering:**
- `?status=active`
- `?role=admin&verified=true`

**Sorting:**
- `?sort=createdAt` (ascending)
- `?sort=-createdAt` (descending)
- `?sort=name,-createdAt` (multiple fields)

**Search:**
- `?q=search+term`

---

## 🚨 Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [...]
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` - Invalid input
- `AUTHENTICATION_REQUIRED` - Missing auth
- `AUTHORIZATION_FAILED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - 404
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## 📖 Complete Endpoint Documentation

[Detailed specs for each endpoint using template above]
```

## REST API Best Practices

### 1. Consistency

```javascript
// ✅ Consistent structure
GET  /users
GET  /products
GET  /orders

// ❌ Inconsistent
GET  /users
GET  /getProducts
POST /createOrder
```

### 2. Use Proper HTTP Methods

```javascript
// ✅ Correct
GET    /users/123          // Fetch user
POST   /users              // Create user
PUT    /users/123          // Full update
PATCH  /users/123          // Partial update
DELETE /users/123          // Delete user

// ❌ Wrong
GET    /users/delete/123   // Don't use GET for destructive actions
POST   /users/123/update   // Use PUT or PATCH
```

### 3. Version Your API

```javascript
// Option 1: URL versioning (recommended)
GET /v1/users
GET /v2/users

// Option 2: Header versioning
GET /users
Headers: Accept: application/vnd.api.v1+json

// Option 3: Query parameter (least recommended)
GET /users?version=1
```

### 4. Return Appropriate Status Codes

```javascript
// ✅ Appropriate codes
app.post('/users', (req, res) => {
  const user = createUser(req.body);
  res.status(201).json(user);  // 201 Created
});

app.delete('/users/:id', (req, res) => {
  deleteUser(req.params.id);
  res.status(204).send();  // 204 No Content
});

// ❌ Always returning 200
app.post('/users', (req, res) => {
  res.status(200).json(user);  // Wrong! Should be 201
});
```

### 5. Pagination for Lists

```javascript
// ✅ Paginated response
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  },
  "links": {
    "first": "/users?page=1",
    "prev": null,
    "next": "/users?page=2",
    "last": "/users?page=8"
  }
}
```

### 6. Filter, Sort, Search

```javascript
// Filtering
GET /users?status=active&role=admin

// Sorting
GET /users?sort=-createdAt,name  // - prefix for desc

// Searching
GET /users?q=john

// Field selection (sparse fieldsets)
GET /users?fields=id,name,email
```

### 7. Use HATEOAS (Optional)

```json
{
  "id": "123",
  "name": "John Doe",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "avatar": { "href": "/users/123/avatar" }
  }
}
```

## GraphQL Design

### Schema Design

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  role: Role!
  orders: [Order!]!
  createdAt: DateTime!
}

enum Role {
  USER
  ADMIN
}

type Order {
  id: ID!
  user: User!
  items: [OrderItem!]!
  total: Float!
  status: OrderStatus!
}

enum OrderStatus {
  PENDING
  PAID
  SHIPPED
  DELIVERED
  CANCELLED
}

type Query {
  user(id: ID!): User
  users(
    page: Int = 1
    limit: Int = 20
    role: Role
  ): UserConnection!

  order(id: ID!): Order
  orders(status: OrderStatus): [Order!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  createOrder(input: CreateOrderInput!): Order!
}

input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

input UpdateUserInput {
  email: String
  name: String
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

## Security Considerations

```markdown
## 🔒 Security Checklist

- [ ] **Authentication**: Verify user identity
- [ ] **Authorization**: Check permissions for each resource
- [ ] **Rate Limiting**: Prevent abuse (e.g., 100 req/min)
- [ ] **Input Validation**: Sanitize and validate all inputs
- [ ] **HTTPS Only**: Encrypt data in transit
- [ ] **CORS**: Configure properly for web clients
- [ ] **API Keys**: Rotate regularly, use env variables
- [ ] **SQL Injection**: Use parameterized queries
- [ ] **XSS Prevention**: Sanitize output
- [ ] **Sensitive Data**: Don't expose in responses (passwords, tokens)
- [ ] **Audit Logging**: Log all access and changes
```

## Documentation Tools

- **Swagger/OpenAPI**: Interactive API docs
- **Postman**: Collections and examples
- **GraphQL Playground**: GraphQL exploration
- **Redoc**: Beautiful OpenAPI rendering

## ADHD-Friendly API Design

### Start Simple
1. Design one resource at a time
2. Get CRUD working first
3. Add filtering/pagination later
4. Optimize last

### Use Templates
Copy-paste endpoint structure for consistency

### Document As You Go
Write API docs while building, not after

### Test Early
Use Postman/Insomnia to test each endpoint immediately
