"""
Advanced Decorator Examples
Demonstrates various decorator patterns and techniques.
"""

from functools import wraps, lru_cache
from typing import Any, Callable, TypeVar
import time
from collections import deque
from inspect import signature

F = TypeVar('F', bound=Callable[..., Any])


# Example 1: Timing Decorator
def timer(func: F) -> F:
    """Measure and print function execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper  # type: ignore


# Example 2: Memoization Decorator
def memoize(func: F) -> F:
    """Cache function results based on arguments."""
    cache: dict[tuple, Any] = {}

    @wraps(func)
    def wrapper(*args: Any) -> Any:
        if args not in cache:
            print(f"[MEMOIZE] Computing {func.__name__}{args}")
            cache[args] = func(*args)
        else:
            print(f"[MEMOIZE] Using cached result for {args}")
        return cache[args]

    wrapper.cache = cache  # type: ignore
    wrapper.cache_clear = lambda: cache.clear()  # type: ignore
    return wrapper  # type: ignore


@memoize
def fibonacci(n: int) -> int:
    """Compute fibonacci number (inefficient without memoization)."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Example 3: Retry Decorator
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Retry function on failure."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        print(f"[RETRY] Failed after {max_attempts} attempts")
                        raise
                    print(f"[RETRY] Attempt {attempts} failed: {e}. Retrying...")
                    time.sleep(delay)

        return wrapper  # type: ignore

    return decorator


# Example 4: Rate Limiting Decorator
def rate_limit(max_calls: int, period: float) -> Callable[[F], F]:
    """Limit function calls to max_calls per period (seconds)."""
    calls: deque[float] = deque()

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()

            # Remove old calls outside the period
            while calls and calls[0] < now - period:
                calls.popleft()

            # Check if we can make another call
            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                print(f"[RATE_LIMIT] Sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                # Retry after sleeping
                return wrapper(*args, **kwargs)

            calls.append(now)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


# Example 5: Validation Decorator
def validate_args(**validators: Callable[[Any], bool]) -> Callable[[F], F]:
    """Validate function arguments."""

    def decorator(func: F) -> F:
        sig = signature(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Bind arguments
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Validate each argument
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for {param_name}={value}"
                        )

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


@validate_args(
    age=lambda x: isinstance(x, int) and x > 0,
    name=lambda x: isinstance(x, str) and len(x) > 0,
)
def create_user(name: str, age: int) -> str:
    """Create a user with validation."""
    return f"Created user: {name}, age {age}"


# Example 6: Count Calls Decorator (Class-based)
class CountCalls:
    """Decorator that counts function calls."""

    def __init__(self, func: Callable) -> None:
        wraps(func)(self)
        self.func = func
        self.count = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1
        print(f"[COUNT] Call #{self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

    def reset(self) -> None:
        """Reset the counter."""
        self.count = 0


@CountCalls
def process_data(data: str) -> str:
    """Process some data."""
    return data.upper()


# Example 7: Debug Decorator
def debug(func: F) -> F:
    """Print function arguments and return value."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"[DEBUG] Calling {func.__name__}({signature})")

        result = func(*args, **kwargs)
        print(f"[DEBUG] {func.__name__} returned {result!r}")
        return result

    return wrapper  # type: ignore


@debug
def calculate(x: int, y: int, operation: str = "add") -> int:
    """Perform calculation."""
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    return 0


# Example 8: Decorator with Optional Arguments
def smart_cache(func: Callable | None = None, *, maxsize: int = 128) -> Callable:
    """Decorator that works with or without arguments."""

    def decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=maxsize)(func)

    if func is None:
        # Called with arguments: @smart_cache(maxsize=256)
        return decorator
    else:
        # Called without arguments: @smart_cache
        return decorator(func)


@smart_cache
def compute1(n: int) -> int:
    """Uses default maxsize."""
    return n ** 2


@smart_cache(maxsize=64)
def compute2(n: int) -> int:
    """Uses custom maxsize."""
    return n ** 3


# Example 9: Access Control Decorator
def require_permission(permission: str) -> Callable[[F], F]:
    """Check if user has required permission."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(user: Any, *args: Any, **kwargs: Any) -> Any:
            if not hasattr(user, "permissions"):
                raise PermissionError("User has no permissions")

            if permission not in user.permissions:
                raise PermissionError(f"User lacks permission: {permission}")

            return func(user, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


class User:
    """User with permissions."""

    def __init__(self, name: str, permissions: list[str]) -> None:
        self.name = name
        self.permissions = permissions


@require_permission("admin")
def delete_user(user: User, target_id: int) -> str:
    """Delete a user (requires admin permission)."""
    return f"{user.name} deleted user {target_id}"


# Example 10: Singleton Class Decorator
def singleton(cls: type) -> Callable:
    """Make a class a singleton."""
    instances: dict[type, Any] = {}

    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            print(f"[SINGLETON] Creating first instance of {cls.__name__}")
            instances[cls] = cls(*args, **kwargs)
        else:
            print(f"[SINGLETON] Returning existing instance of {cls.__name__}")
        return instances[cls]

    return get_instance


@singleton
class Database:
    """Singleton database connection."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        print(f"Connected to: {connection_string}")


def demo() -> None:
    """Demonstrate all decorator examples."""
    print("=" * 60)
    print("DECORATOR EXAMPLES DEMONSTRATION")
    print("=" * 60)

    # Demo 1: Timer
    print("\n1. Timer Decorator:")

    @timer
    def slow_function() -> None:
        time.sleep(0.1)

    slow_function()

    # Demo 2: Memoization
    print("\n2. Memoization Decorator:")
    print(f"fibonacci(10) = {fibonacci(10)}")
    print(f"fibonacci(10) = {fibonacci(10)}")  # Uses cache

    # Demo 3: Retry
    print("\n3. Retry Decorator:")

    @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
    def unreliable_function() -> str:
        import random

        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "Success"

    try:
        result = unreliable_function()
        print(f"  Result: {result}")
    except ValueError:
        print("  Failed after retries")

    # Demo 4: Rate Limiting
    print("\n4. Rate Limiting Decorator:")

    @rate_limit(max_calls=3, period=2.0)
    def api_call(data: str) -> None:
        print(f"  API called with: {data}")

    for i in range(5):
        api_call(f"request {i + 1}")

    # Demo 5: Validation
    print("\n5. Validation Decorator:")
    print(f"  {create_user('Alice', 30)}")
    try:
        create_user("", 30)
    except ValueError as e:
        print(f"  Error: {e}")

    # Demo 6: Count Calls
    print("\n6. Count Calls Decorator:")
    process_data("hello")
    process_data("world")
    process_data("python")

    # Demo 7: Debug
    print("\n7. Debug Decorator:")
    calculate(5, 3, operation="add")
    calculate(5, 3, operation="multiply")

    # Demo 8: Access Control
    print("\n8. Access Control Decorator:")
    admin = User("Admin", ["admin", "read", "write"])
    regular = User("Regular", ["read"])

    print(f"  {delete_user(admin, 123)}")
    try:
        delete_user(regular, 456)
    except PermissionError as e:
        print(f"  Error: {e}")

    # Demo 9: Singleton
    print("\n9. Singleton Decorator:")
    db1 = Database("localhost:5432")
    db2 = Database("different:3306")
    print(f"  db1 is db2: {db1 is db2}")


if __name__ == "__main__":
    demo()
