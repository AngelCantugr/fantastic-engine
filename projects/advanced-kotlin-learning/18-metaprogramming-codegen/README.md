# Project 18: Metaprogramming & Code Generation

**Complexity:** ⭐⭐⭐⭐⭐ (Expert)

**Duration:** 6-7 days

**Prerequisites:** KSP, annotations, AST concepts, KotlinPoet

## Overview

Master metaprogramming and code generation techniques including AST manipulation, template-based generation, and building complete code generation systems.

## Learning Objectives

- ✅ Understand AST (Abstract Syntax Tree)
- ✅ Generate code with KotlinPoet
- ✅ Build template engines
- ✅ Create macro systems
- ✅ Manipulate syntax trees
- ✅ Design code generators

## What You'll Build

1. **ORM Generator** - Generate repository code
2. **API Client Generator** - From OpenAPI specs
3. **State Machine Generator** - Generate state machines
4. **Serializer Generator** - Custom serialization
5. **Mock Generator** - Generate test mocks

## Key Concepts

- KotlinPoet for code generation
- AST manipulation
- Template-based generation
- Symbol processing
- Code generation patterns
- File generation
- Import management

## Quick Example

```kotlin
import com.squareup.kotlinpoet.*

// Generate a data class
fun generateDataClass(name: String, properties: Map<String, TypeName>): FileSpec {
    val classBuilder = TypeSpec.classBuilder(name)
        .addModifiers(KModifier.DATA)

    val constructorBuilder = FunSpec.constructorBuilder()

    properties.forEach { (propName, propType) ->
        classBuilder.addProperty(
            PropertySpec.builder(propName, propType)
                .initializer(propName)
                .build()
        )

        constructorBuilder.addParameter(propName, propType)
    }

    classBuilder.primaryConstructor(constructorBuilder.build())

    return FileSpec.builder("com.example", name)
        .addType(classBuilder.build())
        .build()
}

// Usage
val userClass = generateDataClass("User", mapOf(
    "id" to Long::class.asTypeName(),
    "name" to String::class.asTypeName(),
    "email" to String::class.asTypeName().copy(nullable = true)
))

userClass.writeTo(System.out)
// Generates:
// data class User(
//     val id: Long,
//     val name: String,
//     val email: String?
// )
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Metaprogramming theory
- 💡 [**Usage**](docs/02-usage.md) - Code generation patterns
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Complex generators
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand AST concepts
- [ ] Generate code with KotlinPoet
- [ ] Build working generators
- [ ] Design template systems
- [ ] Complete all exercises

## Resources

- [KotlinPoet](https://square.github.io/kotlinpoet/)
- [Code Generation Guide](https://square.github.io/kotlinpoet/kotlinpoet/)
