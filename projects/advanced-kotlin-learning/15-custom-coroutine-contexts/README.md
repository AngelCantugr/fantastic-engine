# Project 15: Custom Coroutine Contexts

**Complexity:** ⭐⭐⭐⭐⭐ (Expert)

**Duration:** 6-7 days

**Prerequisites:** Advanced coroutines, Flow, suspend functions

## Overview

Master the internals of coroutines by building custom dispatchers, interceptors, and continuation implementations. Understand how coroutines work under the hood.

## Learning Objectives

- ✅ Understand coroutine internals
- ✅ Build custom dispatchers
- ✅ Create continuation interceptors
- ✅ Implement custom context elements
- ✅ Handle coroutine cancellation
- ✅ Debug coroutines effectively

## What You'll Build

1. **Custom Dispatcher** - Thread pool dispatcher
2. **Logging Interceptor** - Trace coroutine execution
3. **Transaction Context** - Database transaction propagation
4. **Rate Limiter** - Dispatcher with rate limiting
5. **Debug Context** - Enhanced debugging tools

## Key Concepts

- CoroutineContext and Elements
- ContinuationInterceptor
- CoroutineDispatcher
- Continuation
- Structured concurrency implementation
- Cancellation mechanism
- Job lifecycle

## Quick Example

```kotlin
// Custom context element
class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>
}

// Custom dispatcher
class LoggingDispatcher(
    private val delegate: CoroutineDispatcher
) : CoroutineDispatcher() {
    override fun dispatch(context: CoroutineContext, block: Runnable) {
        println("Dispatching coroutine: $context")
        delegate.dispatch(context, block)
    }
}

// Usage
suspend fun processRequest() = coroutineScope {
    val requestId = coroutineContext[RequestId]?.id ?: "unknown"
    println("Processing request: $requestId")
}

launch(Dispatchers.Default + RequestId("123")) {
    processRequest()
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - Coroutine internals
- 💡 [**Usage**](docs/02-usage.md) - Building custom contexts
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Advanced scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand coroutine internals
- [ ] Build custom dispatchers
- [ ] Create interceptors
- [ ] Handle cancellation correctly
- [ ] Complete all exercises

## Resources

- [Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
