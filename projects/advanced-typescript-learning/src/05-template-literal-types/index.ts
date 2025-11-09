/**
 * 05 - Template Literal Types
 *
 * Type-level string manipulation using template literal types
 */

// ============================================================================
// PART 1: BASIC TEMPLATE LITERALS
// ============================================================================

/**
 * Create event names with prefixes
 */
export type EventName<T extends string> = `on${Capitalize<T>}`;

type ClickEvent = EventName<'click'>; // "onClick"
type HoverEvent = EventName<'hover'>; // "onHover"

/**
 * HTTP methods with paths
 */
export type HttpEndpoint<Method extends string, Path extends string> = `${Method} ${Path}`;

type GetUsers = HttpEndpoint<'GET', '/users'>; // "GET /users"
type PostUser = HttpEndpoint<'POST', '/users'>; // "POST /users"

// ============================================================================
// PART 2: STRING MANIPULATION UTILITIES
// ============================================================================

/**
 * Capitalize first letter
 */
export type Capitalize<S extends string> = S extends `${infer F}${infer R}`
  ? `${Uppercase<F>}${R}`
  : S;

/**
 * Uncapitalize first letter
 */
export type Uncapitalize<S extends string> = S extends `${infer F}${infer R}`
  ? `${Lowercase<F>}${R}`
  : S;

/**
 * Convert to camelCase
 */
export type CamelCase<S extends string> = S extends `${infer F}_${infer R}`
  ? `${Lowercase<F>}${Capitalize<CamelCase<R>>}`
  : S extends `${infer F}-${infer R}`
  ? `${Lowercase<F>}${Capitalize<CamelCase<R>>}`
  : S;

/**
 * Convert to snake_case
 */
export type SnakeCase<S extends string> = S extends `${infer T}${infer U}`
  ? U extends Uncapitalize<U>
    ? `${Lowercase<T>}${SnakeCase<U>}`
    : `${Lowercase<T>}_${SnakeCase<U>}`
  : S;

/**
 * Convert to kebab-case
 */
export type KebabCase<S extends string> = S extends `${infer T}${infer U}`
  ? U extends Uncapitalize<U>
    ? `${Lowercase<T>}${KebabCase<U>}`
    : `${Lowercase<T>}-${KebabCase<U>}`
  : S;

// ============================================================================
// PART 3: PATH MANIPULATION
// ============================================================================

/**
 * Extract path parameters
 */
export type ExtractPathParams<Path extends string> =
  Path extends `${infer _Start}:${infer Param}/${infer Rest}`
    ? Param | ExtractPathParams<`/${Rest}`>
    : Path extends `${infer _Start}:${infer Param}`
    ? Param
    : never;

type UserIdParam = ExtractPathParams<'/users/:userId/posts/:postId'>; // "userId" | "postId"

/**
 * Create typed route params
 */
export type RouteParams<Path extends string> = {
  [K in ExtractPathParams<Path>]: string;
};

/**
 * Type-safe route builder
 */
export function createRoute<Path extends string>(
  path: Path
): (params: RouteParams<Path>) => string {
  return (params) => {
    let result: string = path;
    for (const [key, value] of Object.entries(params)) {
      result = result.replace(`:${key}`, value);
    }
    return result;
  };
}

// ============================================================================
// PART 4: CSS-IN-JS TYPE SAFETY
// ============================================================================

/**
 * CSS property names
 */
export type CSSProperties = {
  color?: string;
  backgroundColor?: string;
  fontSize?: string;
  padding?: string;
  margin?: string;
};

/**
 * Convert camelCase to kebab-case for CSS
 */
export type CSSPropertyName<T extends string> = KebabCase<T>;

/**
 * Create CSS string from object
 */
export type CSSRule<K extends string, V extends string> = `${CSSPropertyName<K>}: ${V};`;

// ============================================================================
// PART 5: QUERY STRING TYPES
// ============================================================================

/**
 * Parse query string into type
 */
export type ParseQueryString<S extends string> = S extends `${infer Key}=${infer Value}&${infer Rest}`
  ? { [K in Key]: Value } & ParseQueryString<Rest>
  : S extends `${infer Key}=${infer Value}`
  ? { [K in Key]: Value }
  : {};

type Query = ParseQueryString<'name=John&age=30&city=NYC'>;
// { name: "John"; age: "30"; city: "NYC" }

/**
 * Build query string type
 */
export type QueryString<T extends Record<string, string>> = {
  [K in keyof T]: `${K & string}=${T[K]}`;
}[keyof T];

// ============================================================================
// PART 6: BRANDED STRING TYPES
// ============================================================================

/**
 * Create branded string types for type safety
 */
export type Brand<T, B> = T & { __brand: B };

export type Email = Brand<string, 'Email'>;
export type URL = Brand<string, 'URL'>;
export type UUID = Brand<string, 'UUID'>;
export type PhoneNumber = Brand<string, 'PhoneNumber'>;

/**
 * Validators for branded types
 */
export function createEmail(email: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email');
  }
  return email as Email;
}

export function createURL(url: string): URL {
  try {
    new globalThis.URL(url);
    return url as URL;
  } catch {
    throw new Error('Invalid URL');
  }
}

export function createUUID(uuid: string): UUID {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(uuid)) {
    throw new Error('Invalid UUID');
  }
  return uuid as UUID;
}

// ============================================================================
// PART 7: DATABASE QUERY BUILDER
// ============================================================================

/**
 * SQL operations as template literals
 */
export type SQLOperation = 'SELECT' | 'INSERT' | 'UPDATE' | 'DELETE';
export type SQLClause = 'FROM' | 'WHERE' | 'ORDER BY' | 'LIMIT';

export type SQLQuery<
  Op extends SQLOperation,
  Table extends string,
  Condition extends string = ''
> = Condition extends ''
  ? `${Op} * FROM ${Table}`
  : `${Op} * FROM ${Table} WHERE ${Condition}`;

type GetAllUsers = SQLQuery<'SELECT', 'users'>; // "SELECT * FROM users"
type GetActiveUsers = SQLQuery<'SELECT', 'users', 'active = true'>; // "SELECT * FROM users WHERE active = true"

// ============================================================================
// PART 8: PRACTICAL EXAMPLES
// ============================================================================

/**
 * Example 1: Type-safe routing
 */
const getUserRoute = createRoute('/users/:userId/posts/:postId');
const url = getUserRoute({ userId: '123', postId: '456' });
console.log('Route:', url); // /users/123/posts/456

/**
 * Example 2: Event handlers
 */
type MouseEvents = {
  onClick: (e: MouseEvent) => void;
  onMouseOver: (e: MouseEvent) => void;
  onMouseOut: (e: MouseEvent) => void;
};

/**
 * Example 3: Branded types
 */
function sendEmail(to: Email, subject: string, body: string): void {
  console.log(`Sending email to ${to}: ${subject}`);
}

const email = createEmail('user@example.com');
sendEmail(email, 'Hello', 'World');

// This won't compile:
// sendEmail('invalid', 'Hello', 'World');

/**
 * Example 4: Type-safe CSS
 */
type ButtonStyle = CSSRule<'backgroundColor', 'blue'> | CSSRule<'color', 'white'>;

/**
 * Example 5: API route types
 */
type APIRoutes = {
  'GET /users': { response: { id: number; name: string }[] };
  'GET /users/:id': { params: { id: string }; response: { id: number; name: string } };
  'POST /users': { body: { name: string; email: string }; response: { id: number } };
  'DELETE /users/:id': { params: { id: string }; response: { success: boolean } };
};

console.log('Template Literal Types module loaded successfully!');
