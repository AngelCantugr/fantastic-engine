# Project 11: Advanced Type System - Static Typing Mastery

**Difficulty:** Advanced ⭐⭐⭐⭐⭐

## Core Concepts

Python's type system enables static analysis, IDE support, and self-documenting code through type hints.

## Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# Type-safe usage
int_stack: Stack[int] = Stack()
int_stack.push(1)  # OK
# int_stack.push("string")  # Type error!
```

## Union Types & Literal

```python
from typing import Union, Literal

def process(value: Union[int, str]) -> str:
    """Accept int or str."""
    return str(value)

# Python 3.10+ syntax
def process_modern(value: int | str) -> str:
    return str(value)

# Literal types
Mode = Literal["read", "write", "append"]

def open_file(filename: str, mode: Mode) -> None:
    pass

open_file("data.txt", "read")  # OK
# open_file("data.txt", "invalid")  # Type error!
```

## TypedDict

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> None:
    print(data["name"])

create_user({"name": "Alice", "age": 30, "email": "a@b.com"})
```

## Callable Types

```python
from typing import Callable

def apply_operation(
    x: int,
    y: int,
    operation: Callable[[int, int], int]
) -> int:
    return operation(x, y)

def add(a: int, b: int) -> int:
    return a + b

result = apply_operation(5, 3, add)
```

## Advanced Patterns

### Overloading
```python
from typing import overload

@overload
def process(value: int) -> int: ...

@overload
def process(value: str) -> str: ...

def process(value: Union[int, str]) -> Union[int, str]:
    if isinstance(value, int):
        return value * 2
    return value.upper()
```

### Type Guards
```python
from typing import TypeGuard

def is_string_list(val: List[object]) -> TypeGuard[List[str]]:
    return all(isinstance(x, str) for x in val)

def process_strings(items: List[object]) -> None:
    if is_string_list(items):
        # Type checker knows items is List[str]
        print(items[0].upper())
```

## Key Takeaways
- Use `Generic[T]` for generic classes
- `Union` or `|` for multiple types
- `TypedDict` for structured dictionaries
- `Callable` for function parameters
- `@overload` for multiple signatures
- Type hints improve IDE support and catch bugs early

## References
- PEP 484 - Type Hints
- mypy documentation - http://mypy-lang.org/
- typing module - https://docs.python.org/3/library/typing.html
