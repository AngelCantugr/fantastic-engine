# 📖 OAuth 2.0 Learning Guide

A step-by-step guide to understanding OAuth 2.0 through this practical implementation.

## 🎯 Learning Objectives

By the end of this guide, you'll understand:
1. What OAuth 2.0 is and why it exists
2. How the client_credentials flow works
3. How the authorization_code flow works
4. How to implement OAuth in MCP servers and agents
5. Best practices for OAuth security

## 📚 Part 1: OAuth 2.0 Fundamentals

### What is OAuth 2.0?

**The Problem:**
You want an app (like an AI agent) to access your data on another service (like a task manager), but you don't want to give it your password.

**The Solution:**
OAuth 2.0 provides a way for apps to get limited access to your data without ever seeing your password.

### Real-World Analogy

Think of OAuth like a hotel key card:

```mermaid
graph LR
    A[You Check In] --> B[Front Desk]
    B --> C[Front Desk Verifies ID]
    C --> D[Issues Key Card]
    D --> E[Key Card Works Only For:]
    E --> F[Your Room]
    E --> G[Pool Hours: 6am-10pm]
    E --> H[Gym]
    E -.->|Cannot Access| I[Other Rooms]
    E -.->|Cannot Access| J[Staff Areas]

    style B fill:#ff00ff,stroke:#00ffff
    style D fill:#00ff00,stroke:#ff00ff
    style F fill:#ffff00,stroke:#ff00ff
    style G fill:#ffff00,stroke:#ff00ff
    style H fill:#ffff00,stroke:#ff00ff
```

**Key Points:**
- **Limited Access:** Key card only works for specific areas (like OAuth scopes)
- **Temporary:** Key expires at checkout (like token expiration)
- **Revocable:** Hotel can deactivate it anytime
- **No Master Key:** You never get the hotel's master key (password)

### OAuth Roles

```mermaid
graph TB
    subgraph "The OAuth Dance"
        RO[Resource Owner<br/>👤 The User<br/>Has data/resources]
        CLIENT[Client<br/>🤖 MCP/Agent<br/>Wants access]
        AUTH[Authorization Server<br/>🔐 Port 4000<br/>Issues tokens]
        RS[Resource Server<br/>📦 Port 4001<br/>Protects resources]
    end

    RO -->|Owns| DATA[User's Tasks<br/>User's Data]
    CLIENT -->|Requests token| AUTH
    AUTH -->|Issues token| CLIENT
    CLIENT -->|Uses token| RS
    RS -->|Protects| DATA

    style RO fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style CLIENT fill:#00ff00,stroke:#ff00ff,stroke-width:2px
    style AUTH fill:#00ffff,stroke:#ff00ff,stroke-width:2px
    style RS fill:#ffff00,stroke:#ff00ff,stroke-width:2px
```

## 📚 Part 2: Client Credentials Flow (MCP & Agents)

This is the flow used by our MCP server and AI agent.

### When to Use Client Credentials

✅ **Use when:**
- Your client is a backend service (MCP server, agent)
- The client acts on its own behalf (or pre-authorized user)
- No user interaction is needed
- The client can keep secrets secure

❌ **Don't use when:**
- Building a web or mobile app with users
- Need per-user permissions
- Client code runs in browser/app

### The Flow - Step by Step

```mermaid
sequenceDiagram
    autonumber
    participant MCP as MCP Server<br/>(mcp-task-manager)
    participant Auth as Auth Server<br/>(Port 4000)
    participant API as Resource Server<br/>(Port 4001)

    Note over MCP: I need to access tasks

    MCP->>Auth: POST /oauth/token<br/>client_id: "mcp-task-manager"<br/>client_secret: "mcp-secret-12345"<br/>grant_type: "client_credentials"<br/>scope: "tasks:read tasks:write"

    Note over Auth: Verify credentials<br/>Check scopes<br/>Generate JWT

    Auth-->>MCP: 200 OK<br/>{<br/>  access_token: "eyJhbG...",<br/>  expires_in: 3600,<br/>  scope: "tasks:read tasks:write"<br/>}

    Note over MCP: Store token<br/>Set expiry time

    MCP->>API: GET /api/tasks<br/>Authorization: Bearer eyJhbG...

    Note over API: Verify JWT signature<br/>Check expiration<br/>Check scopes

    API-->>MCP: 200 OK<br/>{tasks: [...]}

    Note over MCP: Success!<br/>Use the data
```

### Code Walkthrough

**Step 1: Request Token** (`mcp-client/src/oauth-client.ts:44-72`)

```typescript
// The MCP server authenticates itself
const response = await axios.post(
  'http://localhost:4000/oauth/token',
  {
    grant_type: 'client_credentials',  // ← Flow type
    client_id: 'mcp-task-manager',     // ← Who am I?
    client_secret: 'mcp-secret-12345', // ← Prove it
    scope: 'tasks:read tasks:write',   // ← What do I need?
  }
);

// Response contains the token
// {
//   access_token: "eyJhbGciOi...",
//   token_type: "Bearer",
//   expires_in: 3600,
//   scope: "tasks:read tasks:write"
// }
```

**Step 2: Use Token** (`mcp-client/src/oauth-client.ts:78-110`)

```typescript
// Include token in API request
const response = await axios.get(
  'http://localhost:4001/api/tasks',
  {
    headers: {
      Authorization: `Bearer ${accessToken}`,  // ← The magic line
    }
  }
);
```

**Step 3: Verify Token** (`resource-server/src/middleware.ts:16-48`)

```typescript
// Resource server verifies the token
const token = req.headers.authorization?.substring(7); // Remove 'Bearer '
const payload = JWTUtils.verifyToken(token);  // Verify signature
// Check scopes, expiration, etc.
```

### Try It Yourself

**Exercise 1: Get a Token Manually**

```bash
# Terminal 1: Start auth server
cd projects/oauth2-mcp-exploration
npm run dev:auth

# Terminal 2: Get token
curl -X POST http://localhost:4000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "mcp-task-manager",
    "client_secret": "mcp-secret-12345",
    "scope": "tasks:read"
  }'

# Copy the access_token from the response
```

**Exercise 2: Use the Token**

```bash
# Terminal 3: Start resource server
npm run dev:resource

# Terminal 4: Use your token
export TOKEN="paste-your-token-here"

curl http://localhost:4001/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# You should see the tasks!
```

**Exercise 3: Break It**

```bash
# Try without token (should fail with 401)
curl http://localhost:4001/api/tasks

# Try with invalid token (should fail with 401)
curl http://localhost:4001/api/tasks \
  -H "Authorization: Bearer invalid-token"

# Try with expired token (modify JWT_SECRET then get new token)
# Original token should fail
```

## 📚 Part 3: Authorization Code Flow (Web Apps)

This flow is used when a user needs to grant permission.

### When to Use Authorization Code

✅ **Use when:**
- Building web or mobile apps
- Users need to grant permission
- Need access to user-specific data
- Different users, different permissions

### The Flow - Step by Step

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 User
    participant App as Web App
    participant Auth as Auth Server
    participant API as Resource Server

    User->>App: Click "Login with OAuth"

    App->>Auth: Redirect to /oauth/authorize<br/>client_id, redirect_uri, scope

    Auth->>User: Show login page<br/>"Do you approve?"

    User->>Auth: "Yes, I approve"

    Auth->>App: Redirect to callback<br/>?code=abc123

    App->>Auth: POST /oauth/token<br/>code=abc123<br/>client_id, client_secret

    Auth-->>App: access_token + refresh_token

    App->>API: GET /api/tasks<br/>Bearer token

    API-->>App: User's tasks

    App-->>User: Show tasks
```

### Key Differences from Client Credentials

| Aspect | Client Credentials | Authorization Code |
|--------|-------------------|-------------------|
| User involved? | ❌ No | ✅ Yes |
| Consent screen? | ❌ No | ✅ Yes |
| Refresh token? | ❌ Usually no | ✅ Yes |
| Token represents | The client | The user |
| Use case | Service-to-service | User-delegated access |

### Try It Yourself

**Exercise 4: Get Authorization Code**

```bash
# Start servers if not running
npm run dev:auth
npm run dev:resource

# Get authorization code (simulated user consent)
curl -X POST http://localhost:4000/oauth/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "web-app",
    "redirect_uri": "http://localhost:3000/callback",
    "scope": "tasks:read tasks:write",
    "user_id": "user-123"
  }'

# You'll get back: {"code": "...", "redirect_uri": "..."}
# In a real app, this would redirect the user
```

**Exercise 5: Exchange Code for Token**

```bash
# Use the code from Exercise 4
export CODE="paste-code-here"

curl -X POST http://localhost:4000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "'$CODE'",
    "client_id": "web-app",
    "client_secret": "webapp-secret-abcdef",
    "redirect_uri": "http://localhost:3000/callback"
  }'

# You'll get: access_token AND refresh_token
```

## 📚 Part 4: Scopes - Fine-Grained Permissions

### What Are Scopes?

Scopes are permissions that limit what a token can do.

```mermaid
graph TB
    TOKEN[Access Token] --> SCOPES{What scopes?}

    SCOPES -->|tasks:read| READ[✓ List tasks<br/>✓ Get task details<br/>✗ Create tasks<br/>✗ Update tasks]

    SCOPES -->|tasks:write| WRITE[✓ Create tasks<br/>✓ Update tasks<br/>✓ Delete tasks<br/>Requires tasks:read too]

    SCOPES -->|user:read| USERREAD[✓ Get user profile<br/>✗ Update user]

    SCOPES -->|user:write| USERWRITE[✓ Update user profile<br/>Requires user:read too]

    style TOKEN fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style READ fill:#00ff00,stroke:#ff00ff
    style WRITE fill:#00ff00,stroke:#ff00ff
    style USERREAD fill:#00ff00,stroke:#ff00ff
    style USERWRITE fill:#00ff00,stroke:#ff00ff
```

### Scope Best Practices

1. **Principle of Least Privilege**
   ```typescript
   // ❌ Bad: Request all scopes
   scope: "tasks:read tasks:write user:read user:write admin:all"

   // ✅ Good: Request only what you need
   scope: "tasks:read"  // Just reading tasks
   ```

2. **Granular Scopes**
   ```typescript
   // ✅ Good scope design
   "tasks:read"      // Read tasks
   "tasks:write"     // Create/update tasks
   "tasks:delete"    // Delete tasks
   "tasks:admin"     // Full task management

   // ❌ Bad scope design
   "tasks"           // Too broad
   ```

3. **Hierarchical Scopes**
   ```typescript
   // Higher scopes include lower ones
   "user:admin"  → includes "user:write" → includes "user:read"
   ```

### Exercise 6: Scope Enforcement

**Try requesting too many scopes:**

```bash
curl -X POST http://localhost:4000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "mcp-task-manager",
    "client_secret": "mcp-secret-12345",
    "scope": "tasks:read tasks:write user:admin"
  }'

# Should fail because mcp-task-manager isn't registered for user:admin
```

**Try accessing without required scope:**

```bash
# Get token with only tasks:read
export TOKEN="get-token-with-tasks-read-only"

# Try to create task (requires tasks:write)
curl -X POST http://localhost:4001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'

# Should fail with 403 Insufficient Scope
```

## 📚 Part 5: JWT Tokens Explained

### What's Inside a JWT?

A JWT has three parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
      ↑ Header                              ↑ Payload                                                           ↑ Signature
```

### Decoded JWT Structure

```mermaid
graph TB
    JWT[JWT Token] --> HEADER[Header]
    JWT --> PAYLOAD[Payload]
    JWT --> SIG[Signature]

    HEADER --> H1["alg: HS256<br/>(Algorithm)"]
    HEADER --> H2["typ: JWT<br/>(Type)"]

    PAYLOAD --> P1["sub: user-123<br/>(Subject)"]
    PAYLOAD --> P2["client_id: mcp-task-manager<br/>(OAuth client)"]
    PAYLOAD --> P3["scope: [tasks:read, tasks:write]<br/>(Permissions)"]
    PAYLOAD --> P4["iat: 1699564800<br/>(Issued at)"]
    PAYLOAD --> P5["exp: 1699568400<br/>(Expires)"]
    PAYLOAD --> P6["iss: oauth2-auth-server<br/>(Issuer)"]

    SIG --> S1[HMAC-SHA256 hash of<br/>header + payload + secret]

    style JWT fill:#ff00ff,stroke:#00ffff,stroke-width:2px
    style HEADER fill:#00ff00,stroke:#ff00ff
    style PAYLOAD fill:#00ffff,stroke:#ff00ff
    style SIG fill:#ffff00,stroke:#ff00ff
```

### Verifying a JWT

```typescript
// resource-server/src/middleware.ts

function verifyToken(token: string) {
  // 1. Split into parts
  const [header, payload, signature] = token.split('.');

  // 2. Verify signature
  const validSignature = hmacSHA256(
    header + '.' + payload,
    SECRET_KEY
  );

  if (signature !== validSignature) {
    throw new Error('Invalid signature');
  }

  // 3. Decode payload
  const decoded = base64Decode(payload);

  // 4. Check expiration
  if (decoded.exp < Date.now() / 1000) {
    throw new Error('Token expired');
  }

  // 5. Check issuer
  if (decoded.iss !== 'oauth2-auth-server') {
    throw new Error('Invalid issuer');
  }

  return decoded;
}
```

### Exercise 7: Decode Your Own Token

```bash
# Get a token
curl -X POST http://localhost:4000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "mcp-task-manager",
    "client_secret": "mcp-secret-12345",
    "scope": "tasks:read"
  }' | jq -r '.access_token'

# Copy the token and go to https://jwt.io
# Paste it in the "Encoded" section
# See the decoded header and payload!
```

## 📚 Part 6: Security Best Practices

### ✅ Do's

1. **Always use HTTPS in production**
   ```
   ✅ https://api.example.com
   ❌ http://api.example.com
   ```

2. **Store secrets in environment variables**
   ```typescript
   // ✅ Good
   const clientSecret = process.env.CLIENT_SECRET;

   // ❌ Bad
   const clientSecret = "hardcoded-secret-12345";
   ```

3. **Validate all scopes**
   ```typescript
   // ✅ Good
   if (!token.scope.includes('tasks:write')) {
     return res.status(403).json({error: 'insufficient_scope'});
   }

   // ❌ Bad
   // Just trust the token
   ```

4. **Set appropriate token expiration**
   ```typescript
   // ✅ Good
   expiresIn: '1h'  // Short-lived access tokens

   // ❌ Bad
   expiresIn: '10y'  // Way too long!
   ```

### ❌ Don'ts

1. **Never log tokens**
   ```typescript
   // ❌ Bad
   console.log('Token:', accessToken);

   // ✅ Good
   console.log('Token received for client:', clientId);
   ```

2. **Never send tokens in URL**
   ```
   // ❌ Bad
   GET /api/tasks?token=abc123

   // ✅ Good
   GET /api/tasks
   Authorization: Bearer abc123
   ```

3. **Never skip token verification**
   ```typescript
   // ❌ Bad
   app.get('/api/tasks', (req, res) => {
     // Just return data without checking token
   });

   // ✅ Good
   app.get('/api/tasks', requireAuth, (req, res) => {
     // Token verified by middleware
   });
   ```

## 📚 Part 7: Common Patterns

### Pattern 1: Token Caching

```typescript
// mcp-client/src/oauth-client.ts
class OAuthClient {
  private accessToken: string | null = null;
  private tokenExpiry: number | null = null;

  async getAccessToken(): Promise<string> {
    // Reuse cached token if still valid
    if (this.accessToken && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }

    // Otherwise fetch new token
    await this.fetchAccessToken();
    return this.accessToken;
  }
}
```

### Pattern 2: Automatic Retry on 401

```typescript
// mcp-client/src/oauth-client.ts
async authenticatedRequest<T>(url: string): Promise<T> {
  try {
    return await this.makeRequest(url);
  } catch (error) {
    if (error.status === 401) {
      // Token might be invalid, get new one
      this.accessToken = null;
      const newToken = await this.getAccessToken();
      return await this.makeRequest(url);
    }
    throw error;
  }
}
```

### Pattern 3: Scope Middleware

```typescript
// resource-server/src/middleware.ts
function requireScope(scope: string) {
  return (req, res, next) => {
    if (!req.token.scope.includes(scope)) {
      return res.status(403).json({
        error: 'insufficient_scope',
        required_scope: scope,
      });
    }
    next();
  };
}

// Usage
app.get('/api/tasks', requireAuth, requireScope('tasks:read'), handler);
```

## 🎓 Next Steps

### Beginner → Intermediate
- [ ] Complete all exercises in this guide
- [ ] Run the AI agent demo
- [ ] Modify scopes and observe behavior
- [ ] Add a new endpoint to the resource server

### Intermediate → Advanced
- [ ] Implement refresh token flow
- [ ] Add PKCE (Proof Key for Code Exchange)
- [ ] Implement token revocation
- [ ] Add OpenID Connect layer
- [ ] Build a simple web UI for authorization

### Advanced Projects
- [ ] Build a full OAuth provider
- [ ] Implement multiple grant types
- [ ] Add dynamic client registration
- [ ] Implement OAuth for a real application
- [ ] Add rate limiting and throttling

## 📚 Additional Learning Resources

### Official Specs
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7519 - JWT](https://datatracker.ietf.org/doc/html/rfc7519)
- [RFC 7662 - Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662)

### Beginner-Friendly
- [OAuth 2.0 Simplified](https://www.oauth.com/)
- [JWT.io - Token Decoder](https://jwt.io)
- [OAuth Playground](https://www.oauth.com/playground/)

### Videos
- [OAuth 2.0 Explained in Plain English](https://www.youtube.com/watch?v=CPbvxxslDTU)
- [JWT Authentication Tutorial](https://www.youtube.com/watch?v=7Q17ubqLfaM)

## 🤔 Quiz Yourself

1. What's the difference between client_credentials and authorization_code flows?
2. Why shouldn't you use client_credentials for web apps?
3. What are scopes and why are they important?
4. What are the three parts of a JWT?
5. How long should an access token live?
6. When should you use a refresh token?
7. What happens if you try to use an expired token?
8. How does the resource server verify a token?

## 🎉 Congratulations!

You now understand OAuth 2.0! You've learned:
- ✅ How OAuth works conceptually
- ✅ The client_credentials flow (MCP/agents)
- ✅ The authorization_code flow (web apps)
- ✅ Scopes and permissions
- ✅ JWT tokens
- ✅ Security best practices

**Keep experimenting and building!** 🚀
