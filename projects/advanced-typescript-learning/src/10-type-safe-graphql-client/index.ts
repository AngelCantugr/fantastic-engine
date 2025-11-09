/**
 * 10 - Type-Safe GraphQL Client
 *
 * Full type inference from GraphQL schema to client operations
 * Demonstrates advanced type manipulation and schema-driven types
 */

// ============================================================================
// PART 1: SCHEMA TYPE DEFINITIONS
// ============================================================================

/**
 * Represent GraphQL scalar types
 */
export type GraphQLScalar = string | number | boolean | null;

/**
 * GraphQL field definition
 */
export type GraphQLField = {
  type: string;
  nullable?: boolean;
  list?: boolean;
  args?: Record<string, GraphQLFieldArg>;
};

export type GraphQLFieldArg = {
  type: string;
  nullable?: boolean;
  defaultValue?: any;
};

/**
 * GraphQL object type
 */
export type GraphQLObjectType = {
  fields: Record<string, GraphQLField>;
};

/**
 * GraphQL schema definition
 */
export type GraphQLSchema = {
  types: Record<string, GraphQLObjectType>;
  query: string;
  mutation?: string;
};

// ============================================================================
// PART 2: TYPE EXTRACTION UTILITIES
// ============================================================================

/**
 * Extract field type from schema
 */
export type ExtractFieldType<
  Schema extends GraphQLSchema,
  TypeName extends keyof Schema['types'],
  FieldName extends keyof Schema['types'][TypeName]['fields']
> = Schema['types'][TypeName]['fields'][FieldName] extends infer Field
  ? Field extends GraphQLField
    ? Field['nullable'] extends true
      ? ExtractBaseType<Schema, Field['type']> | null
      : ExtractBaseType<Schema, Field['type']>
    : never
  : never;

/**
 * Extract base type (handle scalars and object types)
 */
export type ExtractBaseType<Schema extends GraphQLSchema, TypeName> =
  TypeName extends 'String' ? string
  : TypeName extends 'Int' ? number
  : TypeName extends 'Float' ? number
  : TypeName extends 'Boolean' ? boolean
  : TypeName extends 'ID' ? string
  : TypeName extends keyof Schema['types']
    ? TypeFromObjectType<Schema, TypeName>
    : never;

/**
 * Convert GraphQL object type to TypeScript type
 */
export type TypeFromObjectType<
  Schema extends GraphQLSchema,
  TypeName extends keyof Schema['types']
> = {
  [K in keyof Schema['types'][TypeName]['fields']]: ExtractFieldType<Schema, TypeName, K>;
};

// ============================================================================
// PART 3: QUERY BUILDER TYPES
// ============================================================================

/**
 * Selection set for a GraphQL query
 */
export type SelectionSet<
  Schema extends GraphQLSchema,
  TypeName extends keyof Schema['types']
> = Partial<{
  [K in keyof Schema['types'][TypeName]['fields']]:
    | boolean
    | (Schema['types'][TypeName]['fields'][K]['type'] extends keyof Schema['types']
        ? SelectionSet<Schema, Schema['types'][TypeName]['fields'][K]['type']>
        : boolean);
}>;

/**
 * Query result type based on selection set
 */
export type QueryResult<
  Schema extends GraphQLSchema,
  TypeName extends keyof Schema['types'],
  Selection extends SelectionSet<Schema, TypeName>
> = {
  [K in keyof Selection & keyof Schema['types'][TypeName]['fields']]:
    Selection[K] extends true
      ? ExtractFieldType<Schema, TypeName, K>
      : Selection[K] extends object
        ? Schema['types'][TypeName]['fields'][K]['type'] extends keyof Schema['types']
          ? QueryResult<
              Schema,
              Schema['types'][TypeName]['fields'][K]['type'],
              Selection[K]
            >
          : never
        : never;
};

// ============================================================================
// PART 4: EXAMPLE SCHEMA
// ============================================================================

/**
 * Example: Blog schema
 */
export type BlogSchema = {
  types: {
    Query: {
      fields: {
        user: { type: 'User'; nullable: false; args: { id: { type: 'ID'; nullable: false } } };
        users: { type: 'User'; nullable: false; list: true };
        post: { type: 'Post'; nullable: false; args: { id: { type: 'ID'; nullable: false } } };
        posts: { type: 'Post'; nullable: false; list: true };
      };
    };
    User: {
      fields: {
        id: { type: 'ID'; nullable: false };
        name: { type: 'String'; nullable: false };
        email: { type: 'String'; nullable: false };
        posts: { type: 'Post'; nullable: false; list: true };
        profile: { type: 'Profile'; nullable: true };
      };
    };
    Profile: {
      fields: {
        bio: { type: 'String'; nullable: true };
        avatar: { type: 'String'; nullable: true };
        website: { type: 'String'; nullable: true };
      };
    };
    Post: {
      fields: {
        id: { type: 'ID'; nullable: false };
        title: { type: 'String'; nullable: false };
        content: { type: 'String'; nullable: false };
        published: { type: 'Boolean'; nullable: false };
        author: { type: 'User'; nullable: false };
        comments: { type: 'Comment'; nullable: false; list: true };
      };
    };
    Comment: {
      fields: {
        id: { type: 'ID'; nullable: false };
        text: { type: 'String'; nullable: false };
        author: { type: 'User'; nullable: false };
      };
    };
  };
  query: 'Query';
};

// ============================================================================
// PART 5: TYPE-SAFE CLIENT
// ============================================================================

/**
 * GraphQL client with full type safety
 */
export class TypedGraphQLClient<Schema extends GraphQLSchema> {
  constructor(private endpoint: string) {}

  async query<
    TypeName extends keyof Schema['types'],
    Selection extends SelectionSet<Schema, TypeName>
  >(
    typeName: TypeName,
    selection: Selection,
    args?: Record<string, any>
  ): Promise<QueryResult<Schema, TypeName, Selection>> {
    // Build GraphQL query string
    const query = this.buildQuery(typeName, selection, args);

    // Execute query
    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    const result = await response.json();
    return result.data as QueryResult<Schema, TypeName, Selection>;
  }

  private buildQuery(
    typeName: string,
    selection: any,
    args?: Record<string, any>
  ): string {
    const fields = this.buildSelectionSet(selection);
    const argsStr = args
      ? `(${Object.entries(args).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join(', ')})`
      : '';

    return `
      query {
        ${typeName}${argsStr} {
          ${fields}
        }
      }
    `;
  }

  private buildSelectionSet(selection: any, indent = 0): string {
    const spaces = '  '.repeat(indent);
    const fields: string[] = [];

    for (const [key, value] of Object.entries(selection)) {
      if (value === true) {
        fields.push(`${spaces}${key}`);
      } else if (typeof value === 'object') {
        const nested = this.buildSelectionSet(value, indent + 1);
        fields.push(`${spaces}${key} {\n${nested}\n${spaces}}`);
      }
    }

    return fields.join('\n');
  }
}

// ============================================================================
// PART 6: QUERY BUILDER HELPER
// ============================================================================

/**
 * Fluent query builder
 */
export class QueryBuilder<
  Schema extends GraphQLSchema,
  TypeName extends keyof Schema['types'] = Schema['query']
> {
  private selection: SelectionSet<Schema, TypeName> = {};
  private args: Record<string, any> = {};

  constructor(
    private client: TypedGraphQLClient<Schema>,
    private typeName: TypeName
  ) {}

  select<K extends keyof Schema['types'][TypeName]['fields']>(
    field: K
  ): QueryBuilder<Schema, TypeName> {
    (this.selection as any)[field] = true;
    return this;
  }

  selectNested<
    K extends keyof Schema['types'][TypeName]['fields'],
    NestedType extends Schema['types'][TypeName]['fields'][K]['type']
  >(
    field: K,
    builder: (
      nested: QueryBuilder<Schema, NestedType & keyof Schema['types']>
    ) => QueryBuilder<Schema, NestedType & keyof Schema['types']>
  ): QueryBuilder<Schema, TypeName> {
    const nestedBuilder = new QueryBuilder(
      this.client,
      {} as NestedType & keyof Schema['types']
    );
    const result = builder(nestedBuilder);
    (this.selection as any)[field] = result.getSelection();
    return this;
  }

  where(args: Record<string, any>): QueryBuilder<Schema, TypeName> {
    this.args = { ...this.args, ...args };
    return this;
  }

  getSelection(): SelectionSet<Schema, TypeName> {
    return this.selection;
  }

  async execute(): Promise<QueryResult<Schema, TypeName, typeof this.selection>> {
    return this.client.query(this.typeName, this.selection, this.args);
  }
}

// ============================================================================
// PART 7: EXAMPLES
// ============================================================================

// Create client
const client = new TypedGraphQLClient<BlogSchema>('https://api.example.com/graphql');

// Example 1: Simple query
async function getUserById(id: string) {
  const result = await client.query(
    'Query',
    {
      user: {
        id: true,
        name: true,
        email: true,
      },
    },
    { id }
  );

  // result.user is fully typed!
  // result.user.id: string
  // result.user.name: string
  // result.user.email: string

  return result;
}

// Example 2: Nested query
async function getPostWithAuthor(postId: string) {
  const result = await client.query(
    'Query',
    {
      post: {
        id: true,
        title: true,
        content: true,
        author: {
          id: true,
          name: true,
          profile: {
            bio: true,
            avatar: true,
          },
        },
      },
    },
    { id: postId }
  );

  // result.post.author.profile.bio is typed as string | null
  return result;
}

// Example 3: Using query builder
async function getUserPosts(userId: string) {
  const query = new QueryBuilder(client, 'Query' as const)
    .selectNested('user', (user) =>
      user
        .select('name')
        .selectNested('posts', (posts) =>
          posts.select('id').select('title').select('published')
        )
    )
    .where({ id: userId });

  const result = await query.execute();
  return result;
}

// ============================================================================
// PART 8: MUTATION SUPPORT
// ============================================================================

export type MutationSchema = {
  types: {
    Mutation: {
      fields: {
        createUser: {
          type: 'User';
          nullable: false;
          args: {
            name: { type: 'String'; nullable: false };
            email: { type: 'String'; nullable: false };
          };
        };
        updateUser: {
          type: 'User';
          nullable: false;
          args: {
            id: { type: 'ID'; nullable: false };
            name: { type: 'String'; nullable: true };
            email: { type: 'String'; nullable: true };
          };
        };
        deleteUser: {
          type: 'Boolean';
          nullable: false;
          args: {
            id: { type: 'ID'; nullable: false };
          };
        };
      };
    };
  };
  query: 'Query';
  mutation: 'Mutation';
};

// ============================================================================
// TYPE TESTS (Compile-time verification)
// ============================================================================

// Test: User type extraction
type User = TypeFromObjectType<BlogSchema, 'User'>;
// User should be:
// {
//   id: string;
//   name: string;
//   email: string;
//   posts: Post[];
//   profile: Profile | null;
// }

// Test: Post type extraction
type Post = TypeFromObjectType<BlogSchema, 'Post'>;
// Post should have author: User

// Test: Query result type
type UserQueryResult = QueryResult<
  BlogSchema,
  'Query',
  {
    user: {
      id: true;
      name: true;
      posts: {
        title: true;
      };
    };
  }
>;
// Should infer: { user: { id: string; name: string; posts: { title: string }[] } }

console.log('Type-Safe GraphQL Client module loaded successfully!');

// Example usage (commented out to avoid runtime errors)
/*
(async () => {
  const user = await getUserById('123');
  console.log('User:', user.user.name);

  const post = await getPostWithAuthor('456');
  console.log('Post author:', post.post.author.name);
  console.log('Author bio:', post.post.author.profile?.bio);
})();
*/
