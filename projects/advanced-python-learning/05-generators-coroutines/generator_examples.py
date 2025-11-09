"""
Advanced Generator and Coroutine Examples
Demonstrates lazy evaluation, pipelines, and coroutine patterns.
"""

from typing import Iterator, Generator, Any, Callable
from functools import wraps
from itertools import islice
import time


# Coroutine decorator for auto-priming
def coroutine(func: Callable) -> Callable:
    """Decorator to automatically prime coroutines."""

    @wraps(func)
    def primer(*args: Any, **kwargs: Any) -> Generator:
        gen = func(*args, **kwargs)
        next(gen)  # Prime the coroutine
        return gen

    return primer


# Example 1: Infinite Sequences
def fibonacci() -> Iterator[int]:
    """Generate infinite fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def primes() -> Iterator[int]:
    """Generate infinite prime numbers."""
    yield 2
    primes_found = [2]

    candidate = 3
    while True:
        is_prime = True
        for prime in primes_found:
            if prime * prime > candidate:
                break
            if candidate % prime == 0:
                is_prime = False
                break

        if is_prime:
            primes_found.append(candidate)
            yield candidate

        candidate += 2


# Example 2: File Processing Pipeline
def read_lines(filename: str) -> Iterator[str]:
    """Read file line by line (memory efficient)."""
    try:
        with open(filename) as f:
            for line in f:
                yield line.strip()
    except FileNotFoundError:
        print(f"[WARNING] File {filename} not found")
        return


def filter_comments(lines: Iterator[str]) -> Iterator[str]:
    """Filter out comment lines."""
    for line in lines:
        if line and not line.startswith("#"):
            yield line


def process_lines(lines: Iterator[str]) -> Iterator[str]:
    """Process each line."""
    for line in lines:
        yield line.upper()


# Example 3: Batching Iterator
def batch(iterable: Iterator[Any], n: int) -> Iterator[list[Any]]:
    """Yield batches of n items."""
    batch_items: list[Any] = []
    for item in iterable:
        batch_items.append(item)
        if len(batch_items) == n:
            yield batch_items
            batch_items = []
    if batch_items:  # Yield remaining items
        yield batch_items


# Example 4: Sliding Window
def sliding_window(iterable: Iterator[Any], size: int) -> Iterator[tuple]:
    """Generate sliding windows over iterable."""
    from collections import deque

    window = deque(maxlen=size)

    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)


# Example 5: Tree Traversal
class Node:
    """Tree node for traversal examples."""

    def __init__(self, value: Any, children: list['Node'] | None = None) -> None:
        self.value = value
        self.children = children or []


def traverse_depth_first(node: Node) -> Iterator[Any]:
    """Depth-first tree traversal."""
    yield node.value
    for child in node.children:
        yield from traverse_depth_first(child)


def traverse_breadth_first(root: Node) -> Iterator[Any]:
    """Breadth-first tree traversal."""
    from collections import deque

    queue = deque([root])
    while queue:
        node = queue.popleft()
        yield node.value
        queue.extend(node.children)


# Example 6: Flatten Nested Structures
def flatten(nested: Any) -> Iterator[Any]:
    """Recursively flatten nested iterables."""
    if isinstance(nested, (list, tuple)):
        for item in nested:
            yield from flatten(item)
    else:
        yield nested


# Example 7: Running Average Coroutine
@coroutine
def running_average() -> Generator[float | None, float, None]:
    """Calculate running average of sent values."""
    total = 0.0
    count = 0
    average = None

    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


# Example 8: Grep Coroutine
@coroutine
def grep(pattern: str) -> Generator[None, str, None]:
    """Filter lines containing pattern."""
    print(f"[GREP] Looking for '{pattern}'")
    while True:
        line = yield
        if pattern in line:
            print(f"  Match: {line}")


# Example 9: Broadcaster Coroutine
@coroutine
def broadcast(*targets: Generator) -> Generator[None, Any, None]:
    """Send received values to multiple targets."""
    while True:
        value = yield
        for target in targets:
            target.send(value)


# Example 10: Coroutine Pipeline
@coroutine
def filter_even(target: Generator) -> Generator[None, int, None]:
    """Filter even numbers and send to target."""
    while True:
        value = yield
        if value % 2 == 0:
            target.send(value)


@coroutine
def multiply(factor: int, target: Generator) -> Generator[None, int, None]:
    """Multiply by factor and send to target."""
    while True:
        value = yield
        target.send(value * factor)


@coroutine
def consumer() -> Generator[None, Any, None]:
    """Final consumer that prints values."""
    while True:
        value = yield
        print(f"  Result: {value}")


# Example 11: Cooperative Multitasking
def task(name: str, count: int) -> Iterator[None]:
    """Simulated task that yields control."""
    for i in range(count):
        print(f"  {name} - step {i + 1}")
        yield
    print(f"  {name} - completed")


def scheduler(*tasks: Iterator) -> None:
    """Simple round-robin task scheduler."""
    task_list = list(tasks)
    while task_list:
        current_task = task_list.pop(0)
        try:
            next(current_task)
            task_list.append(current_task)  # Re-queue
        except StopIteration:
            pass  # Task complete


# Example 12: Generator with State
class StatefulGenerator:
    """Generator that maintains complex state."""

    def __init__(self, start: int = 0) -> None:
        self.value = start
        self.history: list[int] = []

    def __iter__(self) -> Iterator[int]:
        while True:
            self.history.append(self.value)
            yield self.value
            self.value += 1

    def get_history(self) -> list[int]:
        """Get generation history."""
        return self.history.copy()


# Example 13: Chunked File Reader
def read_chunks(filename: str, chunk_size: int = 1024) -> Iterator[str]:
    """Read file in chunks (memory efficient for large files)."""
    try:
        with open(filename, 'r') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError:
        print(f"[WARNING] File {filename} not found")
        return


# Example 14: Range with Float Step
def frange(start: float, stop: float, step: float) -> Iterator[float]:
    """Float range generator."""
    current = start
    while current < stop:
        yield current
        current += step


def demo() -> None:
    """Demonstrate all generator and coroutine examples."""
    print("=" * 60)
    print("GENERATOR & COROUTINE EXAMPLES DEMONSTRATION")
    print("=" * 60)

    # Demo 1: Infinite Sequences
    print("\n1. Infinite Fibonacci Sequence (first 10):")
    print(f"  {list(islice(fibonacci(), 10))}")

    print("\n2. Infinite Prime Numbers (first 10):")
    print(f"  {list(islice(primes(), 10))}")

    # Demo 3: Batching
    print("\n3. Batching:")
    for i, batch_items in enumerate(batch(range(10), 3), 1):
        print(f"  Batch {i}: {batch_items}")

    # Demo 4: Sliding Window
    print("\n4. Sliding Window:")
    windows = list(sliding_window(range(5), 3))
    print(f"  Windows: {windows}")

    # Demo 5: Tree Traversal
    print("\n5. Tree Traversal:")
    tree = Node(
        1, [Node(2, [Node(4), Node(5)]), Node(3, [Node(6, [Node(7)])])]
    )
    print(f"  Depth-first: {list(traverse_depth_first(tree))}")
    print(f"  Breadth-first: {list(traverse_breadth_first(tree))}")

    # Demo 6: Flatten
    print("\n6. Flatten Nested Structure:")
    nested = [1, [2, [3, 4], 5], 6, [7, [8, 9]]]
    print(f"  Nested: {nested}")
    print(f"  Flattened: {list(flatten(nested))}")

    # Demo 7: Running Average Coroutine
    print("\n7. Running Average Coroutine:")
    avg = running_average()
    for value in [10, 20, 30, 40]:
        result = avg.send(value)
        print(f"  Sent {value}, average: {result}")

    # Demo 8: Grep Coroutine
    print("\n8. Grep Coroutine:")
    g = grep("python")
    lines = [
        "python is awesome",
        "java is okay",
        "python rocks",
        "rust is fast",
        "python forever",
    ]
    for line in lines:
        g.send(line)

    # Demo 9: Coroutine Pipeline
    print("\n9. Coroutine Pipeline:")
    print("  Input: 1-10, Filter even, Multiply by 2")
    c = consumer()
    m = multiply(2, c)
    f = filter_even(m)

    for i in range(1, 11):
        f.send(i)

    # Demo 10: Cooperative Multitasking
    print("\n10. Cooperative Multitasking:")
    scheduler(task("Task-A", 3), task("Task-B", 3), task("Task-C", 2))

    # Demo 11: Float Range
    print("\n11. Float Range:")
    print(f"  {list(frange(0.0, 2.0, 0.3))}")

    # Demo 12: Broadcast Coroutine
    print("\n12. Broadcast Coroutine:")

    @coroutine
    def printer(prefix: str) -> Generator[None, Any, None]:
        while True:
            value = yield
            print(f"  {prefix}: {value}")

    p1 = printer("Listener-1")
    p2 = printer("Listener-2")
    p3 = printer("Listener-3")
    b = broadcast(p1, p2, p3)

    b.send("Hello")
    b.send("World")


if __name__ == "__main__":
    demo()
