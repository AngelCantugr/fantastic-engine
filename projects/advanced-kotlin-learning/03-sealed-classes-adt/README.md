# Project 03: Sealed Classes & Algebraic Data Types

**Complexity:** ⭐⭐⭐ (Medium-Advanced)

**Duration:** 2-3 days

**Prerequisites:** Basic Kotlin classes, when expressions

## Overview

Master sealed classes and algebraic data types (ADT) to model domain logic with exhaustive when expressions, type-safe state machines, and functional error handling.

## Learning Objectives

- ✅ Understand sealed classes vs sealed interfaces
- ✅ Model state machines with sealed types
- ✅ Use exhaustive when expressions
- ✅ Implement Result/Either patterns
- ✅ Design type-safe APIs with ADTs
- ✅ Apply functional domain modeling

## What You'll Build

1. **Result Type** - Functional error handling
2. **State Machine** - UI state with sealed classes
3. **Expression Evaluator** - Recursive ADT
4. **Command Pattern** - Type-safe commands
5. **API Response Handler** - Network state modeling

## Key Concepts

- Sealed classes and sealed interfaces
- Algebraic Data Types (Sum types)
- Exhaustive when expressions
- Pattern matching
- Result/Either monads
- Type-safe state machines

## Quick Example

```kotlin
sealed interface Result<out T> {
    data class Success<T>(val value: T) : Result<T>
    data class Error(val exception: Throwable) : Result<Nothing>
    object Loading : Result<Nothing>
}

fun <T> handleResult(result: Result<T>) = when (result) {
    is Result.Success -> println("Got: ${result.value}")
    is Result.Error -> println("Error: ${result.exception}")
    Result.Loading -> println("Loading...")
} // Exhaustive - compiler ensures all cases handled
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Sealed types and ADT theory
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Real-world scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand sealed classes deeply
- [ ] Model state machines correctly
- [ ] Use exhaustive when expressions
- [ ] Implement Result/Either patterns
- [ ] Complete all exercises

## Resources

- [Sealed Classes Documentation](https://kotlinlang.org/docs/sealed-classes.html)
- [ADT in Kotlin](https://arrow-kt.io/learn/typed-errors/working-with-typed-errors/)
