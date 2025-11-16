/**
 * Real-Time Chat System
 * WebSocket-based chat with Kafka message queue and Redis pub/sub
 */

import express from 'express';
import { createServer } from 'http';
import { Server, Socket } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import Redis from 'ioredis';
import { Kafka, Producer, Consumer } from 'kafkajs';
import { Pool } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
    port: parseInt(process.env.PORT || '3000'),
    database: {
        url: process.env.DATABASE_URL || 'postgresql://chatuser:password@localhost:5432/chatdb',
        pool: {
            min: 2,
            max: 20,
            idleTimeoutMillis: 30000,
            connectionTimeoutMillis: 2000,
        },
    },
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
    },
    kafka: {
        brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(','),
        clientId: process.env.KAFKA_CLIENT_ID || 'chat-server',
        groupId: process.env.KAFKA_GROUP_ID || 'chat-consumers',
        topics: {
            messages: process.env.KAFKA_TOPIC_MESSAGES || 'chat-messages',
            analytics: process.env.KAFKA_TOPIC_ANALYTICS || 'chat-analytics',
        },
    },
    websocket: {
        cors: {
            origin: process.env.WS_CORS_ORIGIN?.split(',') || ['http://localhost:3000'],
            credentials: true,
        },
        maxConnections: parseInt(process.env.WS_MAX_CONNECTIONS || '10000'),
        pingTimeout: parseInt(process.env.WS_PING_TIMEOUT || '5000'),
        pingInterval: parseInt(process.env.WS_PING_INTERVAL || '25000'),
    },
    rateLimit: {
        window: parseInt(process.env.RATE_LIMIT_WINDOW || '60000'),
        maxMessages: parseInt(process.env.RATE_LIMIT_MAX_MESSAGES || '60'),
    },
};

// ============================================================================
// Logger Setup
// ============================================================================

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console({
            format: winston.format.simple(),
        }),
    ],
});

// ============================================================================
// Database Setup
// ============================================================================

const db = new Pool({
    connectionString: CONFIG.database.url,
    ...CONFIG.database.pool,
});

db.on('error', (err) => {
    logger.error('Database error:', err);
});

// ============================================================================
// Redis Setup (Pub/Sub + Adapter)
// ============================================================================

const redisPub = new Redis(CONFIG.redis);
const redisSub = new Redis(CONFIG.redis);

redisPub.on('error', (err) => logger.error('Redis Pub error:', err));
redisSub.on('error', (err) => logger.error('Redis Sub error:', err));

// ============================================================================
// Kafka Setup
// ============================================================================

const kafka = new Kafka({
    clientId: CONFIG.kafka.clientId,
    brokers: CONFIG.kafka.brokers,
    retry: {
        initialRetryTime: 100,
        retries: 8,
    },
});

const producer: Producer = kafka.producer();
const consumer: Consumer = kafka.consumer({ groupId: CONFIG.kafka.groupId });

// ============================================================================
// Express & Socket.IO Setup
// ============================================================================

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: CONFIG.websocket.cors,
    pingTimeout: CONFIG.websocket.pingTimeout,
    pingInterval: CONFIG.websocket.pingInterval,
});

// Use Redis adapter for multi-server support
io.adapter(createAdapter(redisPub, redisSub));

// ============================================================================
// Middleware
// ============================================================================

app.use(express.json());

// Health check endpoint
app.get('/health', async (req, res) => {
    try {
        // Check database
        await db.query('SELECT 1');

        // Check Redis
        await redisPub.ping();

        // Check Kafka (producer)
        const metadata = await producer.describeGroup();

        res.json({
            status: 'healthy',
            database: 'connected',
            redis: 'connected',
            kafka: 'connected',
            connections: io.sockets.sockets.size,
            timestamp: new Date().toISOString(),
        });
    } catch (error) {
        logger.error('Health check failed:', error);
        res.status(503).json({
            status: 'unhealthy',
            error: error instanceof Error ? error.message : 'Unknown error',
        });
    }
});

// ============================================================================
// Types
// ============================================================================

interface Message {
    id: string;
    roomId: string;
    userId: string;
    username: string;
    content: string;
    type: 'text' | 'image' | 'file';
    timestamp: Date;
}

interface RateLimitData {
    count: number;
    resetTime: number;
}

// ============================================================================
// Rate Limiting
// ============================================================================

const rateLimitMap = new Map<string, RateLimitData>();

function checkRateLimit(userId: string): boolean {
    const now = Date.now();
    const userLimit = rateLimitMap.get(userId);

    if (!userLimit || now > userLimit.resetTime) {
        rateLimitMap.set(userId, {
            count: 1,
            resetTime: now + CONFIG.rateLimit.window,
        });
        return true;
    }

    if (userLimit.count >= CONFIG.rateLimit.maxMessages) {
        return false;
    }

    userLimit.count++;
    return true;
}

// Cleanup rate limit map every minute
setInterval(() => {
    const now = Date.now();
    for (const [userId, data] of rateLimitMap.entries()) {
        if (now > data.resetTime) {
            rateLimitMap.delete(userId);
        }
    }
}, 60000);

// ============================================================================
// Database Operations
// ============================================================================

async function saveMessage(message: Message): Promise<void> {
    const query = `
        INSERT INTO messages (id, room_id, user_id, content, message_type, created_at)
        VALUES ($1, $2, $3, $4, $5, $6)
    `;

    await db.query(query, [
        message.id,
        message.roomId,
        message.userId,
        message.content,
        message.type,
        message.timestamp,
    ]);
}

async function getMessageHistory(roomId: string, limit: number = 100): Promise<Message[]> {
    const query = `
        SELECT m.id, m.room_id, m.user_id, u.username, m.content, m.message_type, m.created_at
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.room_id = $1 AND m.is_deleted = false
        ORDER BY m.created_at DESC
        LIMIT $2
    `;

    const result = await db.query(query, [roomId, limit]);

    return result.rows.map(row => ({
        id: row.id,
        roomId: row.room_id,
        userId: row.user_id,
        username: row.username,
        content: row.content,
        type: row.message_type,
        timestamp: row.created_at,
    }));
}

// ============================================================================
// Kafka Producer Functions
// ============================================================================

async function publishMessage(message: Message): Promise<void> {
    try {
        await producer.send({
            topic: CONFIG.kafka.topics.messages,
            messages: [
                {
                    key: message.roomId,  // Same room → same partition
                    value: JSON.stringify(message),
                    headers: {
                        'message-id': message.id,
                        'timestamp': message.timestamp.toISOString(),
                    },
                },
            ],
        });

        logger.info(`Message published to Kafka: ${message.id}`);
    } catch (error) {
        logger.error('Failed to publish message to Kafka:', error);
        throw error;
    }
}

// ============================================================================
// WebSocket Event Handlers
// ============================================================================

function handleConnection(socket: Socket) {
    const userId = socket.handshake.auth.userId || socket.id;
    const username = socket.handshake.auth.username || 'Anonymous';

    logger.info(`User connected: ${userId} (${socket.id})`);

    // Join room
    socket.on('join_room', async ({ roomId }) => {
        try {
            socket.join(roomId);
            logger.info(`User ${userId} joined room ${roomId}`);

            // Send message history
            const history = await getMessageHistory(roomId);
            socket.emit('message_history', history);

            // Broadcast user joined
            socket.to(roomId).emit('user_joined', {
                roomId,
                userId,
                username,
                timestamp: new Date(),
            });

            // Update presence
            await redisPub.sadd(`room:${roomId}:members`, userId);
            await redisPub.setex(`user:${userId}:online`, 30, '1');
        } catch (error) {
            logger.error('Error joining room:', error);
            socket.emit('error', { message: 'Failed to join room' });
        }
    });

    // Leave room
    socket.on('leave_room', async ({ roomId }) => {
        try {
            socket.leave(roomId);
            logger.info(`User ${userId} left room ${roomId}`);

            // Broadcast user left
            socket.to(roomId).emit('user_left', {
                roomId,
                userId,
                timestamp: new Date(),
            });

            // Update presence
            await redisPub.srem(`room:${roomId}:members`, userId);
        } catch (error) {
            logger.error('Error leaving room:', error);
        }
    });

    // Send message
    socket.on('send_message', async ({ roomId, content, type = 'text' }) => {
        try {
            // Rate limiting
            if (!checkRateLimit(userId)) {
                socket.emit('error', {
                    code: 'RATE_LIMIT_EXCEEDED',
                    message: 'Too many messages. Please slow down.',
                });
                return;
            }

            // Create message
            const message: Message = {
                id: uuidv4(),
                roomId,
                userId,
                username,
                content,
                type,
                timestamp: new Date(),
            };

            // Publish to Kafka (durability + delivery guarantee)
            await publishMessage(message);

            // Broadcast via Redis Pub/Sub (low latency)
            await redisPub.publish(`room:${roomId}`, JSON.stringify({
                event: 'message',
                data: message,
            }));

            // Save to database (async)
            saveMessage(message).catch(err => {
                logger.error('Failed to save message to database:', err);
            });

            logger.info(`Message sent: ${message.id} in room ${roomId}`);
        } catch (error) {
            logger.error('Error sending message:', error);
            socket.emit('error', { message: 'Failed to send message' });
        }
    });

    // Typing indicators
    socket.on('typing_start', async ({ roomId }) => {
        await redisPub.setex(`room:${roomId}:typing:${userId}`, 5, username);
        socket.to(roomId).emit('typing', { roomId, userId, username });
    });

    socket.on('typing_stop', async ({ roomId }) => {
        await redisPub.del(`room:${roomId}:typing:${userId}`);
        socket.to(roomId).emit('typing_stop', { roomId, userId });
    });

    // Disconnect
    socket.on('disconnect', async (reason) => {
        logger.info(`User disconnected: ${userId} (${reason})`);

        // Remove from all rooms
        const rooms = Array.from(socket.rooms).filter(r => r !== socket.id);
        for (const roomId of rooms) {
            await redisPub.srem(`room:${roomId}:members`, userId);
        }

        // Update presence
        await redisPub.del(`user:${userId}:online`);
    });
}

// Register connection handler
io.on('connection', handleConnection);

// ============================================================================
// Redis Pub/Sub Listener (Inter-Server Communication)
// ============================================================================

redisSub.psubscribe('room:*', (err) => {
    if (err) {
        logger.error('Failed to subscribe to Redis channels:', err);
    } else {
        logger.info('Subscribed to Redis room channels');
    }
});

redisSub.on('pmessage', (pattern, channel, message) => {
    try {
        const { event, data } = JSON.parse(message);
        const roomId = channel.split(':')[1];

        // Emit to all clients in the room
        io.to(`room:${roomId}`).emit(event, data);
    } catch (error) {
        logger.error('Error processing Redis message:', error);
    }
});

// ============================================================================
// Kafka Consumer (Message Processing)
// ============================================================================

async function startKafkaConsumer() {
    await consumer.connect();
    await consumer.subscribe({ topic: CONFIG.kafka.topics.messages, fromBeginning: false });

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            try {
                const messageData: Message = JSON.parse(message.value?.toString() || '{}');

                logger.info(`Consumed message from Kafka: ${messageData.id}`);

                // Process message (e.g., analytics, notifications)
                // For now, we've already broadcasted via Redis Pub/Sub
                // This consumer can be used for:
                // - Message persistence confirmation
                // - Analytics processing
                // - Push notifications
                // - Email notifications

            } catch (error) {
                logger.error('Error consuming Kafka message:', error);
            }
        },
    });

    logger.info('Kafka consumer started');
}

// ============================================================================
// Application Startup
// ============================================================================

async function start() {
    try {
        // Connect to Kafka producer
        await producer.connect();
        logger.info('Kafka producer connected');

        // Start Kafka consumer
        await startKafkaConsumer();

        // Start HTTP server
        httpServer.listen(CONFIG.port, () => {
            logger.info(`Chat server running on port ${CONFIG.port}`);
            logger.info(`WebSocket connections: 0/${CONFIG.websocket.maxConnections}`);
        });

        // Connection count monitoring
        setInterval(() => {
            const connections = io.sockets.sockets.size;
            logger.info(`Active WebSocket connections: ${connections}`);

            // Emit connection metrics
            if (connections > CONFIG.websocket.maxConnections * 0.8) {
                logger.warn(`High connection count: ${connections}/${CONFIG.websocket.maxConnections}`);
            }
        }, 60000);

    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

// ============================================================================
// Graceful Shutdown
// ============================================================================

async function shutdown() {
    logger.info('Shutting down gracefully...');

    try {
        // Close WebSocket connections
        io.close();

        // Disconnect Kafka
        await producer.disconnect();
        await consumer.disconnect();

        // Close Redis connections
        redisPub.disconnect();
        redisSub.disconnect();

        // Close database pool
        await db.end();

        logger.info('Shutdown complete');
        process.exit(0);
    } catch (error) {
        logger.error('Error during shutdown:', error);
        process.exit(1);
    }
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Start the application
start();
