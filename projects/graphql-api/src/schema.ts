/**
 * GraphQL Schema Type Definitions
 */

export const typeDefs = `#graphql
  # ============================================================================
  # Scalar Types
  # ============================================================================

  scalar DateTime

  # ============================================================================
  # Types
  # ============================================================================

  type User {
    id: ID!
    email: String!
    username: String!
    bio: String
    avatarUrl: String
    posts: [Post!]!
    comments: [Comment!]!
    followers: [User!]!
    following: [User!]!
    followerCount: Int!
    followingCount: Int!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    published: Boolean!
    viewCount: Int!
    author: User!
    comments: [Comment!]!
    commentCount: Int!
    createdAt: DateTime!
    updatedAt: DateTime!
    publishedAt: DateTime
  }

  type Comment {
    id: ID!
    content: String!
    post: Post!
    author: User!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  # ============================================================================
  # Inputs
  # ============================================================================

  input SignupInput {
    email: String!
    username: String!
    password: String!
  }

  input LoginInput {
    email: String!
    password: String!
  }

  input CreatePostInput {
    title: String!
    content: String!
    published: Boolean
  }

  input UpdatePostInput {
    title: String
    content: String
    published: Boolean
  }

  input CreateCommentInput {
    postId: ID!
    content: String!
  }

  # ============================================================================
  # Queries
  # ============================================================================

  type Query {
    # User queries
    me: User
    user(id: ID!): User
    users(limit: Int, offset: Int): [User!]!

    # Post queries
    post(id: ID!): Post
    posts(published: Boolean, limit: Int, offset: Int): [Post!]!
    postsByAuthor(authorId: ID!, limit: Int, offset: Int): [Post!]!
    feed(limit: Int, offset: Int): [Post!]!

    # Comment queries
    comment(id: ID!): Comment
    commentsByPost(postId: ID!, limit: Int, offset: Int): [Comment!]!
  }

  # ============================================================================
  # Mutations
  # ============================================================================

  type Mutation {
    # Authentication
    signup(input: SignupInput!): AuthPayload!
    login(input: LoginInput!): AuthPayload!

    # User mutations
    updateProfile(bio: String, avatarUrl: String): User!
    followUser(userId: ID!): User!
    unfollowUser(userId: ID!): User!

    # Post mutations
    createPost(input: CreatePostInput!): Post!
    updatePost(id: ID!, input: UpdatePostInput!): Post!
    deletePost(id: ID!): Boolean!
    publishPost(id: ID!): Post!

    # Comment mutations
    createComment(input: CreateCommentInput!): Comment!
    updateComment(id: ID!, content: String!): Comment!
    deleteComment(id: ID!): Boolean!
  }

  # ============================================================================
  # Subscriptions
  # ============================================================================

  type Subscription {
    # Real-time post updates
    postCreated: Post!
    postUpdated(postId: ID!): Post!
    postDeleted: ID!

    # Real-time comment updates
    commentAdded(postId: ID!): Comment!
    commentUpdated(commentId: ID!): Comment!

    # User activity
    userFollowed(userId: ID!): User!
  }
`;
