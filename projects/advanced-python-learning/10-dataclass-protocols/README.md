# Project 10: Dataclasses & Protocols - Modern Python Patterns

**Difficulty:** Upper Intermediate ⭐⭐⭐⭐

## Core Concepts

Dataclasses reduce boilerplate for data-holding classes. Protocols enable structural subtyping (duck typing with type hints).

## Dataclasses

### Basic Dataclass
```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str = "unknown"  # Default value

# Automatic __init__, __repr__, __eq__
person = Person("Alice", 30)
print(person)  # Person(name='Alice', age=30, email='unknown')
```

### Dataclass Features
```python
from dataclasses import dataclass, field

@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

@dataclass(order=True)  # Comparison methods
class Score:
    value: int

@dataclass
class Container:
    items: list = field(default_factory=list)  # Mutable default

    # Custom methods still work
    def add(self, item):
        self.items.append(item)
```

### Post-Init Processing
```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)  # Computed field

    def __post_init__(self):
        self.area = self.width * self.height
```

## Protocols (Structural Subtyping)

### Defining Protocols
```python
from typing import Protocol

class Drawable(Protocol):
    """Anything with a draw() method."""

    def draw(self) -> str:
        ...

# No need to inherit!
class Circle:
    def draw(self) -> str:
        return "Drawing circle"

class Square:
    def draw(self) -> str:
        return "Drawing square"

# Both are Drawable without explicit inheritance
def render(shape: Drawable) -> None:
    print(shape.draw())

render(Circle())  # OK
render(Square())  # OK
```

### Runtime Checkable Protocols
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int:
        ...

# Check at runtime
class MyList:
    def __len__(self):
        return 0

obj = MyList()
print(isinstance(obj, Sized))  # True
```

## Common Protocols

```python
from typing import Iterator, Iterable

# Iterator Protocol
class MyIterator(Protocol):
    def __next__(self) -> Any:
        ...
    def __iter__(self) -> 'MyIterator':
        ...

# Context Manager Protocol
class ContextManager(Protocol):
    def __enter__(self) -> Any:
        ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        ...

# Comparable Protocol
class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...
```

## Advanced Patterns

### Combining Dataclasses and Protocols
```python
from dataclasses import dataclass
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict:
        ...

@dataclass
class User:
    name: str
    age: int

    def to_dict(self) -> dict:
        return {"name": self.name, "age": self.age}

def save(obj: Serializable) -> None:
    print(f"Saving: {obj.to_dict()}")

save(User("Alice", 30))  # OK - User implements protocol
```

### Generic Protocols
```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Stack(Protocol[T]):
    def push(self, item: T) -> None:
        ...

    def pop(self) -> T:
        ...

# Any class with push/pop is a Stack
```

### Field Validators with Dataclasses
```python
from dataclasses import dataclass, field

def validate_positive(value: int) -> int:
    if value <= 0:
        raise ValueError("Must be positive")
    return value

@dataclass
class Product:
    name: str
    price: float = field(metadata={"validator": validate_positive})

    def __post_init__(self):
        # Manual validation
        if self.price <= 0:
            raise ValueError("Price must be positive")
```

## Dataclass vs NamedTuple vs Dict

```python
from dataclasses import dataclass
from typing import NamedTuple

# Dataclass - mutable, rich features
@dataclass
class PersonDC:
    name: str
    age: int

# NamedTuple - immutable, lightweight
class PersonNT(NamedTuple):
    name: str
    age: int

# Dict - flexible, no type safety
person_dict = {"name": "Alice", "age": 30}

# Choose based on needs:
# - Immutable + simple → NamedTuple
# - Mutable + features → Dataclass
# - Dynamic → Dict
```

## Key Takeaways

- `@dataclass` eliminates boilerplate
- Protocols enable duck typing with type hints
- No inheritance needed for protocols
- Use `frozen=True` for immutability
- `__post_init__` for computed fields
- Protocols checked statically by type checkers
- `@runtime_checkable` for isinstance checks
- Dataclasses work great with type hints

## References
- PEP 557 - Data Classes
- PEP 544 - Protocols: Structural Subtyping
- dataclasses module - https://docs.python.org/3/library/dataclasses.html
- typing.Protocol - https://docs.python.org/3/library/typing.html#typing.Protocol
