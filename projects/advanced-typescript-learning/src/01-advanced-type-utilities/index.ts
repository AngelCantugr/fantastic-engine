/**
 * 01 - Advanced Type Utilities
 *
 * This module demonstrates advanced TypeScript utility types including
 * mapped types, conditional types, and type inference patterns.
 */

// ============================================================================
// PART 1: Custom Utility Types
// ============================================================================

/**
 * DeepPartial - Makes all properties and nested properties optional
 */
export type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends Array<infer U>
      ? Array<DeepPartial<U>>
      : DeepPartial<T[K]>
    : T[K];
};

/**
 * DeepReadonly - Makes all properties and nested properties readonly
 */
export type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Array<infer U>
      ? ReadonlyArray<DeepReadonly<U>>
      : DeepReadonly<T[K]>
    : T[K];
};

/**
 * DeepRequired - Makes all properties and nested properties required
 */
export type DeepRequired<T> = {
  [K in keyof T]-?: T[K] extends object
    ? T[K] extends Array<infer U>
      ? Array<DeepRequired<U>>
      : DeepRequired<T[K]>
    : T[K];
};

/**
 * Nullable - Allows a type to be null
 */
export type Nullable<T> = T | null;

/**
 * Maybe - Allows a type to be null or undefined
 */
export type Maybe<T> = T | null | undefined;

// ============================================================================
// PART 2: Property Manipulation Types
// ============================================================================

/**
 * PickByType - Pick properties of a specific type
 */
export type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

/**
 * OmitByType - Omit properties of a specific type
 */
export type OmitByType<T, U> = {
  [K in keyof T as T[K] extends U ? never : K]: T[K];
};

/**
 * FunctionPropertyNames - Extract names of function properties
 */
export type FunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? K : never;
}[keyof T];

/**
 * FunctionProperties - Extract only function properties
 */
export type FunctionProperties<T> = Pick<T, FunctionPropertyNames<T>>;

/**
 * NonFunctionPropertyNames - Extract names of non-function properties
 */
export type NonFunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? never : K;
}[keyof T];

/**
 * NonFunctionProperties - Extract only non-function properties
 */
export type NonFunctionProperties<T> = Pick<T, NonFunctionPropertyNames<T>>;

// ============================================================================
// PART 3: Advanced Inference Types
// ============================================================================

/**
 * Promisify - Wrap all function return types in Promise
 */
export type Promisify<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? (...args: A) => Promise<R>
    : T[K];
};

/**
 * UnwrapPromise - Extract the type from a Promise
 */
export type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

/**
 * UnwrapArray - Extract the element type from an Array
 */
export type UnwrapArray<T> = T extends Array<infer U> ? U : T;

/**
 * ReturnTypes - Extract return types from all functions in an object
 */
export type ReturnTypes<T> = {
  [K in keyof T]: T[K] extends (...args: any[]) => infer R ? R : never;
};

/**
 * ArgumentTypes - Extract first argument types from all functions
 */
export type ArgumentTypes<T> = {
  [K in keyof T]: T[K] extends (arg: infer A, ...args: any[]) => any ? A : never;
};

// ============================================================================
// PART 4: Conditional Type Utilities
// ============================================================================

/**
 * IsNever - Check if a type is never
 */
export type IsNever<T> = [T] extends [never] ? true : false;

/**
 * IsAny - Check if a type is any
 */
export type IsAny<T> = 0 extends 1 & T ? true : false;

/**
 * IsUnknown - Check if a type is unknown
 */
export type IsUnknown<T> = IsNever<T> extends false
  ? T extends unknown
    ? unknown extends T
      ? IsAny<T> extends false
        ? true
        : false
      : false
    : false
  : false;

/**
 * Equals - Check if two types are equal
 */
export type Equals<X, Y> = (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2
  ? true
  : false;

// ============================================================================
// PART 5: Practical Examples
// ============================================================================

/**
 * Form State Management
 */
export type FieldState<T> = {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
};

export type FormState<T> = {
  [K in keyof T]: FieldState<T[K]>;
};

export type FormValues<T> = {
  [K in keyof T]: T[K] extends FieldState<infer V> ? V : never;
};

/**
 * API Response Types
 */
export type ApiSuccess<T> = {
  status: 'success';
  data: T;
  timestamp: number;
};

export type ApiError = {
  status: 'error';
  error: string;
  code: number;
  timestamp: number;
};

export type ApiLoading = {
  status: 'loading';
};

export type ApiResponse<T> = ApiSuccess<T> | ApiError | ApiLoading;

/**
 * Extract data type from ApiResponse
 */
export type ExtractApiData<T> = T extends ApiSuccess<infer D> ? D : never;

/**
 * Mutable - Remove readonly modifiers
 */
export type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

/**
 * DeepMutable - Remove readonly modifiers recursively
 */
export type DeepMutable<T> = {
  -readonly [K in keyof T]: T[K] extends object ? DeepMutable<T[K]> : T[K];
};

// ============================================================================
// EXAMPLES AND TESTS
// ============================================================================

// Example 1: Form State
interface LoginForm {
  email: string;
  password: string;
  rememberMe: boolean;
}

type LoginFormState = FormState<LoginForm>;

const loginForm: LoginFormState = {
  email: { value: '', error: undefined, touched: false, dirty: false },
  password: { value: '', error: undefined, touched: false, dirty: false },
  rememberMe: { value: false, error: undefined, touched: false, dirty: false },
};

// Example 2: API Response
type UserData = {
  id: number;
  name: string;
  email: string;
};

type UserResponse = ApiResponse<UserData>;

const successResponse: UserResponse = {
  status: 'success',
  data: { id: 1, name: 'John', email: 'john@example.com' },
  timestamp: Date.now(),
};

// Example 3: Property Picking by Type
interface MixedProps {
  name: string;
  age: number;
  onClick: () => void;
  onSubmit: (value: string) => void;
  isActive: boolean;
}

type OnlyFunctions = FunctionProperties<MixedProps>;
// Result: { onClick: () => void; onSubmit: (value: string) => void }

type OnlyData = NonFunctionProperties<MixedProps>;
// Result: { name: string; age: number; isActive: boolean }

// Example 4: Deep Operations
interface NestedConfig {
  database: {
    host: string;
    port: number;
    credentials: {
      username: string;
      password: string;
    };
  };
  cache: {
    enabled: boolean;
    ttl: number;
  };
}

type PartialConfig = DeepPartial<NestedConfig>;
// All properties including nested ones are optional

type ReadonlyConfig = DeepReadonly<NestedConfig>;
// All properties including nested ones are readonly

// Example 5: Promisify
interface SyncService {
  getUser(id: number): UserData;
  deleteUser(id: number): boolean;
  updateUser(id: number, data: Partial<UserData>): UserData;
}

type AsyncService = Promisify<SyncService>;
// All methods now return Promise<T>

// Example 6: Type Checking
type Test1 = IsNever<never>; // true
type Test2 = IsAny<any>; // true
type Test3 = IsUnknown<unknown>; // true
type Test4 = Equals<string, string>; // true
type Test5 = Equals<string, number>; // false

console.log('Advanced Type Utilities module loaded successfully!');
