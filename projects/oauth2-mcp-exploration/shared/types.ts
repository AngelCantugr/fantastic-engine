/**
 * Shared types for OAuth 2.0 implementation
 */

/**
 * OAuth 2.0 Grant Types
 * - authorization_code: For web apps (most secure)
 * - client_credentials: For service-to-service (MCP, agents)
 * - refresh_token: To get new access tokens
 */
export type GrantType = 'authorization_code' | 'client_credentials' | 'refresh_token';

/**
 * OAuth 2.0 Client Registration
 */
export interface OAuthClient {
  client_id: string;
  client_secret: string;
  client_name: string;
  grant_types: GrantType[];
  redirect_uris?: string[];
  scope: string[];
}

/**
 * OAuth 2.0 Access Token
 */
export interface AccessToken {
  access_token: string;
  token_type: 'Bearer';
  expires_in: number;
  refresh_token?: string;
  scope: string;
}

/**
 * JWT Token Payload
 */
export interface TokenPayload {
  sub: string;          // Subject (user ID or client ID)
  client_id: string;    // OAuth client
  scope: string[];      // Granted scopes
  iat: number;          // Issued at
  exp: number;          // Expiration
  iss: string;          // Issuer
}

/**
 * Authorization Code (used in authorization_code flow)
 */
export interface AuthorizationCode {
  code: string;
  client_id: string;
  redirect_uri: string;
  scope: string[];
  user_id: string;
  expires_at: Date;
}

/**
 * User resource (protected by OAuth)
 */
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: Date;
}

/**
 * User action/task (what agents/MCP will create on behalf of user)
 */
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: Date;
  created_by: string; // client_id of the agent/MCP that created it
}
