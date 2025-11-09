/**
 * 02 - Type-Safe Event Emitter
 *
 * A fully type-safe event emitter implementation demonstrating
 * generic constraints, string literal types, and mapped types.
 */

// ============================================================================
// CORE EVENT EMITTER
// ============================================================================

/**
 * EventMap - Defines the contract for events
 * Keys are event names, values are payload types
 */
export type EventMap = Record<string, any>;

/**
 * EventHandler - Type-safe event handler function
 */
export type EventHandler<T> = (payload: T) => void;

/**
 * EventHandlerAsync - Async event handler
 */
export type EventHandlerAsync<T> = (payload: T) => Promise<void>;

/**
 * EventEmitter - Type-safe event emitter class
 */
export class EventEmitter<Events extends EventMap> {
  private handlers: {
    [K in keyof Events]?: Set<EventHandler<Events[K]>>;
  } = {};

  private onceHandlers: {
    [K in keyof Events]?: Set<EventHandler<Events[K]>>;
  } = {};

  /**
   * Subscribe to an event
   */
  on<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>): () => void {
    if (!this.handlers[event]) {
      this.handlers[event] = new Set();
    }
    this.handlers[event]!.add(handler);

    // Return unsubscribe function
    return () => this.off(event, handler);
  }

  /**
   * Subscribe to an event, but only fire once
   */
  once<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>): () => void {
    if (!this.onceHandlers[event]) {
      this.onceHandlers[event] = new Set();
    }
    this.onceHandlers[event]!.add(handler);

    return () => {
      this.onceHandlers[event]?.delete(handler);
    };
  }

  /**
   * Unsubscribe from an event
   */
  off<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>): void {
    this.handlers[event]?.delete(handler);
    this.onceHandlers[event]?.delete(handler);
  }

  /**
   * Emit an event
   */
  emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    // Fire regular handlers
    this.handlers[event]?.forEach((handler) => {
      handler(payload);
    });

    // Fire once handlers and remove them
    this.onceHandlers[event]?.forEach((handler) => {
      handler(payload);
    });
    this.onceHandlers[event]?.clear();
  }

  /**
   * Remove all handlers for an event or all events
   */
  clear<K extends keyof Events>(event?: K): void {
    if (event) {
      this.handlers[event]?.clear();
      this.onceHandlers[event]?.clear();
    } else {
      this.handlers = {};
      this.onceHandlers = {};
    }
  }

  /**
   * Get listener count for an event
   */
  listenerCount<K extends keyof Events>(event: K): number {
    const regularCount = this.handlers[event]?.size ?? 0;
    const onceCount = this.onceHandlers[event]?.size ?? 0;
    return regularCount + onceCount;
  }
}

// ============================================================================
// ADVANCED: ASYNC EVENT EMITTER
// ============================================================================

/**
 * AsyncEventEmitter - Event emitter with async handler support
 */
export class AsyncEventEmitter<Events extends EventMap> {
  private handlers: {
    [K in keyof Events]?: Set<EventHandlerAsync<Events[K]>>;
  } = {};

  on<K extends keyof Events>(event: K, handler: EventHandlerAsync<Events[K]>): () => void {
    if (!this.handlers[event]) {
      this.handlers[event] = new Set();
    }
    this.handlers[event]!.add(handler);
    return () => this.off(event, handler);
  }

  off<K extends keyof Events>(event: K, handler: EventHandlerAsync<Events[K]>): void {
    this.handlers[event]?.delete(handler);
  }

  /**
   * Emit event and wait for all handlers to complete
   */
  async emit<K extends keyof Events>(event: K, payload: Events[K]): Promise<void> {
    const handlers = Array.from(this.handlers[event] ?? []);
    await Promise.all(handlers.map((handler) => handler(payload)));
  }

  /**
   * Emit event and wait for handlers sequentially
   */
  async emitSequential<K extends keyof Events>(event: K, payload: Events[K]): Promise<void> {
    const handlers = Array.from(this.handlers[event] ?? []);
    for (const handler of handlers) {
      await handler(payload);
    }
  }
}

// ============================================================================
// ADVANCED: WILDCARD EVENT EMITTER
// ============================================================================

/**
 * WildcardEventEmitter - Supports wildcard event listening
 */
export class WildcardEventEmitter<Events extends EventMap> extends EventEmitter<Events> {
  private wildcardHandlers: Set<(event: keyof Events, payload: any) => void> = new Set();

  /**
   * Listen to all events
   */
  onAny(handler: <K extends keyof Events>(event: K, payload: Events[K]) => void): () => void {
    this.wildcardHandlers.add(handler);
    return () => this.offAny(handler);
  }

  /**
   * Remove wildcard handler
   */
  offAny(handler: (event: keyof Events, payload: any) => void): void {
    this.wildcardHandlers.delete(handler);
  }

  /**
   * Override emit to trigger wildcard handlers
   */
  override emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    super.emit(event, payload);
    this.wildcardHandlers.forEach((handler) => handler(event, payload));
  }
}

// ============================================================================
// ADVANCED: NAMESPACED EVENT EMITTER
// ============================================================================

/**
 * Extract namespace from event name
 */
type ExtractNamespace<T extends string> = T extends `${infer NS}:${string}` ? NS : never;

/**
 * NamespacedEventEmitter - Event emitter with namespace support
 */
export class NamespacedEventEmitter<Events extends Record<string, any>> extends EventEmitter<Events> {
  /**
   * Listen to all events in a namespace
   */
  onNamespace<NS extends ExtractNamespace<Extract<keyof Events, string>>>(
    namespace: NS,
    handler: <K extends Extract<keyof Events, `${NS}:${string}`>>(
      event: K,
      payload: Events[K]
    ) => void
  ): () => void {
    const unsubscribers: Array<() => void> = [];

    for (const event in this['handlers']) {
      if (String(event).startsWith(`${namespace}:`)) {
        const unsub = this.on(event as keyof Events, (payload) => {
          handler(event as any, payload);
        });
        unsubscribers.push(unsub);
      }
    }

    return () => unsubscribers.forEach((unsub) => unsub());
  }
}

// ============================================================================
// PRACTICAL EXAMPLES
// ============================================================================

/**
 * Example 1: Application Events
 */
interface AppEvents {
  'user:login': { userId: number; username: string; timestamp: Date };
  'user:logout': { userId: number; timestamp: Date };
  'user:register': { userId: number; email: string };
  'data:sync': { items: string[]; timestamp: Date };
  'data:error': { error: Error; operation: string };
  'ui:notification': { message: string; type: 'info' | 'warning' | 'error' };
}

const appEmitter = new EventEmitter<AppEvents>();

// Type-safe event subscription
const unsubscribe = appEmitter.on('user:login', (payload) => {
  console.log(`User ${payload.username} logged in at ${payload.timestamp}`);
  // payload is correctly typed!
});

// Type-safe emission
appEmitter.emit('user:login', {
  userId: 1,
  username: 'john_doe',
  timestamp: new Date(),
});

/**
 * Example 2: WebSocket Events
 */
interface WebSocketEvents {
  'ws:open': Event;
  'ws:message': { data: string; timestamp: Date };
  'ws:error': { error: Error };
  'ws:close': { code: number; reason: string };
}

const wsEmitter = new EventEmitter<WebSocketEvents>();

wsEmitter.on('ws:message', (payload) => {
  console.log('Received:', payload.data);
});

/**
 * Example 3: Observable State
 */
interface StateEvents<T> {
  change: { prev: T; next: T };
  error: { error: Error };
  init: { value: T };
}

class ObservableState<T> extends EventEmitter<StateEvents<T>> {
  private _value: T;

  constructor(initialValue: T) {
    super();
    this._value = initialValue;
    this.emit('init', { value: initialValue });
  }

  get value(): T {
    return this._value;
  }

  set value(newValue: T) {
    const prev = this._value;
    this._value = newValue;
    this.emit('change', { prev, next: newValue });
  }

  update(updater: (current: T) => T): void {
    try {
      const prev = this._value;
      this._value = updater(prev);
      this.emit('change', { prev, next: this._value });
    } catch (error) {
      this.emit('error', { error: error as Error });
    }
  }
}

// Usage
const counter = new ObservableState<number>(0);

counter.on('change', ({ prev, next }) => {
  console.log(`Counter changed from ${prev} to ${next}`);
});

counter.value = 5; // Triggers change event

/**
 * Example 4: Domain Events (E-commerce)
 */
interface OrderEvents {
  'order:created': { orderId: string; userId: number; amount: number };
  'order:paid': { orderId: string; paymentId: string; amount: number };
  'order:shipped': { orderId: string; trackingNumber: string; carrier: string };
  'order:delivered': { orderId: string; timestamp: Date; signature?: string };
  'order:cancelled': { orderId: string; reason: string; refundAmount: number };
  'order:refunded': { orderId: string; amount: number; method: string };
}

const orderEmitter = new AsyncEventEmitter<OrderEvents>();

// Async handlers
orderEmitter.on('order:paid', async (payload) => {
  console.log(`Processing payment ${payload.paymentId}`);
  // Send confirmation email
  // Update inventory
  // Notify shipping department
});

/**
 * Example 5: Wildcard Events
 */
const wildcardEmitter = new WildcardEventEmitter<AppEvents>();

// Listen to all events
wildcardEmitter.onAny((event, payload) => {
  console.log(`Event ${String(event)} fired with:`, payload);
  // Useful for logging, analytics, debugging
});

/**
 * Example 6: Namespaced Events
 */
const namespacedEmitter = new NamespacedEventEmitter<AppEvents>();

// Listen to all user events
namespacedEmitter.onNamespace('user', (event, payload) => {
  console.log(`User event: ${String(event)}`, payload);
});

console.log('Type-Safe Event Emitter module loaded successfully!');

export { appEmitter, wsEmitter, orderEmitter };
