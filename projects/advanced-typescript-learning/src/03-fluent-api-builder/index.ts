/**
 * 03 - Fluent API Builder
 *
 * Demonstrates method chaining, type accumulation, and the builder pattern
 * with full type safety and state tracking.
 */

// ============================================================================
// BASIC FLUENT BUILDER
// ============================================================================

/**
 * Basic QueryBuilder with method chaining
 */
export class QueryBuilder<T = any> {
  private _select: string[] = [];
  private _from?: string;
  private _where: string[] = [];
  private _limit?: number;

  select(...fields: (keyof T)[]): this {
    this._select.push(...(fields as string[]));
    return this;
  }

  from(table: string): this {
    this._from = table;
    return this;
  }

  where(condition: string): this {
    this._where.push(condition);
    return this;
  }

  limit(count: number): this {
    this._limit = count;
    return this;
  }

  build(): string {
    const select = this._select.length > 0 ? this._select.join(', ') : '*';
    let query = `SELECT ${select}`;

    if (this._from) {
      query += ` FROM ${this._from}`;
    }

    if (this._where.length > 0) {
      query += ` WHERE ${this._where.join(' AND ')}`;
    }

    if (this._limit !== undefined) {
      query += ` LIMIT ${this._limit}`;
    }

    return query;
  }
}

// ============================================================================
// TYPE-ACCUMULATING BUILDER
// ============================================================================

/**
 * TypedBuilder - Accumulates properties through chained calls
 */
export class TypedBuilder<T extends Record<string, any> = {}> {
  private data: Partial<T> = {};

  with<K extends string, V>(key: K, value: V): TypedBuilder<T & Record<K, V>> {
    (this.data as any)[key] = value;
    return this as any;
  }

  build(): T {
    return this.data as T;
  }

  get(): T {
    return this.data as T;
  }
}

// ============================================================================
// PHANTOM TYPE BUILDER (State Tracking)
// ============================================================================

/**
 * Track builder states using phantom types
 */
type BuilderState = 'initial' | 'hasName' | 'hasNameAndEmail' | 'complete';

/**
 * UserBuilder with state tracking
 */
export class UserBuilder<State extends BuilderState = 'initial'> {
  private data: Partial<{
    name: string;
    email: string;
    age?: number;
    role?: string;
  }> = {};

  name(value: string): UserBuilder<'hasName'> {
    this.data.name = value;
    return this as any;
  }

  // Can only be called after name()
  email(this: UserBuilder<'hasName'>, value: string): UserBuilder<'hasNameAndEmail'> {
    this.data.email = value;
    return this as any;
  }

  age(value: number): UserBuilder<State> {
    this.data.age = value;
    return this;
  }

  role(value: string): UserBuilder<State> {
    this.data.role = value;
    return this;
  }

  // Can only build after name and email are set
  build(
    this: UserBuilder<'hasNameAndEmail'>
  ): { name: string; email: string; age?: number; role?: string } {
    return this.data as any;
  }
}

// ============================================================================
// HTTP REQUEST BUILDER
// ============================================================================

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

type RequestState = {
  hasUrl: boolean;
  hasMethod: boolean;
};

export class RequestBuilder<
  State extends RequestState = { hasUrl: false; hasMethod: false }
> {
  private config: {
    url?: string;
    method?: HttpMethod;
    headers?: Record<string, string>;
    body?: any;
    params?: Record<string, string>;
  } = {};

  url<U extends string>(url: U): RequestBuilder<State & { hasUrl: true }> {
    this.config.url = url;
    return this as any;
  }

  method<M extends HttpMethod>(method: M): RequestBuilder<State & { hasMethod: true }> {
    this.config.method = method;
    return this as any;
  }

  headers(headers: Record<string, string>): RequestBuilder<State> {
    this.config.headers = { ...this.config.headers, ...headers };
    return this;
  }

  header(key: string, value: string): RequestBuilder<State> {
    if (!this.config.headers) this.config.headers = {};
    this.config.headers[key] = value;
    return this;
  }

  body(data: any): RequestBuilder<State> {
    this.config.body = data;
    return this;
  }

  params(params: Record<string, string>): RequestBuilder<State> {
    this.config.params = { ...this.config.params, ...params };
    return this;
  }

  // Can only execute when both url and method are set
  async execute(
    this: RequestBuilder<{ hasUrl: true; hasMethod: true }>
  ): Promise<Response> {
    const { url, method, headers, body, params } = this.config;

    let finalUrl = url!;
    if (params) {
      const searchParams = new URLSearchParams(params);
      finalUrl += `?${searchParams.toString()}`;
    }

    return fetch(finalUrl, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // Helper methods for common HTTP methods
  static get(url: string): RequestBuilder<{ hasUrl: true; hasMethod: true }> {
    return new RequestBuilder().url(url).method('GET');
  }

  static post(url: string): RequestBuilder<{ hasUrl: true; hasMethod: true }> {
    return new RequestBuilder().url(url).method('POST');
  }

  static put(url: string): RequestBuilder<{ hasUrl: true; hasMethod: true }> {
    return new RequestBuilder().url(url).method('PUT');
  }

  static delete(url: string): RequestBuilder<{ hasUrl: true; hasMethod: true }> {
    return new RequestBuilder().url(url).method('DELETE');
  }
}

// ============================================================================
// VALIDATION BUILDER
// ============================================================================

type ValidationRule<T> = (value: T) => boolean | string;

export class ValidationBuilder<T> {
  private rules: ValidationRule<T>[] = [];
  private customMessage?: string;

  rule(validator: ValidationRule<T>, message?: string): this {
    this.rules.push((value: T) => {
      const result = validator(value);
      if (result === false) {
        return message || 'Validation failed';
      }
      return result;
    });
    return this;
  }

  required(message = 'This field is required'): this {
    return this.rule(
      (value) => value !== null && value !== undefined && value !== '',
      message
    );
  }

  min(minValue: number, message?: string): this {
    return this.rule(
      (value) => typeof value === 'number' && value >= minValue,
      message || `Value must be at least ${minValue}`
    );
  }

  max(maxValue: number, message?: string): this {
    return this.rule(
      (value) => typeof value === 'number' && value <= maxValue,
      message || `Value must be at most ${maxValue}`
    );
  }

  pattern(regex: RegExp, message?: string): this {
    return this.rule(
      (value) => typeof value === 'string' && regex.test(value),
      message || 'Value does not match the required pattern'
    );
  }

  email(message = 'Invalid email address'): this {
    return this.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/, message);
  }

  validate(value: T): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    for (const rule of this.rules) {
      const result = rule(value);
      if (typeof result === 'string') {
        errors.push(result);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// ============================================================================
// EXAMPLES
// ============================================================================

// Example 1: Query Builder
interface User {
  id: number;
  name: string;
  email: string;
}

const userQuery = new QueryBuilder<User>()
  .select('id', 'name', 'email')
  .from('users')
  .where('age > 18')
  .limit(10)
  .build();

console.log('Query:', userQuery);

// Example 2: Typed Builder
const config = new TypedBuilder()
  .with('host', 'localhost')
  .with('port', 3000)
  .with('secure', true)
  .build();

// config is typed as { host: string; port: number; secure: boolean }

// Example 3: User Builder with State
const user = new UserBuilder()
  .name('John Doe')
  .email('john@example.com')
  .age(30)
  .role('admin')
  .build();

// This won't compile - must call name() before email()
// const invalid = new UserBuilder().email('test@test.com').build();

// Example 4: HTTP Request Builder
const request = RequestBuilder.get('https://api.example.com/users')
  .header('Authorization', 'Bearer token123')
  .params({ page: '1', limit: '20' });

// await request.execute(); // Uncomment to actually make the request

// Example 5: Validation Builder
const passwordValidator = new ValidationBuilder<string>()
  .required()
  .min(8, 'Password must be at least 8 characters')
  .pattern(/[A-Z]/, 'Password must contain an uppercase letter')
  .pattern(/[a-z]/, 'Password must contain a lowercase letter')
  .pattern(/[0-9]/, 'Password must contain a number');

const result1 = passwordValidator.validate('weak');
const result2 = passwordValidator.validate('StrongPass123');

console.log('Weak password validation:', result1);
console.log('Strong password validation:', result2);

// Example 6: Email Validator
const emailValidator = new ValidationBuilder<string>()
  .required('Email is required')
  .email();

console.log('Email validation:', emailValidator.validate('test@example.com'));

console.log('Fluent API Builder module loaded successfully!');
