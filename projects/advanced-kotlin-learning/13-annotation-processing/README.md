# Project 13: Annotation Processing

**Complexity:** ⭐⭐⭐⭐⭐ (Expert)

**Duration:** 5-6 days

**Prerequisites:** Annotations, KAPT basics, code generation

## Overview

Master annotation processing with KAPT (Kotlin Annotation Processing Tool) and build custom annotation processors for code generation and compile-time validation.

## Learning Objectives

- ✅ Understand KAPT vs KSP
- ✅ Create custom annotations
- ✅ Build annotation processors
- ✅ Generate code with JavaPoet/KotlinPoet
- ✅ Handle multiple rounds
- ✅ Debug processors

## What You'll Build

1. **AutoService** - Service locator generator
2. **Parcelize Alternative** - Android parcelable generator
3. **Factory Generator** - Factory pattern code gen
4. **DTO Generator** - Generate DTOs from entities
5. **Router Generator** - URL routing code generation

## Key Concepts

- KAPT (Kotlin Annotation Processing Tool)
- javax.annotation.processing API
- Code generation
- Multiple processing rounds
- JavaPoet and KotlinPoet
- Incremental annotation processing
- Error reporting

## Quick Example

```kotlin
// Custom annotation
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.SOURCE)
annotation class AutoFactory

// Annotated class
@AutoFactory
class UserService(
    private val repository: UserRepository
)

// Generated code by processor:
object UserServiceFactory {
    fun create(repository: UserRepository): UserService {
        return UserService(repository)
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Annotation processing
- 💡 [**Usage**](docs/02-usage.md) - Building processors
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Complex generators
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand KAPT architecture
- [ ] Build custom annotations
- [ ] Create working processors
- [ ] Generate valid code
- [ ] Complete all exercises

## Resources

- [KAPT Documentation](https://kotlinlang.org/docs/kapt.html)
- [KotlinPoet](https://square.github.io/kotlinpoet/)
