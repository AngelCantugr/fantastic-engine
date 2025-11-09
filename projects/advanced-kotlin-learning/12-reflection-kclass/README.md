# Project 12: Reflection & KClass

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 4-5 days

**Prerequisites:** Kotlin basics, understanding of runtime type information

## Overview

Master Kotlin reflection API for runtime type inspection, dynamic invocation, and meta-programming. Learn to build frameworks that work with types at runtime.

## Learning Objectives

- ✅ Understand KClass and KType
- ✅ Inspect classes at runtime
- ✅ Invoke functions dynamically
- ✅ Access properties reflectively
- ✅ Build annotation-driven frameworks
- ✅ Optimize reflection usage

## What You'll Build

1. **Serialization Framework** - JSON serializer using reflection
2. **Dependency Injection** - Simple DI container
3. **Validation Framework** - Annotation-based validation
4. **ORM Mapper** - Object-relational mapping
5. **Test Framework** - JUnit-like test runner

## Key Concepts

- KClass, KType, KFunction, KProperty
- Runtime type inspection
- Dynamic invocation
- Annotation processing at runtime
- Reflection performance
- kotlin-reflect library
- Reified type parameters

## Quick Example

```kotlin
import kotlin.reflect.full.*

data class User(val name: String, val age: Int)

fun inspectClass(obj: Any) {
    val kClass = obj::class

    println("Class: ${kClass.simpleName}")
    println("Properties:")
    kClass.memberProperties.forEach { prop ->
        println("  ${prop.name}: ${prop.get(obj)}")
    }

    println("Functions:")
    kClass.memberFunctions.forEach { func ->
        println("  ${func.name}")
    }
}

inspectClass(User("Alice", 30))
// Class: User
// Properties:
//   name: Alice
//   age: 30
// Functions:
//   copy
//   toString
//   ...
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Reflection API
- 💡 [**Usage**](docs/02-usage.md) - Practical reflection
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Framework building
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand KClass API
- [ ] Use reflection effectively
- [ ] Build reflection-based framework
- [ ] Optimize reflection code
- [ ] Complete all exercises

## Resources

- [Reflection Documentation](https://kotlinlang.org/docs/reflection.html)
- [kotlin-reflect API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.reflect/)
