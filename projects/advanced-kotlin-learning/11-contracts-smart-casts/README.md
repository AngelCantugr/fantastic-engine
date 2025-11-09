# Project 11: Contracts & Smart Casts

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 3-4 days

**Prerequisites:** Kotlin type system, nullable types, type checking

## Overview

Master Kotlin contracts to help the compiler understand your code better, enabling smarter casts, improved null safety, and better flow analysis.

## Learning Objectives

- ✅ Understand compiler contracts
- ✅ Use built-in contracts effectively
- ✅ Create custom contracts
- ✅ Improve smart cast behavior
- ✅ Enhance null safety analysis
- ✅ Design contract-aware APIs

## What You'll Build

1. **Validation Library** - Contract-based validators
2. **Null Safety Helpers** - Smart null checks
3. **Type Guards** - Type checking utilities
4. **Flow Analysis** - Improve compiler understanding
5. **DSL with Contracts** - Better DSL type inference

## Key Concepts

- Kotlin contracts
- Smart casts
- Flow-sensitive typing
- Contract effects (returns, callsInPlace)
- Null safety improvements
- Type narrowing
- Contract syntax and limitations

## Quick Example

```kotlin
// Without contract
fun String?.isNotNullOrEmpty(): Boolean {
    return this != null && this.isNotEmpty()
}

fun test(s: String?) {
    if (s.isNotNullOrEmpty()) {
        println(s.length) // ❌ Compiler error: s might be null
    }
}

// With contract
@OptIn(ExperimentalContracts::class)
fun String?.isNotNullOrEmpty(): Boolean {
    contract {
        returns(true) implies (this@isNotNullOrEmpty != null)
    }
    return this != null && this.isNotEmpty()
}

fun test(s: String?) {
    if (s.isNotNullOrEmpty()) {
        println(s.length) // ✅ Smart cast: s is now String (not null)
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Contracts deep dive
- 💡 [**Usage**](docs/02-usage.md) - Practical contracts
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Advanced scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand contract effects
- [ ] Use contracts for smart casts
- [ ] Create custom contracts
- [ ] Improve type inference
- [ ] Complete all exercises

## Resources

- [Contracts Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.contracts/)
- [Contracts KEEP](https://github.com/Kotlin/KEEP/blob/master/proposals/kotlin-contracts.md)
