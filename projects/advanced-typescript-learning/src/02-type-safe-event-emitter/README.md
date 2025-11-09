# 02 - Type-Safe Event Emitter 📡

**Complexity:** Medium
**Focus:** Generic event systems with strict typing

## 📚 Concepts Covered

1. **Generic Constraints** - Restricting type parameters
2. **String Literal Types** - Exact string matching at compile time
3. **Mapped Types** - Creating event handler maps
4. **Type-Safe Event Handlers** - Ensuring callbacks match event payloads
5. **Method Overloading** - Multiple signatures for type safety

## 🎯 Learning Objectives

- Build a fully type-safe event emitter
- Understand generic constraints with event maps
- Master string literal types for event names
- Learn how to infer handler types from event payloads

## 💡 Key Concepts

### Event Map Pattern

```typescript
interface EventMap {
  'user:login': { userId: number; timestamp: Date }
  'user:logout': { userId: number }
  'data:update': { key: string; value: unknown }
}
```

### Type-Safe Handlers

```typescript
type EventHandler<T> = (payload: T) => void
```

### Generic Event Emitter

```typescript
class EventEmitter<Events extends Record<string, any>> {
  on<K extends keyof Events>(
    event: K,
    handler: (payload: Events[K]) => void
  ): void
}
```

## 🔬 Practical Examples

### Basic Event Emitter

```typescript
// Define events
interface AppEvents {
  'user:login': { userId: number }
  'user:logout': void
  'data:sync': { items: string[] }
}

// Create emitter
const emitter = new EventEmitter<AppEvents>()

// Type-safe subscription
emitter.on('user:login', (payload) => {
  // payload is typed as { userId: number }
  console.log(payload.userId)
})
```

### Advanced Features

- Event namespacing
- Wildcard listeners
- Once-only handlers
- Handler removal
- Event replay for late subscribers

## 🎓 Nuanced Scenarios

### Scenario 1: React-like State Updates

```typescript
interface StateEvents<T> {
  change: { prev: T; next: T }
  error: { error: Error }
}

class ObservableState<T> extends EventEmitter<StateEvents<T>> {
  // Implementation
}
```

### Scenario 2: WebSocket Event Typing

```typescript
interface WebSocketEvents {
  'ws:open': Event
  'ws:message': MessageEvent<string>
  'ws:error': Event
  'ws:close': CloseEvent
}
```

### Scenario 3: Domain Events

```typescript
interface OrderEvents {
  'order:created': { orderId: string; amount: number }
  'order:paid': { orderId: string; paymentId: string }
  'order:shipped': { orderId: string; trackingNumber: string }
  'order:delivered': { orderId: string; timestamp: Date }
  'order:cancelled': { orderId: string; reason: string }
}
```

## 🏃 Practice Exercises

1. Add support for wildcard event listeners
2. Implement event priorities
3. Create async event handlers with Promise support
4. Build an event history/replay system
5. Add middleware/interceptor support
