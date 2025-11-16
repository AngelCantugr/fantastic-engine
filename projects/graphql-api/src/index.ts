/**
 * GraphQL API Server
 * Apollo Server 4 with subscriptions, DataLoader, and authentication
 */

import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginDrainHttpServer } from '@apollo/server/plugin/drainHttpServer';
import { makeExecutableSchema } from '@graphql-tools/schema';
import { WebSocketServer } from 'ws';
import { useServer } from 'graphql-ws/lib/use/ws';
import express from 'express';
import { createServer } from 'http';
import cors from 'cors';
import { PrismaClient } from '@prisma/client';
import DataLoader from 'dataloader';
import { typeDefs } from './schema';
import { resolvers } from './resolvers';
import { verifyToken } from './utils/auth';
import type { User } from '@prisma/client';

// ============================================================================
// Configuration
// ============================================================================

const PORT = parseInt(process.env.PORT || '4000');
const CORS_ORIGIN = process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000'];

// ============================================================================
// Prisma Client
// ============================================================================

const prisma = new PrismaClient({
    log: ['error', 'warn'],
});

// ============================================================================
// DataLoader Factory Functions
// ============================================================================

function createUserLoader() {
    return new DataLoader<string, User | null>(async (ids) => {
        const users = await prisma.user.findMany({
            where: { id: { in: [...ids] } },
        });

        const userMap = new Map(users.map(user => [user.id, user]));
        return ids.map(id => userMap.get(id) || null);
    });
}

function createPostLoader() {
    return new DataLoader(async (ids: readonly string[]) => {
        const posts = await prisma.post.findMany({
            where: { id: { in: [...ids] } },
        });

        const postMap = new Map(posts.map(post => [post.id, post]));
        return ids.map(id => postMap.get(id) || null);
    });
}

function createCommentsByPostLoader() {
    return new DataLoader(async (postIds: readonly string[]) => {
        const comments = await prisma.comment.findMany({
            where: { postId: { in: [...postIds] } },
            orderBy: { createdAt: 'desc' },
        });

        const commentsByPost = new Map<string, typeof comments>();
        for (const postId of postIds) {
            commentsByPost.set(postId, []);
        }
        for (const comment of comments) {
            commentsByPost.get(comment.postId)?.push(comment);
        }

        return postIds.map(id => commentsByPost.get(id) || []);
    });
}

// ============================================================================
// Context Type
// ============================================================================

export interface Context {
    userId?: string;
    prisma: PrismaClient;
    loaders: {
        user: DataLoader<string, User | null>;
        post: DataLoader<string, any>;
        commentsByPost: DataLoader<string, any[]>;
    };
}

// ============================================================================
// Create Context Function
// ============================================================================

async function createContext({ req }: { req: express.Request }): Promise<Context> {
    const authHeader = req.headers.authorization || '';
    let userId: string | undefined;

    if (authHeader.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        try {
            const payload = verifyToken(token);
            userId = payload.userId;
        } catch (error) {
            console.error('Invalid token:', error);
        }
    }

    return {
        userId,
        prisma,
        loaders: {
            user: createUserLoader(),
            post: createPostLoader(),
            commentsByPost: createCommentsByPostLoader(),
        },
    };
}

// ============================================================================
// WebSocket Context (for Subscriptions)
// ============================================================================

async function createWSContext(ctx: any): Promise<Context> {
    const token = ctx.connectionParams?.authentication;
    let userId: string | undefined;

    if (token) {
        try {
            const payload = verifyToken(token);
            userId = payload.userId;
        } catch (error) {
            console.error('Invalid WebSocket token:', error);
        }
    }

    return {
        userId,
        prisma,
        loaders: {
            user: createUserLoader(),
            post: createPostLoader(),
            commentsByPost: createCommentsByPostLoader(),
        },
    };
}

// ============================================================================
// Express & HTTP Server Setup
// ============================================================================

const app = express();
const httpServer = createServer(app);

// ============================================================================
// GraphQL Schema
// ============================================================================

const schema = makeExecutableSchema({
    typeDefs,
    resolvers,
});

// ============================================================================
// WebSocket Server (for Subscriptions)
// ============================================================================

const wsServer = new WebSocketServer({
    server: httpServer,
    path: '/graphql',
});

const serverCleanup = useServer(
    {
        schema,
        context: createWSContext,
    },
    wsServer
);

// ============================================================================
// Apollo Server
// ============================================================================

const server = new ApolloServer<Context>({
    schema,
    plugins: [
        // Proper shutdown for HTTP server
        ApolloServerPluginDrainHttpServer({ httpServer }),

        // Proper shutdown for WebSocket server
        {
            async serverWillStart() {
                return {
                    async drainServer() {
                        await serverCleanup.dispose();
                    },
                };
            },
        },
    ],
    introspection: process.env.GRAPHQL_INTROSPECTION === 'true',
    formatError: (error) => {
        console.error('GraphQL Error:', error);

        // Don't expose internal errors in production
        if (process.env.NODE_ENV === 'production') {
            return {
                message: error.message,
                locations: error.locations,
                path: error.path,
            };
        }

        return error;
    },
});

// ============================================================================
// Start Server
// ============================================================================

async function startServer() {
    await server.start();

    // Apply middleware
    app.use(
        '/graphql',
        cors<cors.CorsRequest>({
            origin: CORS_ORIGIN,
            credentials: true,
        }),
        express.json(),
        expressMiddleware(server, {
            context: createContext,
        })
    );

    // Health check endpoint
    app.get('/health', async (req, res) => {
        try {
            await prisma.$queryRaw`SELECT 1`;
            res.json({
                status: 'healthy',
                database: 'connected',
                timestamp: new Date().toISOString(),
            });
        } catch (error) {
            res.status(503).json({
                status: 'unhealthy',
                error: error instanceof Error ? error.message : 'Unknown error',
            });
        }
    });

    // Apollo Server health check
    app.get('/.well-known/apollo/server-health', (req, res) => {
        res.json({ status: 'pass' });
    });

    // Start HTTP server
    await new Promise<void>((resolve) => {
        httpServer.listen(PORT, resolve);
    });

    console.log(`🚀 Server ready at http://localhost:${PORT}/graphql`);
    console.log(`🔌 Subscriptions ready at ws://localhost:${PORT}/graphql`);
}

// ============================================================================
// Graceful Shutdown
// ============================================================================

async function shutdown() {
    console.log('Shutting down gracefully...');

    try {
        await server.stop();
        await prisma.$disconnect();
        httpServer.close();
        console.log('Shutdown complete');
        process.exit(0);
    } catch (error) {
        console.error('Error during shutdown:', error);
        process.exit(1);
    }
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Start the server
startServer().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
});
