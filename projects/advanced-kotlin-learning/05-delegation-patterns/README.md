# Project 05: Delegation Patterns

**Complexity:** ⭐⭐⭐ (Medium-Advanced)

**Duration:** 3-4 days

**Prerequisites:** Interfaces, properties, basic Kotlin syntax

## Overview

Master class delegation and property delegation including lazy, observable, vetoable, and custom delegates. Learn to build powerful, reusable abstractions using Kotlin's delegation features.

## Learning Objectives

- ✅ Understand class delegation with `by`
- ✅ Master property delegation
- ✅ Use built-in delegates (lazy, observable, vetoable)
- ✅ Create custom delegates
- ✅ Implement delegated properties
- ✅ Apply delegation patterns in real scenarios

## What You'll Build

1. **Repository Pattern** - Delegated repository implementations
2. **Observable Properties** - Custom observable delegates
3. **Lazy Initialization** - Advanced lazy patterns
4. **Validation Delegates** - Property validation
5. **Caching Delegate** - Memoization patterns

## Key Concepts

- Class delegation (`by` keyword)
- Property delegation
- ReadOnlyProperty and ReadWriteProperty interfaces
- Built-in delegates (lazy, observable, vetoable, map)
- Custom delegate creation
- Providing delegates with provideDelegate

## Quick Example

```kotlin
// Class delegation
interface Repository {
    fun save(data: String)
}

class CachingRepository(
    private val delegate: Repository
) : Repository by delegate {
    private val cache = mutableMapOf<String, String>()

    override fun save(data: String) {
        cache[data] = data
        delegate.save(data)
    }
}

// Property delegation
class User {
    var name: String by observable("<no name>") { prop, old, new ->
        println("$old -> $new")
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Delegation theory
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Real-world scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand class vs property delegation
- [ ] Create custom delegates
- [ ] Use built-in delegates effectively
- [ ] Apply delegation patterns appropriately
- [ ] Complete all exercises

## Resources

- [Delegation Documentation](https://kotlinlang.org/docs/delegation.html)
- [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html)
