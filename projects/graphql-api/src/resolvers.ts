/**
 * GraphQL Resolvers
 */

import { PubSub } from 'graphql-subscriptions';
import { GraphQLError } from 'graphql';
import { DateTimeResolver } from 'graphql-scalars';
import bcrypt from 'bcryptjs';
import { generateToken } from './utils/auth';
import type { Context } from './index';

const pubsub = new PubSub();

// ============================================================================
// Helper Functions
// ============================================================================

function requireAuth(context: Context) {
    if (!context.userId) {
        throw new GraphQLError('Not authenticated', {
            extensions: { code: 'UNAUTHENTICATED' },
        });
    }
    return context.userId;
}

async function getCurrentUser(context: Context) {
    const userId = requireAuth(context);
    return context.prisma.user.findUniqueOrThrow({
        where: { id: userId },
    });
}

// ============================================================================
// Resolvers
// ============================================================================

export const resolvers = {
    DateTime: DateTimeResolver,

    Query: {
        me: async (_: any, __: any, context: Context) => {
            const userId = requireAuth(context);
            return context.loaders.user.load(userId);
        },

        user: async (_: any, { id }: { id: string }, context: Context) => {
            return context.loaders.user.load(id);
        },

        users: async (_: any, { limit = 20, offset = 0 }: { limit?: number; offset?: number }, context: Context) => {
            return context.prisma.user.findMany({
                take: limit,
                skip: offset,
                orderBy: { createdAt: 'desc' },
            });
        },

        post: async (_: any, { id }: { id: string }, context: Context) => {
            return context.loaders.post.load(id);
        },

        posts: async (_: any, { published, limit = 20, offset = 0 }: any, context: Context) => {
            return context.prisma.post.findMany({
                where: published !== undefined ? { published } : undefined,
                take: limit,
                skip: offset,
                orderBy: { createdAt: 'desc' },
            });
        },

        postsByAuthor: async (_: any, { authorId, limit = 20, offset = 0 }: any, context: Context) => {
            return context.prisma.post.findMany({
                where: { authorId },
                take: limit,
                skip: offset,
                orderBy: { createdAt: 'desc' },
            });
        },

        feed: async (_: any, { limit = 20, offset = 0 }: { limit?: number; offset?: number }, context: Context) => {
            const userId = requireAuth(context);

            // Get users that current user follows
            const following = await context.prisma.follow.findMany({
                where: { followerId: userId },
                select: { followingId: true },
            });

            const followingIds = following.map(f => f.followingId);

            // Get posts from followed users
            return context.prisma.post.findMany({
                where: {
                    authorId: { in: followingIds },
                    published: true,
                },
                take: limit,
                skip: offset,
                orderBy: { publishedAt: 'desc' },
            });
        },

        commentsByPost: async (_: any, { postId, limit = 20, offset = 0 }: any, context: Context) => {
            return context.prisma.comment.findMany({
                where: { postId },
                take: limit,
                skip: offset,
                orderBy: { createdAt: 'desc' },
            });
        },
    },

    Mutation: {
        signup: async (_: any, { input }: any, context: Context) => {
            const { email, username, password } = input;

            // Check if user exists
            const existingUser = await context.prisma.user.findFirst({
                where: {
                    OR: [{ email }, { username }],
                },
            });

            if (existingUser) {
                throw new GraphQLError('User already exists', {
                    extensions: { code: 'BAD_USER_INPUT' },
                });
            }

            // Hash password
            const passwordHash = await bcrypt.hash(password, 10);

            // Create user
            const user = await context.prisma.user.create({
                data: {
                    email,
                    username,
                    passwordHash,
                },
            });

            // Generate token
            const token = generateToken(user);

            return { token, user };
        },

        login: async (_: any, { input }: any, context: Context) => {
            const { email, password } = input;

            // Find user
            const user = await context.prisma.user.findUnique({
                where: { email },
            });

            if (!user) {
                throw new GraphQLError('Invalid credentials', {
                    extensions: { code: 'UNAUTHENTICATED' },
                });
            }

            // Verify password
            const valid = await bcrypt.compare(password, user.passwordHash);

            if (!valid) {
                throw new GraphQLError('Invalid credentials', {
                    extensions: { code: 'UNAUTHENTICATED' },
                });
            }

            // Generate token
            const token = generateToken(user);

            return { token, user };
        },

        createPost: async (_: any, { input }: any, context: Context) => {
            const userId = requireAuth(context);

            const post = await context.prisma.post.create({
                data: {
                    ...input,
                    authorId: userId,
                    publishedAt: input.published ? new Date() : null,
                },
            });

            if (post.published) {
                pubsub.publish('POST_CREATED', { postCreated: post });
            }

            return post;
        },

        updatePost: async (_: any, { id, input }: any, context: Context) => {
            const userId = requireAuth(context);

            // Check ownership
            const post = await context.prisma.post.findUnique({ where: { id } });

            if (!post || post.authorId !== userId) {
                throw new GraphQLError('Not authorized', {
                    extensions: { code: 'FORBIDDEN' },
                });
            }

            const updatedPost = await context.prisma.post.update({
                where: { id },
                data: input,
            });

            pubsub.publish(\`POST_UPDATED_\${id}\`, { postUpdated: updatedPost });

            return updatedPost;
        },

        deletePost: async (_: any, { id }: { id: string }, context: Context) => {
            const userId = requireAuth(context);

            // Check ownership
            const post = await context.prisma.post.findUnique({ where: { id } });

            if (!post || post.authorId !== userId) {
                throw new GraphQLError('Not authorized', {
                    extensions: { code: 'FORBIDDEN' },
                });
            }

            await context.prisma.post.delete({ where: { id } });

            pubsub.publish('POST_DELETED', { postDeleted: id });

            return true;
        },

        createComment: async (_: any, { input }: any, context: Context) => {
            const userId = requireAuth(context);

            const comment = await context.prisma.comment.create({
                data: {
                    ...input,
                    authorId: userId,
                },
            });

            pubsub.publish(\`COMMENT_ADDED_\${input.postId}\`, { commentAdded: comment });

            return comment;
        },

        followUser: async (_: any, { userId: targetUserId }: { userId: string }, context: Context) => {
            const userId = requireAuth(context);

            if (userId === targetUserId) {
                throw new GraphQLError('Cannot follow yourself', {
                    extensions: { code: 'BAD_USER_INPUT' },
                });
            }

            await context.prisma.follow.create({
                data: {
                    followerId: userId,
                    followingId: targetUserId,
                },
            });

            const user = await context.loaders.user.load(targetUserId);

            pubsub.publish(\`USER_FOLLOWED_\${targetUserId}\`, { userFollowed: user });

            return user!;
        },

        unfollowUser: async (_: any, { userId: targetUserId }: { userId: string }, context: Context) => {
            const userId = requireAuth(context);

            await context.prisma.follow.deleteMany({
                where: {
                    followerId: userId,
                    followingId: targetUserId,
                },
            });

            return context.loaders.user.load(targetUserId);
        },
    },

    Subscription: {
        postCreated: {
            subscribe: () => pubsub.asyncIterator(['POST_CREATED']),
        },

        postUpdated: {
            subscribe: (_: any, { postId }: { postId: string }) => {
                return pubsub.asyncIterator([\`POST_UPDATED_\${postId}\`]);
            },
        },

        postDeleted: {
            subscribe: () => pubsub.asyncIterator(['POST_DELETED']),
        },

        commentAdded: {
            subscribe: (_: any, { postId }: { postId: string }) => {
                return pubsub.asyncIterator([\`COMMENT_ADDED_\${postId}\`]);
            },
        },

        userFollowed: {
            subscribe: (_: any, { userId }: { userId: string }) => {
                return pubsub.asyncIterator([\`USER_FOLLOWED_\${userId}\`]);
            },
        },
    },

    // Field resolvers
    User: {
        posts: async (parent: any, _: any, context: Context) => {
            return context.prisma.post.findMany({
                where: { authorId: parent.id },
                orderBy: { createdAt: 'desc' },
            });
        },

        comments: async (parent: any, _: any, context: Context) => {
            return context.prisma.comment.findMany({
                where: { authorId: parent.id },
                orderBy: { createdAt: 'desc' },
            });
        },

        followers: async (parent: any, _: any, context: Context) => {
            const follows = await context.prisma.follow.findMany({
                where: { followingId: parent.id },
                include: { follower: true },
            });
            return follows.map(f => f.follower);
        },

        following: async (parent: any, _: any, context: Context) => {
            const follows = await context.prisma.follow.findMany({
                where: { followerId: parent.id },
                include: { following: true },
            });
            return follows.map(f => f.following);
        },

        followerCount: async (parent: any, _: any, context: Context) => {
            return context.prisma.follow.count({
                where: { followingId: parent.id },
            });
        },

        followingCount: async (parent: any, _: any, context: Context) => {
            return context.prisma.follow.count({
                where: { followerId: parent.id },
            });
        },
    },

    Post: {
        author: async (parent: any, _: any, context: Context) => {
            // Uses DataLoader - prevents N+1
            return context.loaders.user.load(parent.authorId);
        },

        comments: async (parent: any, _: any, context: Context) => {
            // Uses DataLoader - batches comment queries
            return context.loaders.commentsByPost.load(parent.id);
        },

        commentCount: async (parent: any, _: any, context: Context) => {
            return context.prisma.comment.count({
                where: { postId: parent.id },
            });
        },
    },

    Comment: {
        post: async (parent: any, _: any, context: Context) => {
            return context.loaders.post.load(parent.postId);
        },

        author: async (parent: any, _: any, context: Context) => {
            return context.loaders.user.load(parent.authorId);
        },
    },
};
