/**
 * 06 - Branded & Phantom Types
 *
 * Implement nominal typing in TypeScript's structural type system
 * Use phantom types to encode invariants at the type level
 */

// ============================================================================
// PART 1: BRANDED TYPES
// ============================================================================

/**
 * Brand utility - attach unique identifier to types
 */
declare const brand: unique symbol;
export type Brand<T, B> = T & { readonly [brand]: B };

/**
 * Domain-specific branded types
 */
export type UserId = Brand<number, 'UserId'>;
export type ProductId = Brand<number, 'ProductId'>;
export type OrderId = Brand<string, 'OrderId'>;
export type Money = Brand<number, 'Money'>;
export type Percentage = Brand<number, 'Percentage'>;

/**
 * Smart constructors for branded types
 */
export function createUserId(id: number): UserId {
  if (id <= 0) throw new Error('UserId must be positive');
  return id as UserId;
}

export function createProductId(id: number): ProductId {
  if (id <= 0) throw new Error('ProductId must be positive');
  return id as ProductId;
}

export function createOrderId(id: string): OrderId {
  if (!/^ORD-\d{6}$/.test(id)) {
    throw new Error('OrderId must match format ORD-XXXXXX');
  }
  return id as OrderId;
}

export function createMoney(amount: number): Money {
  if (amount < 0) throw new Error('Money cannot be negative');
  if (!Number.isFinite(amount)) throw new Error('Money must be finite');
  // Round to 2 decimal places
  return Math.round(amount * 100) / 100 as Money;
}

export function createPercentage(value: number): Percentage {
  if (value < 0 || value > 100) {
    throw new Error('Percentage must be between 0 and 100');
  }
  return value as Percentage;
}

// ============================================================================
// PART 2: OPERATIONS ON BRANDED TYPES
// ============================================================================

/**
 * Type-safe money operations
 */
export const MoneyOps = {
  add(a: Money, b: Money): Money {
    return createMoney((a as number) + (b as number));
  },
  subtract(a: Money, b: Money): Money {
    return createMoney((a as number) - (b as number));
  },
  multiply(a: Money, factor: number): Money {
    return createMoney((a as number) * factor);
  },
  applyPercentage(amount: Money, percent: Percentage): Money {
    return createMoney((amount as number) * ((percent as number) / 100));
  },
  format(amount: Money, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount as number);
  },
};

// ============================================================================
// PART 3: PHANTOM TYPES
// ============================================================================

/**
 * Phantom type parameter encodes state without runtime representation
 */
export type Validated<T, State extends 'unvalidated' | 'validated' = 'unvalidated'> = {
  readonly value: T;
  readonly __phantomState: State;
};

/**
 * Create unvalidated value
 */
export function unvalidated<T>(value: T): Validated<T, 'unvalidated'> {
  return { value, __phantomState: 'unvalidated' as const };
}

/**
 * Validate function - transforms unvalidated to validated
 */
export function validate<T>(
  input: Validated<T, 'unvalidated'>,
  validator: (value: T) => boolean
): Validated<T, 'validated'> {
  if (!validator(input.value)) {
    throw new Error('Validation failed');
  }
  return { value: input.value, __phantomState: 'validated' as const };
}

/**
 * Function that only accepts validated values
 */
export function processValidated<T>(input: Validated<T, 'validated'>): T {
  return input.value;
}

// ============================================================================
// PART 4: SANITIZED STRINGS
// ============================================================================

/**
 * Track HTML sanitization state
 */
export type HTML<State extends 'raw' | 'sanitized' = 'raw'> = Brand<string, 'HTML'> & {
  readonly __sanitizationState: State;
};

export function rawHTML(html: string): HTML<'raw'> {
  return html as HTML<'raw'>;
}

export function sanitizeHTML(raw: HTML<'raw'>): HTML<'sanitized'> {
  // Simple sanitization (in practice, use a library like DOMPurify)
  const sanitized = (raw as string)
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '');

  return sanitized as HTML<'sanitized'>;
}

export function renderHTML(html: HTML<'sanitized'>): void {
  // Only sanitized HTML can be rendered
  console.log('Rendering:', html);
}

// ============================================================================
// PART 5: TYPE-LEVEL STATE MACHINES
// ============================================================================

/**
 * Connection states as phantom types
 */
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export class Connection<State extends ConnectionState = 'disconnected'> {
  private constructor(private state: State) {}

  static create(): Connection<'disconnected'> {
    return new Connection('disconnected');
  }

  connect(this: Connection<'disconnected'>): Connection<'connecting'> {
    console.log('Connecting...');
    return new Connection('connecting');
  }

  finalize(this: Connection<'connecting'>): Connection<'connected'> {
    console.log('Connected!');
    return new Connection('connected');
  }

  send(this: Connection<'connected'>, data: string): void {
    console.log('Sending:', data);
  }

  disconnect(this: Connection<'connected'>): Connection<'disconnected'> {
    console.log('Disconnecting...');
    return new Connection('disconnected');
  }

  handleError(this: Connection<'connecting' | 'connected'>): Connection<'error'> {
    console.log('Error occurred');
    return new Connection('error');
  }

  retry(this: Connection<'error'>): Connection<'disconnected'> {
    console.log('Retrying...');
    return new Connection('disconnected');
  }
}

// ============================================================================
// PART 6: UNITS OF MEASURE
// ============================================================================

/**
 * Physical units as phantom types
 */
export type Unit = 'meters' | 'feet' | 'kilograms' | 'pounds' | 'celsius' | 'fahrenheit';

export type Measure<N extends number, U extends Unit> = Brand<N, U>;

export type Meters = Measure<number, 'meters'>;
export type Feet = Measure<number, 'feet'>;
export type Kilograms = Measure<number, 'kilograms'>;
export type Pounds = Measure<number, 'pounds'>;
export type Celsius = Measure<number, 'celsius'>;
export type Fahrenheit = Measure<number, 'fahrenheit'>;

export const meters = (value: number): Meters => value as Meters;
export const feet = (value: number): Feet => value as Feet;
export const kg = (value: number): Kilograms => value as Kilograms;
export const lbs = (value: number): Pounds => value as Pounds;
export const celsius = (value: number): Celsius => value as Celsius;
export const fahrenheit = (value: number): Fahrenheit => value as Fahrenheit;

/**
 * Unit conversions
 */
export const Convert = {
  metersToFeet(m: Meters): Feet {
    return feet((m as number) * 3.28084);
  },
  feetToMeters(f: Feet): Meters {
    return meters((f as number) / 3.28084);
  },
  kgToLbs(k: Kilograms): Pounds {
    return lbs((k as number) * 2.20462);
  },
  lbsToKg(p: Pounds): Kilograms {
    return kg((p as number) / 2.20462);
  },
  celsiusToFahrenheit(c: Celsius): Fahrenheit {
    return fahrenheit((c as number) * 9 / 5 + 32);
  },
  fahrenheitToCelsius(f: Fahrenheit): Celsius {
    return celsius(((f as number) - 32) * 5 / 9);
  },
};

// ============================================================================
// EXAMPLES
// ============================================================================

// Example 1: Type-safe IDs prevent mixing
const userId = createUserId(42);
const productId = createProductId(99);

function getUser(id: UserId): void {
  console.log('Getting user:', id);
}

getUser(userId); // ✓ OK
// getUser(productId); // ✗ Compile error - ProductId is not assignable to UserId

// Example 2: Money operations
const price = createMoney(99.99);
const tax = createPercentage(8.5);
const taxAmount = MoneyOps.applyPercentage(price, tax);
const total = MoneyOps.add(price, taxAmount);
console.log('Total:', MoneyOps.format(total));

// Example 3: Validation phantom types
const userInput = unvalidated('test@example.com');
const validEmail = validate(userInput, (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
processValidated(validEmail);
// processValidated(userInput); // ✗ Compile error - must be validated first

// Example 4: HTML sanitization
const unsafeHTML = rawHTML('<script>alert("XSS")</script><p>Safe content</p>');
const safeHTML = sanitizeHTML(unsafeHTML);
renderHTML(safeHTML);
// renderHTML(unsafeHTML); // ✗ Compile error - must be sanitized first

// Example 5: Connection state machine
const conn = Connection.create()
  .connect()
  .finalize();

conn.send('Hello, World!');
const disconnected = conn.disconnect();
// disconnected.send('data'); // ✗ Compile error - cannot send when disconnected

// Example 6: Units of measure
const height = meters(1.8);
const heightInFeet = Convert.metersToFeet(height);
console.log(`Height: ${height}m = ${heightInFeet}ft`);

const temp = celsius(25);
const tempF = Convert.celsiusToFahrenheit(temp);
console.log(`Temperature: ${temp}°C = ${tempF}°F`);

console.log('Branded & Phantom Types module loaded successfully!');
