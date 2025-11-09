# Project 08: Context Receivers

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 4-5 days

**Prerequisites:** Extension functions, receivers, dependency injection concepts

## Overview

Explore context receivers (experimental feature) for elegant dependency injection, multiple receivers, and context-aware programming. Learn to design APIs that depend on ambient context.

## Learning Objectives

- ✅ Understand context receivers syntax
- ✅ Use multiple receivers effectively
- ✅ Implement context-based DI
- ✅ Design context-aware APIs
- ✅ Migrate from traditional DI
- ✅ Handle context propagation

## What You'll Build

1. **Logging Framework** - Context-aware logging
2. **Transaction Manager** - Database transactions with context
3. **Authorization System** - Context-based permissions
4. **Configuration Access** - Ambient configuration
5. **Testing Framework** - Test context propagation

## Key Concepts

- Context receivers syntax
- Multiple receivers
- Context propagation
- Ambient context pattern
- Implicit parameters
- Reader monad pattern
- Context vs traditional DI

## Quick Example

```kotlin
// Traditional approach
fun processOrder(order: Order, logger: Logger, db: Database, config: Config) {
    logger.info("Processing ${order.id}")
    db.save(order)
}

// With context receivers
context(Logger, Database, Config)
fun processOrder(order: Order) {
    info("Processing ${order.id}") // Logger context
    save(order)                     // Database context
}

// Usage
with(logger) {
    with(database) {
        with(config) {
            processOrder(order)
        }
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Context receivers theory
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Real-world scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand context receivers
- [ ] Use multiple contexts effectively
- [ ] Design context-aware APIs
- [ ] Compare with traditional DI
- [ ] Complete all exercises

## Resources

- [Context Receivers KEEP](https://github.com/Kotlin/KEEP/issues/367)
- [Context Receivers Proposal](https://github.com/Kotlin/KEEP/blob/master/proposals/context-receivers.md)
