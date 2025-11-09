/**
 * 08 - Advanced Decorators
 *
 * Decorator factories, metadata reflection, and practical decorator patterns
 * Note: Requires experimentalDecorators and emitDecoratorMetadata in tsconfig
 */

// ============================================================================
// PART 1: METHOD DECORATORS
// ============================================================================

/**
 * Measure method execution time
 */
export function Measure(target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    const start = performance.now();
    const result = originalMethod.apply(this, args);
    const end = performance.now();
    console.log(`${propertyKey} took ${(end - start).toFixed(2)}ms`);
    return result;
  };
}

/**
 * Memoize method results
 */
export function Memoize(target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
  const originalMethod = descriptor.value;
  const cache = new Map<string, any>();

  descriptor.value = function (...args: any[]) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = originalMethod.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

/**
 * Retry failed operations
 */
export function Retry(maxAttempts: number = 3, delay: number = 1000) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: any;
      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error;
          console.log(`Attempt ${attempt} failed, retrying...`);
          if (attempt < maxAttempts) {
            await new Promise((resolve) => setTimeout(resolve, delay));
          }
        }
      }
      throw lastError;
    };
  };
}

/**
 * Debounce method calls
 */
export function Debounce(ms: number) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
    const originalMethod = descriptor.value;
    let timeoutId: ReturnType<typeof setTimeout>;

    descriptor.value = function (...args: any[]) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        originalMethod.apply(this, args);
      }, ms);
    };
  };
}

/**
 * Throttle method calls
 */
export function Throttle(ms: number) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
    const originalMethod = descriptor.value;
    let isThrottled = false;

    descriptor.value = function (...args: any[]) {
      if (isThrottled) return;

      originalMethod.apply(this, args);
      isThrottled = true;

      setTimeout(() => {
        isThrottled = false;
      }, ms);
    };
  };
}

// ============================================================================
// PART 2: CLASS DECORATORS
// ============================================================================

/**
 * Singleton pattern
 */
export function Singleton<T extends { new (...args: any[]): {} }>(constructor: T) {
  let instance: any;

  return class extends constructor {
    constructor(...args: any[]) {
      if (instance) {
        return instance;
      }
      super(...args);
      instance = this;
    }
  } as T;
}

/**
 * Seal a class (prevent extensions)
 */
export function Sealed<T extends { new (...args: any[]): {} }>(constructor: T) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
  return constructor;
}

/**
 * Add logging to all methods
 */
export function LogAllMethods<T extends { new (...args: any[]): {} }>(constructor: T) {
  const methods = Object.getOwnPropertyNames(constructor.prototype);

  methods.forEach((methodName) => {
    const descriptor = Object.getOwnPropertyDescriptor(constructor.prototype, methodName);

    if (descriptor && typeof descriptor.value === 'function' && methodName !== 'constructor') {
      const originalMethod = descriptor.value;

      descriptor.value = function (...args: any[]) {
        console.log(`Calling ${methodName} with:`, args);
        const result = originalMethod.apply(this, args);
        console.log(`${methodName} returned:`, result);
        return result;
      };

      Object.defineProperty(constructor.prototype, methodName, descriptor);
    }
  });

  return constructor;
}

// ============================================================================
// PART 3: PROPERTY DECORATORS
// ============================================================================

/**
 * Mark property as readonly
 */
export function Readonly(target: any, propertyKey: string): void {
  let value: any;

  Object.defineProperty(target, propertyKey, {
    get() {
      return value;
    },
    set(newValue: any) {
      if (value === undefined) {
        value = newValue;
      } else {
        throw new Error(`Cannot modify readonly property ${propertyKey}`);
      }
    },
    enumerable: true,
    configurable: false,
  });
}

/**
 * Validate property value
 */
export function Validate(validator: (value: any) => boolean, message?: string) {
  return function (target: any, propertyKey: string): void {
    let value: any;

    Object.defineProperty(target, propertyKey, {
      get() {
        return value;
      },
      set(newValue: any) {
        if (!validator(newValue)) {
          throw new Error(message || `Validation failed for ${propertyKey}`);
        }
        value = newValue;
      },
      enumerable: true,
      configurable: true,
    });
  };
}

/**
 * Observable property (emit events on change)
 */
export function Observable(target: any, propertyKey: string): void {
  const listeners = new Set<(value: any) => void>();
  let value: any;

  // Add listener method
  (target as any)[`on${propertyKey}Change`] = (callback: (value: any) => void) => {
    listeners.add(callback);
    return () => listeners.delete(callback);
  };

  Object.defineProperty(target, propertyKey, {
    get() {
      return value;
    },
    set(newValue: any) {
      const oldValue = value;
      value = newValue;
      listeners.forEach((listener) => listener(newValue));
    },
    enumerable: true,
    configurable: true,
  });
}

// ============================================================================
// PART 4: PARAMETER DECORATORS
// ============================================================================

const requiredParams: Map<any, Map<string, number[]>> = new Map();

/**
 * Mark parameter as required
 */
export function Required(target: any, propertyKey: string, parameterIndex: number): void {
  if (!requiredParams.has(target)) {
    requiredParams.set(target, new Map());
  }
  const methodParams = requiredParams.get(target)!;
  if (!methodParams.has(propertyKey)) {
    methodParams.set(propertyKey, []);
  }
  methodParams.get(propertyKey)!.push(parameterIndex);
}

/**
 * Validate required parameters
 */
export function ValidateParams(target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    const methodParams = requiredParams.get(target)?.get(propertyKey);
    if (methodParams) {
      for (const index of methodParams) {
        if (args[index] === undefined || args[index] === null) {
          throw new Error(`Parameter at index ${index} is required for ${propertyKey}`);
        }
      }
    }
    return originalMethod.apply(this, args);
  };
}

// ============================================================================
// PART 5: DECORATOR COMPOSITION
// ============================================================================

/**
 * Compose multiple decorators
 */
export function Compose(...decorators: MethodDecorator[]) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor): void {
    decorators.reverse().forEach((decorator) => {
      decorator(target, propertyKey, descriptor);
    });
  };
}

// ============================================================================
// EXAMPLES
// ============================================================================

/**
 * Example 1: Performance monitoring
 */
class Calculator {
  @Measure
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }

  @Memoize
  @Measure
  fibonacciMemoized(n: number): number {
    if (n <= 1) return n;
    return this.fibonacciMemoized(n - 1) + this.fibonacciMemoized(n - 2);
  }
}

/**
 * Example 2: API client with retry
 */
class APIClient {
  @Retry(3, 1000)
  async fetchUser(id: number): Promise<any> {
    const response = await fetch(`https://api.example.com/users/${id}`);
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  }

  @Debounce(300)
  search(query: string): void {
    console.log('Searching for:', query);
  }

  @Throttle(1000)
  trackEvent(event: string): void {
    console.log('Tracking event:', event);
  }
}

/**
 * Example 3: Singleton service
 */
@Singleton
class ConfigService {
  private config: Record<string, any> = {};

  set(key: string, value: any): void {
    this.config[key] = value;
  }

  get(key: string): any {
    return this.config[key];
  }
}

/**
 * Example 4: Validated model
 */
class User {
  @Validate((value) => typeof value === 'string' && value.length > 0, 'Name is required')
  name!: string;

  @Validate((value) => typeof value === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value), 'Invalid email')
  email!: string;

  @Validate((value) => typeof value === 'number' && value >= 18, 'Must be 18 or older')
  age!: number;

  @Observable
  status!: string;
}

/**
 * Example 5: Required parameters
 */
class UserService {
  @ValidateParams
  createUser(@Required name: string, @Required email: string, age?: number): void {
    console.log('Creating user:', { name, email, age });
  }
}

// Test examples
const calc = new Calculator();
console.log('Fibonacci(10):', calc.fibonacci(10));
console.log('Fibonacci memoized(10):', calc.fibonacciMemoized(10));

const config1 = new ConfigService();
const config2 = new ConfigService();
console.log('Singleton works:', config1 === config2); // true

const user = new User();
user.name = 'Alice';
user.email = 'alice@example.com';
user.age = 25;

// Add observer
(user as any).onstatusChange((value: string) => {
  console.log('Status changed to:', value);
});
user.status = 'active';

const userService = new UserService();
userService.createUser('Bob', 'bob@example.com');

console.log('Advanced Decorators module loaded successfully!');
