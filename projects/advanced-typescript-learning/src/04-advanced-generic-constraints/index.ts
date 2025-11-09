/**
 * 04 - Advanced Generic Constraints
 *
 * Deep dive into generic constraints, variance, and type inference
 */

// ============================================================================
// PART 1: BASIC CONSTRAINTS
// ============================================================================

/**
 * Constrain to objects with specific properties
 */
export function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

/**
 * Constrain to objects with specific structure
 */
export function merge<T extends object, U extends object>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

// ============================================================================
// PART 2: CONDITIONAL CONSTRAINTS
// ============================================================================

/**
 * Constrain based on conditional types
 */
export type Flatten<T> = T extends Array<infer U> ? U : T;

export function flatten<T>(value: T): Flatten<T> {
  return (Array.isArray(value) ? value[0] : value) as Flatten<T>;
}

/**
 * Constrain to constructable types
 */
export type Constructor<T = any> = new (...args: any[]) => T;

export function instantiate<T>(ctor: Constructor<T>, ...args: any[]): T {
  return new ctor(...args);
}

// ============================================================================
// PART 3: MULTIPLE TYPE PARAMETERS WITH CONSTRAINTS
// ============================================================================

/**
 * Generic cache with key-value constraints
 */
export class TypedCache<K extends string | number, V> {
  private store = new Map<K, V>();

  set(key: K, value: V): void {
    this.store.set(key, value);
  }

  get(key: K): V | undefined {
    return this.store.get(key);
  }

  has(key: K): boolean {
    return this.store.has(key);
  }
}

/**
 * Generic event bus with constraints
 */
export class EventBus<Events extends Record<string, unknown[]>> {
  private listeners = new Map<keyof Events, Set<(...args: any[]) => void>>();

  on<K extends keyof Events>(event: K, handler: (...args: Events[K]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }

  emit<K extends keyof Events>(event: K, ...args: Events[K]): void {
    this.listeners.get(event)?.forEach((handler) => handler(...args));
  }
}

// ============================================================================
// PART 4: RECURSIVE CONSTRAINTS
// ============================================================================

/**
 * Deep readonly with constraints
 */
export type DeepReadonlyObject<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepReadonlyObject<T[K]>
    : T[K];
};

/**
 * Deep pick with path constraints
 */
export type PathsToStringProps<T> = T extends string
  ? []
  : {
      [K in Extract<keyof T, string>]: [K, ...PathsToStringProps<T[K]>];
    }[Extract<keyof T, string>];

// ============================================================================
// PART 5: VARIANCE AND CONTRAVARIANCE
// ============================================================================

/**
 * Covariance example (return types)
 */
type Producer<T> = () => T;

// Contravariance example (parameter types)
type Consumer<T> = (value: T) => void;

// Invariance example (both)
type Transformer<T> = (value: T) => T;

/**
 * Safe type narrowing with constraints
 */
export function assertType<T>(value: unknown, check: (v: unknown) => v is T): asserts value is T {
  if (!check(value)) {
    throw new TypeError('Type assertion failed');
  }
}

// ============================================================================
// PART 6: ADVANCED INFERENCE
// ============================================================================

/**
 * Infer function parameters
 */
export type Parameters<T extends (...args: any) => any> = T extends (...args: infer P) => any
  ? P
  : never;

/**
 * Infer function return type
 */
export type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R
  ? R
  : never;

/**
 * Infer instance type from constructor
 */
export type InstanceType<T extends Constructor> = T extends Constructor<infer I> ? I : never;

/**
 * Infer promise resolution type
 */
export type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T;

// ============================================================================
// PART 7: COMPLEX CONSTRAINT PATTERNS
// ============================================================================

/**
 * Constrain to comparable types
 */
export interface Comparable<T> {
  compareTo(other: T): number;
}

export function sort<T extends Comparable<T>>(items: T[]): T[] {
  return items.sort((a, b) => a.compareTo(b));
}

/**
 * Constrain to serializable types
 */
export type Serializable = string | number | boolean | null | Serializable[] | { [key: string]: Serializable };

export function serialize<T extends Serializable>(value: T): string {
  return JSON.stringify(value);
}

/**
 * Constrain to numeric enums
 */
export function getEnumValues<T extends Record<string, number | string>>(
  enumObj: T
): Array<T[keyof T]> {
  return Object.values(enumObj).filter((v) => typeof v === 'number') as Array<T[keyof T]>;
}

// ============================================================================
// EXAMPLES
// ============================================================================

// Example 1: Generic constraints
interface Person {
  name: string;
  age: number;
}

const person: Person = { name: 'Alice', age: 30 };
const name = getProperty(person, 'name'); // string
const age = getProperty(person, 'age'); // number

// Example 2: Typed cache
const cache = new TypedCache<string, Person>();
cache.set('user1', { name: 'Bob', age: 25 });
const user = cache.get('user1');

// Example 3: Event bus with typed events
interface AppEvents {
  login: [userId: number, timestamp: Date];
  logout: [userId: number];
  error: [error: Error];
}

const bus = new EventBus<AppEvents>();
bus.on('login', (userId, timestamp) => {
  console.log(`User ${userId} logged in at ${timestamp}`);
});

bus.emit('login', 123, new Date());

// Example 4: Comparable implementation
class Version implements Comparable<Version> {
  constructor(
    public major: number,
    public minor: number,
    public patch: number
  ) {}

  compareTo(other: Version): number {
    if (this.major !== other.major) return this.major - other.major;
    if (this.minor !== other.minor) return this.minor - other.minor;
    return this.patch - other.patch;
  }
}

const versions = [new Version(2, 0, 0), new Version(1, 5, 3), new Version(1, 10, 0)];
const sorted = sort(versions);

console.log('Advanced Generic Constraints module loaded successfully!');
