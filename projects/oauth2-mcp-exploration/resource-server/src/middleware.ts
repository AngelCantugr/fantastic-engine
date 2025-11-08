/**
 * OAuth 2.0 middleware for protecting endpoints
 */

import { Request, Response, NextFunction } from 'express';
import { JWTUtils, TokenPayload } from 'shared';

// Extend Express Request to include token payload
declare global {
  namespace Express {
    interface Request {
      token?: TokenPayload;
    }
  }
}

/**
 * Middleware to verify OAuth 2.0 Bearer token
 */
export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      error: 'unauthorized',
      error_description: 'Missing or invalid Authorization header',
    });
  }

  const token = authHeader.substring(7); // Remove 'Bearer ' prefix

  try {
    const payload = JWTUtils.verifyToken(token);
    req.token = payload;

    console.log(`[RESOURCE] ✓ Authenticated ${payload.sub} with scopes: ${payload.scope.join(', ')}`);

    next();
  } catch (error) {
    console.log(`[RESOURCE] ✗ Invalid token: ${error instanceof Error ? error.message : 'Unknown error'}`);

    return res.status(401).json({
      error: 'invalid_token',
      error_description: error instanceof Error ? error.message : 'Token verification failed',
    });
  }
}

/**
 * Middleware to require specific scope
 */
export function requireScope(requiredScope: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.token) {
      return res.status(401).json({
        error: 'unauthorized',
        error_description: 'No token found',
      });
    }

    if (!JWTUtils.hasScope(req.token, requiredScope)) {
      console.log(`[RESOURCE] ✗ Insufficient scope. Required: ${requiredScope}, Have: ${req.token.scope.join(', ')}`);

      return res.status(403).json({
        error: 'insufficient_scope',
        error_description: `Required scope: ${requiredScope}`,
        required_scope: requiredScope,
      });
    }

    next();
  };
}

/**
 * Middleware to require any of the specified scopes
 */
export function requireAnyScope(requiredScopes: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.token) {
      return res.status(401).json({
        error: 'unauthorized',
        error_description: 'No token found',
      });
    }

    if (!JWTUtils.hasAnyScope(req.token, requiredScopes)) {
      console.log(`[RESOURCE] ✗ Insufficient scope. Required one of: ${requiredScopes.join(', ')}, Have: ${req.token.scope.join(', ')}`);

      return res.status(403).json({
        error: 'insufficient_scope',
        error_description: `Required one of: ${requiredScopes.join(', ')}`,
        required_scopes: requiredScopes,
      });
    }

    next();
  };
}
