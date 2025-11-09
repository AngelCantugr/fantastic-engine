# Project 14: C Extensions - Performance Boost

**Difficulty:** Advanced ⭐⭐⭐⭐⭐

## Core Concepts

C extensions allow you to write performance-critical code in C/C++ and call it from Python.

## Why Use C Extensions?

- **Performance**: 10-100x speedup for CPU-bound tasks
- **Legacy Code**: Interface with existing C libraries
- **System Access**: Low-level system operations
- **Protection**: Obfuscate proprietary algorithms

## Modern Approaches

### 1. ctypes (No Compilation)
```python
import ctypes

# Load C library
libc = ctypes.CDLL("libc.so.6")  # Linux
# libc = ctypes.CDLL("msvcrt.dll")  # Windows

# Call C function
libc.printf(b"Hello from C!\n")

# Define types
libc.sqrt.argtypes = [ctypes.c_double]
libc.sqrt.restype = ctypes.c_double

result = libc.sqrt(25.0)
print(result)  # 5.0
```

### 2. cffi (C Foreign Function Interface)
```python
from cffi import FFI

ffi = FFI()

# Define C signatures
ffi.cdef("""
    int add(int a, int b);
""")

# Compile inline C code
lib = ffi.verify("""
    int add(int a, int b) {
        return a + b;
    }
""")

result = lib.add(5, 3)
print(result)  # 8
```

### 3. Cython (Python-like C Extension)
```python
# example.pyx
def fibonacci(int n):
    cdef int a = 0, b = 1, i
    for i in range(n):
        a, b = b, a + b
    return a

# Compile with: cythonize -i example.pyx
# Import: from example import fibonacci
```

### 4. pybind11 (Modern C++)
```cpp
// example.cpp
#include <pybind11/pybind11.h>

int add(int a, int b) {
    return a + b;
}

PYBIND11_MODULE(example, m) {
    m.def("add", &add, "Add two numbers");
}

// Compile and use in Python:
// import example
// example.add(5, 3)
```

## Performance Comparison

```python
import time

# Pure Python
def fibonacci_python(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Measure
start = time.time()
result = fibonacci_python(1000000)
python_time = time.time() - start

# C extension would be 10-100x faster!
```

## When to Use C Extensions

✅ **Use when:**
- CPU-intensive computations
- Need native library access
- Performance critical paths
- Processing large data volumes

❌ **Avoid when:**
- Pure I/O operations (use async instead)
- Premature optimization
- Code maintainability is priority
- Python solution is fast enough

## Building C Extensions

### setup.py
```python
from setuptools import setup, Extension

module = Extension(
    'mymodule',
    sources=['mymodule.c'],
    extra_compile_args=['-O3']  # Optimize
)

setup(
    name='MyModule',
    version='1.0',
    ext_modules=[module]
)

# Build: python setup.py build_ext --inplace
```

### Basic C Extension
```c
// mymodule.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* add(PyObject* self, PyObject* args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b))
        return NULL;
    return PyLong_FromLong(a + b);
}

static PyMethodDef methods[] = {
    {"add", add, METH_VARARGS, "Add two integers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "mymodule",
    "Example module",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_mymodule(void) {
    return PyModule_Create(&module);
}
```

## Modern Alternatives

### NumPy/NumExpr
```python
import numpy as np
import numexpr as ne

# NumPy (C-optimized)
a = np.array([1, 2, 3, 4, 5])
result = np.sum(a ** 2)  # Fast C code!

# NumExpr (even faster for expressions)
result = ne.evaluate("sum(a ** 2)")
```

### Numba (JIT Compilation)
```python
from numba import jit

@jit(nopython=True)  # Compile to machine code
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# First call compiles, subsequent calls are fast!
```

## Key Takeaways
- C extensions provide major performance boost
- Use ctypes for existing libraries
- cffi for dynamic C code
- Cython for Python-like syntax
- pybind11 for modern C++
- Consider Numba/NumPy first
- Profile before optimizing
- Maintain pure Python fallback

## References
- Python C API - https://docs.python.org/3/c-api/
- ctypes - https://docs.python.org/3/library/ctypes.html
- Cython - https://cython.org/
- pybind11 - https://pybind11.readthedocs.io/
