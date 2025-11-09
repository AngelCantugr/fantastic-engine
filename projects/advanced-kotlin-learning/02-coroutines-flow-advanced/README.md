# Project 02: Coroutines & Flow Advanced

**Complexity:** ⭐⭐⭐ (Medium-Advanced)

**Duration:** 4-5 days

**Prerequisites:** Basic coroutines knowledge, suspend functions, basic Flow

## Overview

Master advanced coroutines and Flow patterns including StateFlow, SharedFlow, Channel operators, and the Select expression. Learn to build reactive, concurrent systems with proper error handling and backpressure management.

## Learning Objectives

- ✅ Master StateFlow vs SharedFlow vs Flow
- ✅ Understand cold vs hot flows
- ✅ Build complex channel pipelines
- ✅ Use Select expressions for multiplexing
- ✅ Handle backpressure correctly
- ✅ Implement proper error handling
- ✅ Apply structured concurrency patterns

## What You'll Build

1. **Reactive State Manager** - StateFlow-based state management
2. **Event Bus System** - SharedFlow for event broadcasting
3. **Pipeline Processor** - Channel-based data processing
4. **WebSocket Handler** - Real-time communication with Flow
5. **Actor Model** - Concurrent actors using channels

## Key Concepts

- StateFlow, SharedFlow, Channel differences
- Cold vs Hot flows
- Select expressions
- Backpressure strategies (buffer, conflate, collectLatest)
- Flow operators (flatMapMerge, combine, zip)
- Structured concurrency
- Exception handling in flows

## Quick Example

```kotlin
class ViewModel {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun loadData() = viewModelScope.launch {
        repository.getData()
            .onStart { _state.value = UiState.Loading }
            .catch { _state.value = UiState.Error(it) }
            .collect { _state.value = UiState.Success(it) }
    }
}
```

## Documentation

- 📖 [**Concepts**](docs/01-concepts.md) - StateFlow, SharedFlow, Channel, Select
- 💡 [**Usage**](docs/02-usage.md) - Practical patterns and best practices
- 🎯 [**Scenarios**](docs/03-scenarios.md) - Real-world scenarios
- ✏️ [**Exercises**](docs/04-exercises.md) - Hands-on practice

## Success Criteria

- [ ] Understand StateFlow vs SharedFlow vs Flow
- [ ] Handle backpressure correctly
- [ ] Use Select expressions
- [ ] Implement proper error handling
- [ ] Build reactive systems
- [ ] Complete all exercises

## Resources

- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [StateFlow and SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)
- [Channel Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/)
