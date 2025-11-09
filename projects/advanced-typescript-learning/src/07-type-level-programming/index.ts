/**
 * 07 - Type-Level Programming
 *
 * Advanced type-level computations, recursive types, and type-level algorithms
 */

// ============================================================================
// PART 1: TYPE-LEVEL NUMBERS
// ============================================================================

/**
 * Represent numbers as tuple lengths
 */
export type NumberToTuple<
  N extends number,
  Acc extends unknown[] = []
> = Acc['length'] extends N ? Acc : NumberToTuple<N, [...Acc, unknown]>;

export type Length<T extends readonly unknown[]> = T['length'];

/**
 * Type-level arithmetic
 */
export type Add<A extends number, B extends number> = Length<
  [...NumberToTuple<A>, ...NumberToTuple<B>]
>;

export type Subtract<A extends number, B extends number> = NumberToTuple<A> extends [
  ...NumberToTuple<B>,
  ...infer Rest
]
  ? Length<Rest>
  : never;

type Sum = Add<5, 3>; // 8
type Difference = Subtract<10, 3>; // 7

// ============================================================================
// PART 2: TYPE-LEVEL LISTS
// ============================================================================

/**
 * List operations at type level
 */
export type Head<T extends readonly unknown[]> = T extends readonly [infer H, ...unknown[]]
  ? H
  : never;

export type Tail<T extends readonly unknown[]> = T extends readonly [unknown, ...infer Rest]
  ? Rest
  : never;

export type Last<T extends readonly unknown[]> = T extends readonly [...unknown[], infer L]
  ? L
  : never;

export type Init<T extends readonly unknown[]> = T extends readonly [...infer I, unknown]
  ? I
  : never;

/**
 * Reverse a tuple
 */
export type Reverse<T extends readonly unknown[], Acc extends readonly unknown[] = []> = T extends readonly [
  infer First,
  ...infer Rest
]
  ? Reverse<Rest, [First, ...Acc]>
  : Acc;

type Original = [1, 2, 3, 4];
type Reversed = Reverse<Original>; // [4, 3, 2, 1]

/**
 * Concat tuples
 */
export type Concat<T extends readonly unknown[], U extends readonly unknown[]> = [...T, ...U];

/**
 * Flatten nested tuples
 */
export type Flatten<T extends readonly unknown[]> = T extends readonly [infer First, ...infer Rest]
  ? First extends readonly unknown[]
    ? [...Flatten<First>, ...Flatten<Rest>]
    : [First, ...Flatten<Rest>]
  : [];

type Nested = [[1, 2], [3, [4, 5]], 6];
type Flattened = Flatten<Nested>; // [1, 2, 3, 4, 5, 6]

// ============================================================================
// PART 3: TYPE-LEVEL BOOLEAN LOGIC
// ============================================================================

export type Not<T extends boolean> = T extends true ? false : true;

export type And<A extends boolean, B extends boolean> = A extends true
  ? B extends true
    ? true
    : false
  : false;

export type Or<A extends boolean, B extends boolean> = A extends true
  ? true
  : B extends true
  ? true
  : false;

export type Xor<A extends boolean, B extends boolean> = A extends B ? false : true;

/**
 * Type-level comparisons
 */
export type Equals<X, Y> = (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2
  ? true
  : false;

export type IsNever<T> = [T] extends [never] ? true : false;
export type IsAny<T> = 0 extends 1 & T ? true : false;
export type IsUnknown<T> = unknown extends T
  ? IsAny<T> extends true
    ? false
    : true
  : false;

// ============================================================================
// PART 4: TYPE-LEVEL STRINGS
// ============================================================================

/**
 * String manipulation at type level
 */
export type StringToTuple<S extends string> = S extends `${infer C}${infer Rest}`
  ? [C, ...StringToTuple<Rest>]
  : [];

export type TupleToString<T extends readonly string[]> = T extends readonly [
  infer First extends string,
  ...infer Rest extends string[]
]
  ? `${First}${TupleToString<Rest>}`
  : '';

export type ReverseString<S extends string> = TupleToString<Reverse<StringToTuple<S>>>;

type Str = 'hello';
type StrReversed = ReverseString<Str>; // "olleh"

/**
 * String length
 */
export type StringLength<S extends string> = StringToTuple<S>['length'];

type HelloLength = StringLength<'hello'>; // 5

/**
 * String contains
 */
export type Includes<S extends string, Sub extends string> = S extends `${string}${Sub}${string}`
  ? true
  : false;

type HasWorld = Includes<'hello world', 'world'>; // true
type HasFoo = Includes<'hello world', 'foo'>; // false

// ============================================================================
// PART 5: TYPE-LEVEL SETS
// ============================================================================

/**
 * Union operations
 */
export type Union<T, U> = T | U;

export type Intersection<T, U> = T extends U ? T : never;

export type Diff<T, U> = T extends U ? never : T;

export type SymmetricDiff<T, U> = Diff<T, U> | Diff<U, T>;

type A = 'a' | 'b' | 'c';
type B = 'b' | 'c' | 'd';
type AB_Intersection = Intersection<A, B>; // "b" | "c"
type AB_Diff = Diff<A, B>; // "a"
type AB_SymDiff = SymmetricDiff<A, B>; // "a" | "d"

/**
 * Has duplicates in tuple
 */
export type HasDuplicates<T extends readonly unknown[]> = T extends readonly [
  infer First,
  ...infer Rest
]
  ? First extends Rest[number]
    ? true
    : HasDuplicates<Rest>
  : false;

/**
 * Remove duplicates from tuple
 */
export type Unique<T extends readonly unknown[], Acc extends readonly unknown[] = []> = T extends readonly [
  infer First,
  ...infer Rest
]
  ? First extends Acc[number]
    ? Unique<Rest, Acc>
    : Unique<Rest, [...Acc, First]>
  : Acc;

type WithDupes = [1, 2, 2, 3, 1, 4];
type NoDupes = Unique<WithDupes>; // [1, 2, 3, 4]

// ============================================================================
// PART 6: TYPE-LEVEL SORTING
// ============================================================================

/**
 * Comparison for sorting
 */
export type Compare<A, B> = A extends B ? 0 : A extends number
  ? B extends number
    ? A extends 0
      ? -1
      : 1
    : 0
  : 0;

/**
 * Merge sort at type level (simplified for small tuples)
 */
export type Sort<T extends readonly number[]> = T extends readonly [infer First extends number]
  ? [First]
  : T extends readonly [
      infer A extends number,
      infer B extends number
    ]
  ? A extends B
    ? [A, B]
    : [A, B] | [B, A]
  : T;

// ============================================================================
// PART 7: TYPE-LEVEL FUNCTIONS
// ============================================================================

/**
 * Compose types
 */
export type Compose<F, G> = F extends (arg: infer A) => infer B
  ? G extends (arg: B) => infer C
    ? (arg: A) => C
    : never
  : never;

/**
 * Pipe types
 */
export type Pipe<Fns extends readonly ((arg: any) => any)[]> = Fns extends readonly [
  (arg: infer A) => infer B,
  ...infer Rest extends readonly ((arg: any) => any)[]
]
  ? (arg: A) => Pipe<Rest> extends (arg: B) => infer C
    ? C
    : B
  : never;

// ============================================================================
// PART 8: PRACTICAL EXAMPLES
// ============================================================================

/**
 * Deep path access
 */
export type PathValue<T, P extends string> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T
    ? PathValue<T[K], Rest>
    : never
  : P extends keyof T
  ? T[P]
  : never;

type User = {
  profile: {
    name: string;
    address: {
      city: string;
      zip: number;
    };
  };
  settings: {
    theme: 'light' | 'dark';
  };
};

type City = PathValue<User, 'profile.address.city'>; // string
type Theme = PathValue<User, 'settings.theme'>; // "light" | "dark"

/**
 * JSON Schema validator
 */
export type JSONValue =
  | null
  | string
  | number
  | boolean
  | { [key: string]: JSONValue }
  | JSONValue[];

export type ValidJSON<T> = T extends JSONValue ? T : never;

/**
 * State machine type
 */
export type StateMachine<
  States extends string,
  Transitions extends Record<States, States>
> = {
  current: States;
  transition<To extends Transitions[States]>(to: To): StateMachine<States, Transitions>;
};

// Traffic light state machine
type TrafficStates = 'red' | 'yellow' | 'green';
type TrafficTransitions = {
  red: 'green';
  green: 'yellow';
  yellow: 'red';
};

type TrafficLight = StateMachine<TrafficStates, TrafficTransitions>;

/**
 * Parser combinator types
 */
export type Parser<T> = (input: string) => readonly [T, string] | null;

export type ParseResult<P> = P extends Parser<infer T> ? T : never;

// ============================================================================
// RUNTIME EXAMPLES
// ============================================================================

// Example: Deep path getter
function getPath<T, P extends string>(obj: T, path: P): PathValue<T, P> {
  const keys = path.split('.');
  let result: any = obj;
  for (const key of keys) {
    result = result[key];
  }
  return result;
}

const user: User = {
  profile: {
    name: 'Alice',
    address: {
      city: 'NYC',
      zip: 10001,
    },
  },
  settings: {
    theme: 'dark',
  },
};

const city = getPath(user, 'profile.address.city'); // Typed as string
const theme = getPath(user, 'settings.theme'); // Typed as "light" | "dark"

console.log('City:', city);
console.log('Theme:', theme);

console.log('Type-Level Programming module loaded successfully!');
