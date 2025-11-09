# Project 13: Bytecode Optimization - Under the Hood

**Difficulty:** Advanced ⭐⭐⭐⭐⭐

## Core Concepts

Python compiles source code to bytecode (intermediate representation) executed by the Python VM.

## Viewing Bytecode

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

Output:
```
  2           0 LOAD_FAST                0 (a)
              2 LOAD_FAST                1 (b)
              4 BINARY_ADD
              6 RETURN_VALUE
```

## Understanding Bytecode

```python
# Each instruction has:
# - Line number
# - Offset
# - Opcode name
# - Arguments
# - Interpretation

def example():
    x = 1        # LOAD_CONST, STORE_FAST
    y = 2        # LOAD_CONST, STORE_FAST
    return x + y # LOAD_FAST, LOAD_FAST, BINARY_ADD, RETURN_VALUE
```

## Optimization Insights

### 1. Constant Folding (done by compiler)
```python
# Python optimizes constants at compile time
x = 24 * 60 * 60  # Compiled to: x = 86400

import dis
dis.dis(lambda: 24 * 60 * 60)
# Shows: LOAD_CONST (86400) - pre-calculated!
```

### 2. Loop Optimization
```python
# Slower - attribute lookup in loop
def slow_loop(items):
    result = []
    for item in items:
        result.append(item * 2)  # Looks up 'append' each time
    return result

# Faster - hoist lookup
def fast_loop(items):
    result = []
    append = result.append  # Single lookup
    for item in items:
        append(item * 2)
    return result
```

### 3. Local vs Global Access
```python
import dis

global_var = 10

def use_global():
    return global_var  # LOAD_GLOBAL (slower)

def use_local():
    local_var = 10
    return local_var   # LOAD_FAST (faster)

# Locals are faster!
```

## Code Objects

```python
def my_function(x):
    return x * 2

code = my_function.__code__

print(f"Arguments: {code.co_argcount}")
print(f"Locals: {code.co_nlocals}")
print(f"Constants: {code.co_consts}")
print(f"Names: {code.co_names}")
print(f"Bytecode: {code.co_code}")
```

## Practical Patterns

### Peephole Optimization
```python
# Python's peephole optimizer simplifies bytecode

# Example: Jump optimization
# Multiple jumps combined
# Dead code eliminated
# Constant expressions folded
```

### Custom Bytecode Generation
```python
import types

def create_function_from_bytecode():
    """Advanced: Create function from bytecode."""
    # Build code object manually
    code = compile("return 42", "<string>", "eval")

    func = types.FunctionType(
        code,
        globals(),
        "generated_func"
    )
    return func

func = create_function_from_bytecode()
print(func())  # 42
```

## Profiling Bytecode

```python
import sys

def trace_bytecode(frame, event, arg):
    """Trace bytecode execution."""
    if event == 'call':
        code = frame.f_code
        print(f"Calling: {code.co_name}")
    return trace_bytecode

sys.settrace(trace_bytecode)
```

## Key Takeaways
- Bytecode is intermediate representation
- `dis` module for viewing bytecode
- Local variable access is faster than global
- Python optimizes constant expressions
- Understanding bytecode helps optimization
- Not usually needed for regular development
- Useful for performance-critical code

## References
- dis module - https://docs.python.org/3/library/dis.html
- Python bytecode - https://docs.python.org/3/library/inspect.html
- CPython internals - https://devguide.python.org/
