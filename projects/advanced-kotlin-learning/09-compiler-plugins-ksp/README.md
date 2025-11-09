# Project 09: Compiler Plugins & KSP

**Complexity:** ⭐⭐⭐⭐⭐ (Expert)

**Duration:** 5-7 days

**Prerequisites:** Kotlin syntax, annotations, basic code generation concepts

## Overview

Master Kotlin Symbol Processing (KSP) for building compiler plugins and code generators. Learn to analyze source code and generate boilerplate automatically.

## Learning Objectives

- ✅ Understand KSP architecture
- ✅ Process Kotlin symbols
- ✅ Generate Kotlin code
- ✅ Create custom annotations
- ✅ Build incremental processors
- ✅ Debug KSP processors

## What You'll Build

1. **Builder Generator** - Auto-generate builders from classes
2. **DTO Mapper** - Generate mapping code
3. **Serialization Plugin** - Custom serialization
4. **Validation Generator** - Generate validators
5. **Repository Generator** - Generate repository implementations

## Key Concepts

- KSP API and architecture
- Symbol processing
- Code generation with KotlinPoet
- Incremental processing
- Multi-round processing
- Annotation processing
- Visitor pattern for symbols

## Quick Example

```kotlin
// Custom annotation
@Target(AnnotationTarget.CLASS)
annotation class GenerateBuilder

// Annotated class
@GenerateBuilder
data class User(
    val name: String,
    val age: Int
)

// KSP Processor generates:
class UserBuilder {
    var name: String = ""
    var age: Int = 0

    fun build() = User(name, age)
}

fun user(init: UserBuilder.() -> Unit): User {
    return UserBuilder().apply(init).build()
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - KSP deep dive
- 💡 [**Usage**](docs/02-usage.md) - Building processors
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Complex generators
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand KSP architecture
- [ ] Process Kotlin symbols
- [ ] Generate valid Kotlin code
- [ ] Build working processors
- [ ] Complete all exercises

## Resources

- [KSP Documentation](https://kotlinlang.org/docs/ksp-overview.html)
- [KotlinPoet](https://square.github.io/kotlinpoet/)
- [KSP Quickstart](https://kotlinlang.org/docs/ksp-quickstart.html)
