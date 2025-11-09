# Project 10: Multiplatform Architecture

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 5-6 days

**Prerequisites:** Kotlin basics, understanding of different platforms (JVM, JS, Native)

## Overview

Master Kotlin Multiplatform to share code across JVM, JavaScript, Native, and other platforms. Learn expect/actual declarations, platform-specific implementations, and multiplatform architecture patterns.

## Learning Objectives

- ✅ Understand expect/actual mechanism
- ✅ Design multiplatform libraries
- ✅ Handle platform-specific code
- ✅ Share business logic across platforms
- ✅ Configure multiplatform projects
- ✅ Test multiplatform code

## What You'll Build

1. **Logging Library** - Multiplatform logger
2. **Network Client** - HTTP client for all platforms
3. **Storage Layer** - Persistent storage abstraction
4. **Crypto Library** - Encryption across platforms
5. **UI State Manager** - Shared business logic

## Key Concepts

- expect/actual declarations
- Platform-specific implementations
- Common module architecture
- Source sets configuration
- Gradle multiplatform plugin
- Target platforms (JVM, JS, Native, iOS, Android)
- Multiplatform libraries

## Quick Example

```kotlin
// Common code (expect)
expect class Platform {
    val name: String
}

expect fun currentTimeMillis(): Long

// JVM implementation (actual)
actual class Platform {
    actual val name: String = "JVM"
}

actual fun currentTimeMillis(): Long = System.currentTimeMillis()

// JS implementation (actual)
actual class Platform {
    actual val name: String = "JavaScript"
}

actual fun currentTimeMillis(): Long = Date.now().toLong()

// Shared code
fun greet() {
    println("Hello from ${Platform().name} at ${currentTimeMillis()}")
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Multiplatform architecture
- 💡 [**Usage**](docs/02-usage.md) - Building multiplatform libs
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Platform-specific code
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand expect/actual
- [ ] Build multiplatform library
- [ ] Handle platform differences
- [ ] Configure multiplatform projects
- [ ] Complete all exercises

## Resources

- [Kotlin Multiplatform](https://kotlinlang.org/docs/multiplatform.html)
- [Multiplatform Guide](https://kotlinlang.org/docs/multiplatform-discover-project.html)
