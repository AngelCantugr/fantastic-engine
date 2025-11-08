/**
 * OAuth 2.0 Authorization Server
 *
 * Endpoints:
 * - POST /oauth/token - Get access token (client_credentials or authorization_code)
 * - POST /oauth/authorize - Get authorization code (for web apps)
 * - POST /oauth/introspect - Verify token validity
 * - GET /debug/clients - List registered clients
 */

import express from 'express';
import { JWTUtils } from 'shared';
import { Storage } from './storage.js';

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize storage with demo data
Storage.init();

/**
 * Token endpoint - RFC 6749 Section 3.2
 * Handles both client_credentials and authorization_code grants
 */
app.post('/oauth/token', (req, res) => {
  const { grant_type, client_id, client_secret, code, redirect_uri, scope } = req.body;

  console.log(`[AUTH] Token request - grant_type: ${grant_type}, client_id: ${client_id}`);

  // Authenticate client
  const client = Storage.authenticateClient(client_id, client_secret);
  if (!client) {
    return res.status(401).json({
      error: 'invalid_client',
      error_description: 'Client authentication failed',
    });
  }

  // Check if client supports this grant type
  if (!client.grant_types.includes(grant_type)) {
    return res.status(400).json({
      error: 'unauthorized_client',
      error_description: `Client not authorized for grant_type: ${grant_type}`,
    });
  }

  // Handle client_credentials grant (for MCP and agents)
  if (grant_type === 'client_credentials') {
    const requestedScopes = scope ? scope.split(' ') : client.scope;

    // Validate scopes
    const invalidScopes = requestedScopes.filter((s: string) => !client.scope.includes(s));
    if (invalidScopes.length > 0) {
      return res.status(400).json({
        error: 'invalid_scope',
        error_description: `Invalid scopes: ${invalidScopes.join(', ')}`,
      });
    }

    // Generate token
    const accessToken = JWTUtils.generateAccessToken({
      sub: client_id,
      client_id: client_id,
      scope: requestedScopes,
    });

    console.log(`[AUTH] ✓ Issued token for ${client_id} with scopes: ${requestedScopes.join(', ')}`);

    return res.json({
      access_token: accessToken,
      token_type: 'Bearer',
      expires_in: 3600,
      scope: requestedScopes.join(' '),
    });
  }

  // Handle authorization_code grant (for web apps)
  if (grant_type === 'authorization_code') {
    if (!code || !redirect_uri) {
      return res.status(400).json({
        error: 'invalid_request',
        error_description: 'Missing code or redirect_uri',
      });
    }

    const authCode = Storage.getAuthCode(code);
    if (!authCode) {
      return res.status(400).json({
        error: 'invalid_grant',
        error_description: 'Invalid authorization code',
      });
    }

    // Validate authorization code
    if (authCode.client_id !== client_id) {
      return res.status(400).json({
        error: 'invalid_grant',
        error_description: 'Code was issued to different client',
      });
    }

    if (authCode.redirect_uri !== redirect_uri) {
      return res.status(400).json({
        error: 'invalid_grant',
        error_description: 'Redirect URI mismatch',
      });
    }

    if (new Date() > authCode.expires_at) {
      Storage.deleteAuthCode(code);
      return res.status(400).json({
        error: 'invalid_grant',
        error_description: 'Authorization code expired',
      });
    }

    // Delete code (one-time use)
    Storage.deleteAuthCode(code);

    // Generate tokens
    const accessToken = JWTUtils.generateAccessToken({
      sub: authCode.user_id,
      client_id: client_id,
      scope: authCode.scope,
    });

    const refreshToken = JWTUtils.generateRefreshToken({
      sub: authCode.user_id,
      client_id: client_id,
      scope: authCode.scope,
    });

    console.log(`[AUTH] ✓ Issued token for user ${authCode.user_id} via ${client_id}`);

    return res.json({
      access_token: accessToken,
      token_type: 'Bearer',
      expires_in: 3600,
      refresh_token: refreshToken,
      scope: authCode.scope.join(' '),
    });
  }

  return res.status(400).json({
    error: 'unsupported_grant_type',
    error_description: `Grant type ${grant_type} not supported`,
  });
});

/**
 * Authorization endpoint - RFC 6749 Section 3.1
 * Simplified version for demo purposes
 */
app.post('/oauth/authorize', (req, res) => {
  const { client_id, redirect_uri, scope, user_id } = req.body;

  const client = Storage.getClient(client_id);
  if (!client) {
    return res.status(400).json({
      error: 'invalid_client',
      error_description: 'Unknown client',
    });
  }

  if (!client.redirect_uris?.includes(redirect_uri)) {
    return res.status(400).json({
      error: 'invalid_request',
      error_description: 'Invalid redirect_uri',
    });
  }

  const requestedScopes = scope.split(' ');
  const invalidScopes = requestedScopes.filter((s: string) => !client.scope.includes(s));
  if (invalidScopes.length > 0) {
    return res.status(400).json({
      error: 'invalid_scope',
      error_description: `Invalid scopes: ${invalidScopes.join(', ')}`,
    });
  }

  // In a real app, verify user is authenticated and consented
  // For demo, we'll just accept any user_id
  const code = Storage.createAuthCode(client_id, redirect_uri, requestedScopes, user_id);

  console.log(`[AUTH] ✓ Created authorization code for user ${user_id}`);

  res.json({
    code,
    redirect_uri,
  });
});

/**
 * Token introspection endpoint - RFC 7662
 * Used by resource servers to validate tokens
 */
app.post('/oauth/introspect', (req, res) => {
  const { token } = req.body;

  if (!token) {
    return res.status(400).json({
      error: 'invalid_request',
      error_description: 'Missing token parameter',
    });
  }

  try {
    const payload = JWTUtils.verifyToken(token);

    console.log(`[AUTH] ✓ Token introspection - valid token for ${payload.sub}`);

    res.json({
      active: true,
      scope: payload.scope.join(' '),
      client_id: payload.client_id,
      sub: payload.sub,
      exp: payload.exp,
      iat: payload.iat,
    });
  } catch (error) {
    console.log(`[AUTH] ✗ Token introspection - invalid token`);

    res.json({
      active: false,
    });
  }
});

/**
 * Debug endpoint - list registered clients
 */
app.get('/debug/clients', (req, res) => {
  res.json({
    clients: Storage.getAllClients(),
  });
});

/**
 * Health check
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'auth-server' });
});

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║  🔐 OAuth 2.0 Authorization Server                       ║
╟──────────────────────────────────────────────────────────╢
║  Port: ${PORT}                                            ║
║  Endpoints:                                              ║
║    POST /oauth/token      - Get access token             ║
║    POST /oauth/authorize  - Get authorization code       ║
║    POST /oauth/introspect - Verify token                 ║
║    GET  /debug/clients    - List registered clients      ║
║    GET  /health           - Health check                 ║
╟──────────────────────────────────────────────────────────╢
║  Registered Clients:                                     ║
║    • mcp-task-manager (MCP server)                       ║
║    • ai-agent-assistant (AI agent)                       ║
║    • web-app (demo web application)                      ║
╚══════════════════════════════════════════════════════════╝
  `);
});
