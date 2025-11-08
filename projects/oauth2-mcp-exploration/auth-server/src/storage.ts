/**
 * In-memory storage for OAuth clients, codes, and tokens
 * In production, use a real database (PostgreSQL, Redis, etc.)
 */

import { OAuthClient, AuthorizationCode, User } from 'shared';
import { randomBytes } from 'crypto';

export class Storage {
  private static clients = new Map<string, OAuthClient>();
  private static authCodes = new Map<string, AuthorizationCode>();
  private static users = new Map<string, User>();

  /**
   * Initialize with some demo clients and users
   */
  static init() {
    // Register MCP client
    this.registerClient({
      client_id: 'mcp-task-manager',
      client_secret: 'mcp-secret-12345',
      client_name: 'MCP Task Manager',
      grant_types: ['client_credentials'],
      scope: ['tasks:read', 'tasks:write'],
    });

    // Register AI Agent client
    this.registerClient({
      client_id: 'ai-agent-assistant',
      client_secret: 'agent-secret-67890',
      client_name: 'AI Agent Assistant',
      grant_types: ['client_credentials'],
      scope: ['tasks:read', 'tasks:write', 'user:read'],
    });

    // Register a web app client (for comparison)
    this.registerClient({
      client_id: 'web-app',
      client_secret: 'webapp-secret-abcdef',
      client_name: 'Web Application',
      grant_types: ['authorization_code', 'refresh_token'],
      redirect_uris: ['http://localhost:3000/callback'],
      scope: ['tasks:read', 'tasks:write', 'user:read', 'user:write'],
    });

    // Create a demo user
    this.createUser({
      id: 'user-123',
      username: 'demo-user',
      email: 'demo@example.com',
      created_at: new Date(),
    });
  }

  // Client methods
  static registerClient(client: OAuthClient) {
    this.clients.set(client.client_id, client);
  }

  static getClient(clientId: string): OAuthClient | undefined {
    return this.clients.get(clientId);
  }

  static authenticateClient(clientId: string, clientSecret: string): OAuthClient | null {
    const client = this.clients.get(clientId);
    if (!client || client.client_secret !== clientSecret) {
      return null;
    }
    return client;
  }

  // Authorization code methods
  static createAuthCode(clientId: string, redirectUri: string, scope: string[], userId: string): string {
    const code = randomBytes(32).toString('hex');
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    this.authCodes.set(code, {
      code,
      client_id: clientId,
      redirect_uri: redirectUri,
      scope,
      user_id: userId,
      expires_at: expiresAt,
    });

    return code;
  }

  static getAuthCode(code: string): AuthorizationCode | undefined {
    return this.authCodes.get(code);
  }

  static deleteAuthCode(code: string) {
    this.authCodes.delete(code);
  }

  // User methods
  static createUser(user: User) {
    this.users.set(user.id, user);
  }

  static getUser(userId: string): User | undefined {
    return this.users.get(userId);
  }

  static getAllUsers(): User[] {
    return Array.from(this.users.values());
  }

  // Debug methods
  static getAllClients(): OAuthClient[] {
    return Array.from(this.clients.values()).map(client => ({
      ...client,
      client_secret: '***REDACTED***',
    }));
  }
}
