# Project 04: Inline & Value Classes

**Complexity:** ⭐⭐⭐ (Medium-Advanced)

**Duration:** 3-4 days

**Prerequisites:** Basic Kotlin classes, understanding of JVM bytecode basics

## Overview

Master inline and value classes for zero-cost abstractions, type-safe wrappers, and performance optimization. Learn when and how to use these powerful features for type safety without runtime overhead.

## Learning Objectives

- ✅ Understand inline vs value classes
- ✅ Create zero-cost wrappers
- ✅ Implement type-safe primitives
- ✅ Optimize performance with inline classes
- ✅ Understand JVM representation
- ✅ Handle boxing and unboxing

## What You'll Build

1. **Type-Safe IDs** - UserId, OrderId wrappers
2. **Units of Measure** - Distance, Weight, Temperature
3. **Validated Types** - Email, PhoneNumber, URL
4. **Performance Wrappers** - Zero-cost abstractions
5. **Domain Primitives** - Money, Percentage, Coordinates

## Key Concepts

- Value classes (@JvmInline)
- Inline classes (deprecated, now value classes)
- Zero-cost abstractions
- Type safety without overhead
- Boxing and unboxing scenarios
- Generic constraints

## Quick Example

```kotlin
@JvmInline
value class UserId(val value: Long)

@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

// Zero runtime overhead - compiles to primitive Long
fun getUser(id: UserId): User {
    // Type-safe: cannot pass OrderId by mistake
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Value classes deep dive
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Performance and edge cases
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand value class compilation
- [ ] Create type-safe wrappers
- [ ] Know when boxing occurs
- [ ] Optimize with zero-cost abstractions
- [ ] Complete all exercises

## Resources

- [Inline Classes Documentation](https://kotlinlang.org/docs/inline-classes.html)
- [Value Classes KEEP](https://github.com/Kotlin/KEEP/blob/master/proposals/inline-classes.md)
