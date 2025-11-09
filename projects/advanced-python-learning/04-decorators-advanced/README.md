# Project 04: Advanced Decorators - Function Transformation

**Difficulty:** Intermediate-Advanced ⭐⭐⭐⭐

## Core Concepts

Decorators are functions that modify or enhance other functions/classes. They use Python's `@` syntax and implement the concept of higher-order functions.

```mermaid
graph TD
    A[@decorator] --> B[original function]
    B --> C[decorator function]
    C --> D[wrapper function]
    D --> E[enhanced function]

    style A fill:#ff00ff,stroke:#00ffff
    style E fill:#00ff00,stroke:#00ffff
```

### Basic Decorator Pattern

```python
def decorator(func):
    """A decorator is a callable that returns a callable."""
    def wrapper(*args, **kwargs):
        # Before function call
        result = func(*args, **kwargs)
        # After function call
        return result
    return wrapper

@decorator
def my_function():
    pass

# Equivalent to:
my_function = decorator(my_function)
```

## Decorator Types

### 1. Function Decorators

```python
def timer(func):
    """Measure function execution time."""
    import time
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

### 2. Class Decorators

```python
def singleton(cls):
    """Make a class a singleton."""
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    pass
```

### 3. Method Decorators

```python
class MyClass:
    @staticmethod
    def static_method():
        """No self or cls parameter."""
        pass

    @classmethod
    def class_method(cls):
        """Receives class as first parameter."""
        pass

    @property
    def prop(self):
        """Accessed like an attribute."""
        return self._value
```

## Advanced Decorator Patterns

### Pattern 1: Decorators with Arguments

```python
def repeat(times):
    """Decorator factory - returns a decorator."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Prints 3 times
```

```mermaid
graph LR
    A[repeat(times=3)] --> B[returns decorator]
    B --> C[@decorator on greet]
    C --> D[returns wrapper]
    D --> E[greet = wrapper]

    style A fill:#ff00ff,stroke:#00ffff
    style E fill:#00ff00,stroke:#00ffff
```

### Pattern 2: Class-Based Decorators

```python
class CountCalls:
    """Decorator that counts function calls."""

    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def process():
    print("Processing...")

process()  # Call 1
process()  # Call 2
```

### Pattern 3: Preserving Function Metadata

```python
from functools import wraps

def decorator(func):
    @wraps(func)  # Preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def documented_function():
    """This docstring is preserved."""
    pass

print(documented_function.__name__)  # 'documented_function'
print(documented_function.__doc__)   # 'This docstring is preserved.'
```

## Practical Examples

### Example 1: Memoization Decorator

```python
from functools import wraps

def memoize(func):
    """Cache function results."""
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            print(f"Computing {func.__name__}{args}")
            cache[args] = func(*args)
        else:
            print(f"Using cached result for {args}")
        return cache[args]

    wrapper.cache = cache
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # Computes and caches
print(fibonacci(10))  # Uses cache
```

### Example 2: Validation Decorator

```python
from functools import wraps
from typing import get_type_hints

def validate_types(func):
    """Validate function arguments against type hints."""
    hints = get_type_hints(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get parameter names
        from inspect import signature
        sig = signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Validate each argument
        for name, value in bound.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"{name} must be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

        return func(*args, **kwargs)

    return wrapper

@validate_types
def greet(name: str, age: int) -> str:
    return f"{name} is {age} years old"

greet("Alice", 30)     # OK
# greet("Bob", "30")   # Raises TypeError
```

### Example 3: Retry Decorator

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1.0, exceptions=(Exception,)):
    """Retry function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    print(f"Attempt {attempts} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5, exceptions=(ConnectionError,))
def unreliable_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success"
```

### Example 4: Rate Limiting Decorator

```python
import time
from functools import wraps
from collections import deque

def rate_limit(max_calls, period):
    """Limit function calls to max_calls per period (seconds)."""
    calls = deque()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls outside the period
            while calls and calls[0] < now - period:
                calls.popleft()

            # Check if we can make another call
            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                print(f"Rate limit reached. Sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                return wrapper(*args, **kwargs)

            calls.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_calls=3, period=5.0)
def api_call():
    print(f"API called at {time.time():.2f}")
```

### Example 5: Access Control Decorator

```python
from functools import wraps

def require_permission(permission):
    """Check if user has required permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if not hasattr(user, 'permissions'):
                raise PermissionError("User has no permissions")

            if permission not in user.permissions:
                raise PermissionError(
                    f"User lacks permission: {permission}"
                )

            return func(user, *args, **kwargs)
        return wrapper
    return decorator

class User:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

@require_permission('admin')
def delete_user(user, target_id):
    return f"{user.name} deleted user {target_id}"

admin = User("Admin", ['admin', 'read', 'write'])
regular = User("Regular", ['read'])

delete_user(admin, 123)    # OK
# delete_user(regular, 123)  # Raises PermissionError
```

## Nuanced Scenarios

### Scenario 1: Stacking Decorators

```python
@decorator1
@decorator2
@decorator3
def func():
    pass

# Equivalent to:
func = decorator1(decorator2(decorator3(func)))

# Order matters!
@timer
@memoize
def compute(n):
    """Timer measures wrapper, not original function."""
    pass

@memoize
@timer
def compute(n):
    """Timer measures original function."""
    pass
```

### Scenario 2: Decorator with Optional Arguments

```python
from functools import wraps

def smart_decorator(func=None, *, option="default"):
    """Works with or without arguments."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Option: {option}")
            return func(*args, **kwargs)
        return wrapper

    if func is None:
        # Called with arguments: @smart_decorator(option="value")
        return decorator
    else:
        # Called without arguments: @smart_decorator
        return decorator(func)

@smart_decorator
def func1():
    pass

@smart_decorator(option="custom")
def func2():
    pass
```

### Scenario 3: Parametrized Class Decorator

```python
class Cache:
    """Class decorator with parameters."""

    def __init__(self, maxsize=128):
        self.maxsize = maxsize
        self.cache = {}

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args):
            if len(self.cache) >= self.maxsize:
                # Evict oldest entry
                self.cache.pop(next(iter(self.cache)))

            if args not in self.cache:
                self.cache[args] = func(*args)

            return self.cache[args]
        return wrapper

@Cache(maxsize=3)
def expensive(n):
    print(f"Computing {n}")
    return n ** 2
```

### Scenario 4: Decorator for Methods

```python
from functools import wraps

def method_decorator(func):
    """Decorator that works with methods (receives self)."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Calling {func.__name__} on {self.__class__.__name__}")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def method(self):
        return "result"
```

## Advanced Patterns

### Pattern: Context-Aware Decorator

```python
from contextvars import ContextVar
from functools import wraps

request_context = ContextVar('request_context', default=None)

def with_context(func):
    """Decorator that uses context variables."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = request_context.get()
        if context:
            print(f"Context: {context}")
        return func(*args, **kwargs)
    return wrapper

@with_context
def process_request():
    pass
```

### Pattern: Chaining Decorators

```python
class DecoratorChain:
    """Allows chaining decorators fluently."""

    def __init__(self, func):
        self.func = func
        self.decorators = []

    def add(self, decorator):
        """Add a decorator to the chain."""
        self.decorators.append(decorator)
        return self

    def __call__(self, *args, **kwargs):
        """Apply all decorators in order."""
        result = self.func
        for dec in reversed(self.decorators):
            result = dec(result)
        return result(*args, **kwargs)

# Usage
@DecoratorChain
def func():
    pass

func.add(timer).add(memoize).add(validate_types)
```

## Exercises

1. **Debug Decorator**: Create decorator that logs function arguments and return values
2. **Timeout Decorator**: Implement decorator that raises TimeoutError if function takes too long
3. **Deprecated Decorator**: Build decorator that warns when deprecated functions are called
4. **Profile Decorator**: Create decorator using `cProfile` to profile function performance

## Key Takeaways

- Decorators are functions that transform functions/classes
- Use `@wraps` to preserve function metadata
- Decorator factories return decorators (for parameterized decorators)
- Class-based decorators use `__call__` method
- Stack order matters when using multiple decorators
- Decorators can maintain state across calls
- Use decorators for cross-cutting concerns (logging, caching, validation)

## References

- PEP 318 - Decorators for Functions and Methods
- Python Decorator Library - https://wiki.python.org/moin/PythonDecoratorLibrary
- functools.wraps - https://docs.python.org/3/library/functools.html#functools.wraps
