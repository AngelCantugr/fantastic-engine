# Project 06: Extension Functions & Receivers

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 4-5 days

**Prerequisites:** Extension functions basics, scope functions

## Overview

Deep dive into extension functions, receivers, scope functions, and context receivers. Master the nuances of dispatch vs extension receivers, shadowing, and advanced receiver patterns.

## Learning Objectives

- ✅ Understand dispatch vs extension receivers
- ✅ Master scope functions (let, run, with, apply, also)
- ✅ Handle receiver shadowing correctly
- ✅ Use context receivers (experimental)
- ✅ Create extension-heavy APIs
- ✅ Design fluent interfaces

## What You'll Build

1. **Extension Library** - Comprehensive utility extensions
2. **Scope Function Alternatives** - Custom scope functions
3. **Fluent Validation** - Extension-based validation
4. **Context Receivers Demo** - DI with context receivers
5. **DSL with Extensions** - Combining extensions with DSLs

## Key Concepts

- Extension functions and properties
- Dispatch receiver vs extension receiver
- Scope functions (let, run, with, apply, also)
- Context receivers (experimental)
- Member vs extension precedence
- Nullable receivers
- Extension shadowing and resolution

## Quick Example

```kotlin
// Extension function with receiver
fun String.isValidEmail(): Boolean =
    this.contains("@") && this.contains(".")

// Context receivers (experimental)
context(Logger, Database)
fun processUser(user: User) {
    log("Processing user: ${user.id}")
    save(user)
}

// Dispatch vs extension receiver
class MyClass {
    fun String.myFun() {
        this // String (extension receiver)
        this@MyClass // MyClass (dispatch receiver)
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Receivers and extensions
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Complex scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand receiver types
- [ ] Use scope functions appropriately
- [ ] Handle shadowing correctly
- [ ] Design extension-based APIs
- [ ] Complete all exercises

## Resources

- [Extensions Documentation](https://kotlinlang.org/docs/extensions.html)
- [Scope Functions](https://kotlinlang.org/docs/scope-functions.html)
- [Context Receivers KEEP](https://github.com/Kotlin/KEEP/issues/367)
