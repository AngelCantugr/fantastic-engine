# Project 19: Advanced Type System

**Complexity:** ⭐⭐⭐⭐⭐ (Expert)

**Duration:** 5-6 days

**Prerequisites:** Generics, variance, type bounds

## Overview

Master Kotlin's advanced type system including variance, projections, PECS principle, phantom types, and type-level programming for building ultra type-safe APIs.

## Learning Objectives

- ✅ Understand variance (in/out)
- ✅ Use type projections correctly
- ✅ Apply PECS principle
- ✅ Implement phantom types
- ✅ Use star projections
- ✅ Design type-safe APIs

## What You'll Build

1. **Type-Safe Builder** - Phantom types for builder states
2. **Generic Repository** - Variance-aware repository
3. **Event Bus** - Covariant event system
4. **State Machine** - Type-level state enforcement
5. **Parser** - Type-safe parser combinators

## Key Concepts

- Variance (covariance, contravariance, invariance)
- Declaration-site variance (in/out)
- Use-site variance (projections)
- PECS (Producer Extends Consumer Super)
- Phantom types
- Type bounds
- Reified type parameters
- Star projections

## Quick Example

```kotlin
// Covariance (out) - can read, cannot write
interface Producer<out T> {
    fun produce(): T
    // fun consume(value: T) // ❌ Not allowed with 'out'
}

// Contravariance (in) - can write, cannot read
interface Consumer<in T> {
    fun consume(value: T)
    // fun produce(): T // ❌ Not allowed with 'in'
}

// Phantom types for compile-time state
sealed class State
object Unlocked : State()
object Locked : State()

class Door<S : State> private constructor() {
    companion object {
        fun create(): Door<Unlocked> = Door()
    }

    fun lock(): Door<Locked> {
        println("Locking door")
        return Door()
    }

    fun unlock(): Door<Unlocked> where S : Locked {
        println("Unlocking door")
        return Door()
    }

    fun open() where S : Unlocked {
        println("Opening door")
    }
}

// Usage
val door = Door.create()  // Door<Unlocked>
// door.lock()            // ✅ OK
// door.open()            // ✅ OK

val locked = door.lock()  // Door<Locked>
// locked.open()          // ❌ Compile error!
// locked.unlock()        // ✅ OK
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Type system deep dive
- 💡 [**Usage**](docs/02-usage.md) - Advanced type patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Type-level programming
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand variance deeply
- [ ] Use projections correctly
- [ ] Implement phantom types
- [ ] Design type-safe APIs
- [ ] Complete all exercises

## Resources

- [Generics Documentation](https://kotlinlang.org/docs/generics.html)
- [Variance in Kotlin](https://kotlinlang.org/docs/generics.html#variance)
