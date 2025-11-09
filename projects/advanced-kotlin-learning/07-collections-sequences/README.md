# Project 07: Collections & Sequences

**Complexity:** ⭐⭐⭐⭐ (Advanced)

**Duration:** 3-4 days

**Prerequisites:** Collections basics, higher-order functions

## Overview

Master the difference between collections and sequences, lazy evaluation, performance optimization, and advanced collection operations. Learn when to use sequences for optimal performance.

## Learning Objectives

- ✅ Understand eager vs lazy evaluation
- ✅ Master sequence operations
- ✅ Optimize collection pipelines
- ✅ Create custom sequences
- ✅ Measure and improve performance
- ✅ Use appropriate collection operations

## What You'll Build

1. **Performance Benchmarks** - Compare collections vs sequences
2. **Custom Sequence** - Build infinite sequences
3. **Data Pipeline** - Optimized ETL pipeline
4. **Stream Processor** - Large file processing
5. **Query Optimizer** - Lazy query evaluation

## Key Concepts

- Collections (eager) vs Sequences (lazy)
- Intermediate vs terminal operations
- Sequence performance characteristics
- generateSequence and sequence builder
- Infinite sequences
- Performance benchmarking
- Memory efficiency

## Quick Example

```kotlin
// Collections (eager) - creates intermediate lists
val result1 = listOf(1, 2, 3, 4, 5)
    .map { it * 2 }        // New list created
    .filter { it > 5 }     // New list created
    .sum()                 // Terminal operation

// Sequences (lazy) - no intermediate collections
val result2 = listOf(1, 2, 3, 4, 5)
    .asSequence()
    .map { it * 2 }        // Lazy operation
    .filter { it > 5 }     // Lazy operation
    .sum()                 // Terminal operation triggers evaluation

// Infinite sequence
val fibonacci = generateSequence(0 to 1) { (a, b) ->
    b to (a + b)
}.map { it.first }

fibonacci.take(10).toList() // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Collections vs Sequences
- 💡 [**Usage**](docs/02-usage.md) - When to use what
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Performance optimization
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand eager vs lazy evaluation
- [ ] Choose collections vs sequences appropriately
- [ ] Create custom sequences
- [ ] Optimize data pipelines
- [ ] Complete all exercises

## Resources

- [Sequences Documentation](https://kotlinlang.org/docs/sequences.html)
- [Collections Overview](https://kotlinlang.org/docs/collections-overview.html)
