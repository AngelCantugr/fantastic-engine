/**
 * JWT utilities for creating and verifying OAuth tokens
 */

import jwt from 'jsonwebtoken';
import { TokenPayload } from './types.js';

// In production, use environment variables and rotate regularly
const JWT_SECRET = 'your-super-secret-jwt-key-change-in-production';
const JWT_ISSUER = 'oauth2-auth-server';

export class JWTUtils {
  /**
   * Generate an access token
   */
  static generateAccessToken(payload: Omit<TokenPayload, 'iat' | 'exp' | 'iss'>): string {
    return jwt.sign(
      payload,
      JWT_SECRET,
      {
        expiresIn: '1h',
        issuer: JWT_ISSUER,
      }
    );
  }

  /**
   * Generate a refresh token (longer lived)
   */
  static generateRefreshToken(payload: Omit<TokenPayload, 'iat' | 'exp' | 'iss'>): string {
    return jwt.sign(
      payload,
      JWT_SECRET,
      {
        expiresIn: '7d',
        issuer: JWT_ISSUER,
      }
    );
  }

  /**
   * Verify and decode a token
   */
  static verifyToken(token: string): TokenPayload {
    try {
      const decoded = jwt.verify(token, JWT_SECRET, {
        issuer: JWT_ISSUER,
      });
      return decoded as TokenPayload;
    } catch (error) {
      throw new Error(`Invalid token: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Decode token without verification (for debugging)
   */
  static decodeToken(token: string): TokenPayload | null {
    try {
      const decoded = jwt.decode(token);
      return decoded as TokenPayload;
    } catch {
      return null;
    }
  }

  /**
   * Check if token has required scope
   */
  static hasScope(token: TokenPayload, requiredScope: string): boolean {
    return token.scope.includes(requiredScope);
  }

  /**
   * Check if token has any of the required scopes
   */
  static hasAnyScope(token: TokenPayload, requiredScopes: string[]): boolean {
    return requiredScopes.some(scope => token.scope.includes(scope));
  }
}
