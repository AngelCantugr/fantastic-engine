"""
Advanced Context Manager Examples
Demonstrates practical context manager patterns.
"""

from contextlib import contextmanager
from typing import Any, Optional, Generator
import time
import os
import tempfile
import shutil
from pathlib import Path


# Example 1: Class-Based File Manager with Logging
class ManagedFile:
    """File context manager with detailed logging."""

    def __init__(self, filename: str, mode: str = 'r') -> None:
        self.filename = filename
        self.mode = mode
        self.file: Optional[Any] = None

    def __enter__(self) -> Any:
        print(f"[OPEN] {self.filename} in mode '{self.mode}'")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if self.file:
            print(f"[CLOSE] {self.filename}")
            self.file.close()

        if exc_type is not None:
            print(f"[ERROR] {exc_type.__name__}: {exc_value}")

        return False  # Don't suppress exceptions


# Example 2: Timer Context Manager
class Timer:
    """Measures and reports execution time."""

    def __init__(self, name: str = "Operation") -> None:
        self.name = name
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> 'Timer':
        print(f"[START] {self.name}")
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        self.elapsed = time.perf_counter() - self.start_time
        print(f"[END] {self.name} completed in {self.elapsed:.4f} seconds")
        return False


# Example 3: Temporary Directory Manager
@contextmanager
def temporary_directory(prefix: str = "tmp_") -> Generator[Path, None, None]:
    """Create and clean up a temporary directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    print(f"[CREATE] Temporary directory: {temp_dir}")
    try:
        yield temp_dir
    finally:
        print(f"[DELETE] Temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


# Example 4: State Change Manager
class TemporaryState:
    """Temporarily modifies object state, then restores it."""

    def __init__(self, obj: Any, **new_state: Any) -> None:
        self.obj = obj
        self.new_state = new_state
        self.old_state: dict[str, Any] = {}

    def __enter__(self) -> Any:
        # Save current state
        for key in self.new_state:
            if hasattr(self.obj, key):
                self.old_state[key] = getattr(self.obj, key)
            else:
                self.old_state[key] = None

        # Apply new state
        for key, value in self.new_state.items():
            setattr(self.obj, key, value)
            print(f"[SET] {key} = {value}")

        return self.obj

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # Restore old state
        for key, value in self.old_state.items():
            if value is None and key in self.new_state:
                delattr(self.obj, key)
            else:
                setattr(self.obj, key, value)
            print(f"[RESTORE] {key} = {value}")

        return False


# Example 5: Change Directory Context Manager
@contextmanager
def change_directory(path: str) -> Generator[None, None, None]:
    """Temporarily change working directory."""
    old_dir = os.getcwd()
    print(f"[CD] {old_dir} -> {path}")
    os.chdir(path)
    try:
        yield
    finally:
        print(f"[CD] {path} -> {old_dir}")
        os.chdir(old_dir)


# Example 6: Environment Variable Manager
@contextmanager
def temporary_env(**env_vars: str) -> Generator[None, None, None]:
    """Temporarily set environment variables."""
    old_env: dict[str, Optional[str]] = {}

    # Save old values and set new ones
    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value
        print(f"[ENV] Set {key}={value}")

    try:
        yield
    finally:
        # Restore old values
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
                print(f"[ENV] Removed {key}")
            else:
                os.environ[key] = old_value
                print(f"[ENV] Restored {key}={old_value}")


# Example 7: Database Transaction Simulator
class DatabaseTransaction:
    """Simulates database transaction with commit/rollback."""

    def __init__(self, name: str = "Transaction") -> None:
        self.name = name
        self.operations: list[str] = []

    def execute(self, operation: str) -> None:
        """Add operation to transaction."""
        self.operations.append(operation)
        print(f"  [EXEC] {operation}")

    def __enter__(self) -> 'DatabaseTransaction':
        print(f"[BEGIN] {self.name}")
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if exc_type is None:
            print(f"[COMMIT] {self.name} ({len(self.operations)} operations)")
        else:
            print(f"[ROLLBACK] {self.name} due to {exc_type.__name__}")
            self.operations.clear()

        return False  # Don't suppress exceptions


# Example 8: Resource Pool Manager
class ResourcePool:
    """Manages a pool of limited resources."""

    def __init__(self, resources: list[str]) -> None:
        self.available = list(resources)
        self.in_use: set[str] = set()
        self._current_resource: Optional[str] = None

    def __enter__(self) -> str:
        if not self.available:
            raise RuntimeError("No resources available in pool")

        self._current_resource = self.available.pop(0)
        self.in_use.add(self._current_resource)
        print(f"[ACQUIRE] Resource: {self._current_resource}")
        print(f"  Available: {len(self.available)}, In use: {len(self.in_use)}")
        return self._current_resource

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if self._current_resource:
            self.in_use.remove(self._current_resource)
            self.available.append(self._current_resource)
            print(f"[RELEASE] Resource: {self._current_resource}")
            print(f"  Available: {len(self.available)}, In use: {len(self.in_use)}")
            self._current_resource = None

        return False


# Example 9: Suppress Specific Exceptions
@contextmanager
def suppress_exceptions(*exception_types: type[Exception]) -> Generator[None, None, None]:
    """Suppress specific exception types."""
    try:
        yield
    except exception_types as e:
        print(f"[SUPPRESSED] {type(e).__name__}: {e}")


# Example 10: Retry Context Manager
class Retry:
    """Retry operations on failure."""

    def __init__(self, max_attempts: int = 3, delay: float = 0.1) -> None:
        self.max_attempts = max_attempts
        self.delay = delay
        self.attempt = 0

    def __enter__(self) -> 'Retry':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if exc_type is None:
            return False

        self.attempt += 1
        if self.attempt < self.max_attempts:
            print(
                f"[RETRY] Attempt {self.attempt}/{self.max_attempts} "
                f"failed: {exc_type.__name__}"
            )
            time.sleep(self.delay)
            return True  # Suppress exception to retry
        else:
            print(f"[FAILED] All {self.max_attempts} attempts exhausted")
            return False  # Propagate exception


def demo() -> None:
    """Demonstrate all context manager examples."""
    print("=" * 60)
    print("CONTEXT MANAGER EXAMPLES DEMONSTRATION")
    print("=" * 60)

    # Demo 1: Managed File
    print("\n1. Managed File:")
    with ManagedFile("/tmp/test.txt", "w") as f:
        f.write("Hello, World!")

    # Demo 2: Timer
    print("\n2. Timer:")
    with Timer("Computation"):
        result = sum(i**2 for i in range(100000))

    # Demo 3: Temporary Directory
    print("\n3. Temporary Directory:")
    with temporary_directory("my_temp_") as temp_dir:
        test_file = temp_dir / "test.txt"
        test_file.write_text("temporary content")
        print(f"  Created file: {test_file}")

    # Demo 4: Temporary State
    print("\n4. Temporary State:")

    class Config:
        debug = False
        verbose = False

    config = Config()
    print(f"  Initial: debug={config.debug}, verbose={config.verbose}")

    with TemporaryState(config, debug=True, verbose=True):
        print(f"  Inside: debug={config.debug}, verbose={config.verbose}")

    print(f"  Restored: debug={config.debug}, verbose={config.verbose}")

    # Demo 5: Environment Variables
    print("\n5. Environment Variables:")
    with temporary_env(TEST_VAR="test_value", DEBUG="true"):
        print(f"  TEST_VAR={os.environ.get('TEST_VAR')}")

    # Demo 6: Database Transaction
    print("\n6. Database Transaction:")
    with DatabaseTransaction("User Creation") as tx:
        tx.execute("INSERT INTO users VALUES ('alice', 30)")
        tx.execute("INSERT INTO accounts VALUES ('alice', 1000)")

    # Demo 7: Resource Pool
    print("\n7. Resource Pool:")
    pool = ResourcePool(["conn1", "conn2", "conn3"])

    with pool as conn:
        print(f"  Using connection: {conn}")

    with pool as conn:
        print(f"  Using connection: {conn}")

    # Demo 8: Suppress Exceptions
    print("\n8. Suppress Exceptions:")
    with suppress_exceptions(ValueError, KeyError):
        print("  Raising ValueError...")
        raise ValueError("This will be suppressed")
    print("  Continued after suppressed exception")


if __name__ == "__main__":
    demo()
