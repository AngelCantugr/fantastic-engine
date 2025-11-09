"""
Advanced Descriptor Examples
Demonstrates the descriptor protocol and practical applications.
"""

from typing import Any, Type, Optional, Callable, Dict
import weakref
import re
from datetime import datetime


# Example 1: Type-Validated Descriptors
class TypedProperty:
    """Descriptor that enforces type checking."""

    def __init__(self, name: str, expected_type: Type) -> None:
        self.name = name
        self.expected_type = expected_type

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.name] = value


class Person:
    """Person with type-validated attributes."""

    name = TypedProperty("name", str)
    age = TypedProperty("age", int)
    email = TypedProperty("email", str)

    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name
        self.age = age
        self.email = email


# Example 2: Lazy Property (Computed Once)
class LazyProperty:
    """Descriptor that computes value once and caches it."""

    def __init__(self, func: Callable) -> None:
        self.func = func
        self.name = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self

        # Check if already computed
        if self.name not in obj.__dict__:
            # Compute and cache in instance dict
            print(f"[LazyProperty] Computing {self.name}...")
            obj.__dict__[self.name] = self.func(obj)

        return obj.__dict__[self.name]


class DataSet:
    """Dataset with lazy-computed statistics."""

    def __init__(self, data: list[float]) -> None:
        self.data = data

    @LazyProperty
    def mean(self) -> float:
        """Calculate mean (computed once)."""
        return sum(self.data) / len(self.data)

    @LazyProperty
    def variance(self) -> float:
        """Calculate variance (computed once)."""
        m = self.mean
        return sum((x - m) ** 2 for x in self.data) / len(self.data)

    @LazyProperty
    def std_dev(self) -> float:
        """Calculate standard deviation (computed once)."""
        return self.variance ** 0.5


# Example 3: Validation Descriptors
class Validated:
    """Base descriptor with validation hook."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def __set_name__(self, owner: Type, name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj: Any, value: Any) -> None:
        self.validate(value)
        obj.__dict__[self.name] = value

    def validate(self, value: Any) -> None:
        """Override in subclasses."""
        pass


class PositiveNumber(Validated):
    """Validates positive numbers."""

    def validate(self, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")


class String(Validated):
    """Validates string with length constraints."""

    def __init__(
        self,
        name: Optional[str] = None,
        min_length: int = 1,
        max_length: Optional[int] = None,
    ) -> None:
        super().__init__(name)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")

        if len(value) < self.min_length:
            raise ValueError(
                f"{self.name} must be at least {self.min_length} characters"
            )

        if self.max_length and len(value) > self.max_length:
            raise ValueError(
                f"{self.name} must be at most {self.max_length} characters"
            )


class Email(Validated):
    """Validates email format."""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")

        if not self.EMAIL_REGEX.match(value):
            raise ValueError(f"{self.name} must be a valid email address")


class RangeValue(Validated):
    """Validates value is within a range."""

    def __init__(
        self,
        name: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> None:
        super().__init__(name)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")


class Product:
    """Product with validated attributes."""

    name = String(min_length=3, max_length=50)
    price = PositiveNumber()
    quantity = PositiveNumber()
    discount = RangeValue(min_value=0.0, max_value=1.0)

    def __init__(
        self, name: str, price: float, quantity: int, discount: float = 0.0
    ) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity
        self.discount = discount

    def total_price(self) -> float:
        """Calculate total price with discount."""
        return self.price * self.quantity * (1 - self.discount)


# Example 4: History Tracking Descriptor
class Tracked:
    """Descriptor that tracks all changes to an attribute."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self.history: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    def __set_name__(self, owner: Type, name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self
        if obj not in self.history:
            return None
        return self.history[obj][-1][1] if self.history[obj] else None

    def __set__(self, obj: Any, value: Any) -> None:
        if obj not in self.history:
            self.history[obj] = []
        timestamp = datetime.now()
        self.history[obj].append((timestamp, value))

    def get_history(self, obj: Any) -> list[tuple[datetime, Any]]:
        """Get full history of changes."""
        return self.history.get(obj, []).copy()


class Configuration:
    """Configuration with change tracking."""

    setting1 = Tracked()
    setting2 = Tracked()

    def __init__(self) -> None:
        self.setting1 = "default1"
        self.setting2 = "default2"


# Example 5: Read-Only Descriptor
class ReadOnly:
    """Descriptor that allows setting only once (immutable after first set)."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    def __set_name__(self, owner: Type, name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj: Any, value: Any) -> None:
        if self.name in obj.__dict__:
            raise AttributeError(f"{self.name} is read-only and already set")
        obj.__dict__[self.name] = value


class ImmutableConfig:
    """Configuration with read-only fields."""

    api_key = ReadOnly()
    secret = ReadOnly()

    def __init__(self, api_key: str, secret: str) -> None:
        self.api_key = api_key
        self.secret = secret


# Example 6: Weakref Descriptor (Memory Efficient)
class WeakRefDescriptor:
    """Stores data using weakref to avoid memory leaks."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self.data: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    def __set_name__(self, owner: Type, name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Any:
        if obj is None:
            return self
        return self.data.get(obj, None)

    def __set__(self, obj: Any, value: Any) -> None:
        self.data[obj] = value


class CachedData:
    """Class with memory-efficient cached data."""

    cache = WeakRefDescriptor()

    def __init__(self, value: Any) -> None:
        self.cache = value


def demo() -> None:
    """Demonstrate all descriptor examples."""
    print("=" * 60)
    print("DESCRIPTOR EXAMPLES DEMONSTRATION")
    print("=" * 60)

    # Demo 1: Type-Validated Descriptors
    print("\n1. Type-Validated Descriptors:")
    person = Person("Alice", 30, "alice@example.com")
    print(f"Person: {person.name}, {person.age}, {person.email}")
    try:
        person.age = "invalid"
    except TypeError as e:
        print(f"  Error: {e}")

    # Demo 2: Lazy Properties
    print("\n2. Lazy Properties:")
    dataset = DataSet([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"  Mean: {dataset.mean}")
    print(f"  Mean (cached): {dataset.mean}")
    print(f"  Variance: {dataset.variance}")
    print(f"  Std Dev: {dataset.std_dev}")

    # Demo 3: Validated Attributes
    print("\n3. Validated Attributes:")
    product = Product("Widget", 19.99, 5, 0.1)
    print(f"  Product: {product.name}, ${product.price}, qty: {product.quantity}")
    print(f"  Total: ${product.total_price():.2f}")
    try:
        product.discount = 1.5
    except ValueError as e:
        print(f"  Error: {e}")

    # Demo 4: History Tracking
    print("\n4. History Tracking:")
    config = Configuration()
    print(f"  Initial setting1: {config.setting1}")
    config.setting1 = "new value 1"
    config.setting1 = "new value 2"
    config.setting1 = "new value 3"
    history = Tracked.get_history(Configuration.setting1, config)
    print(f"  History ({len(history)} changes):")
    for timestamp, value in history:
        print(f"    {timestamp.strftime('%H:%M:%S')}: {value}")

    # Demo 5: Read-Only Descriptor
    print("\n5. Read-Only Descriptor:")
    immutable = ImmutableConfig("key-123", "secret-456")
    print(f"  API Key: {immutable.api_key}")
    try:
        immutable.api_key = "new-key"
    except AttributeError as e:
        print(f"  Error: {e}")

    # Demo 6: Weakref Descriptor
    print("\n6. Weakref Descriptor:")
    cached = CachedData("important data")
    print(f"  Cached value: {cached.cache}")
    print("  (Instance will be garbage collected when deleted)")


if __name__ == "__main__":
    demo()
