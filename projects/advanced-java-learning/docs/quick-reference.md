# Advanced Java Quick Reference Guide

A concise reference for all 20 projects with code snippets and common patterns.

---

## Project Index

| # | Project | Difficulty | Key API/Tools |
|---|---------|------------|---------------|
| 01 | Custom Collections | ⭐⭐⭐ | Generics, Iterator, Comparable |
| 02 | NIO.2 Explorer | ⭐⭐⭐ | Path, Files, WatchService |
| 03 | Reflection & Annotations | ⭐⭐⭐ | Class, Field, Method, @Retention |
| 04 | Multithreading | ⭐⭐⭐ | ExecutorService, Locks, volatile |
| 05 | Stream API | ⭐⭐⭐ | Stream, Collectors, Optional |
| 06 | Serialization | ⭐⭐⭐⭐ | Externalizable, ObjectStream |
| 07 | Concurrent Structures | ⭐⭐⭐⭐ | ConcurrentHashMap, Atomic*, CAS |
| 08 | Dynamic Proxy & AOP | ⭐⭐⭐⭐ | Proxy, InvocationHandler |
| 09 | Memory Management | ⭐⭐⭐⭐ | GC, MemoryMXBean, Heap Analysis |
| 10 | Async Programming | ⭐⭐⭐⭐ | CompletableFuture, Reactive |
| 11 | DI Container | ⭐⭐⭐⭐⭐ | Reflection, Annotations, Lifecycle |
| 12 | Bytecode Manipulation | ⭐⭐⭐⭐⭐ | ASM, ByteBuddy, ClassLoader |
| 13 | NIO Server | ⭐⭐⭐⭐⭐ | Selector, SocketChannel, Buffer |
| 14 | Distributed Cache | ⭐⭐⭐⭐⭐ | Consistent Hashing, Replication |
| 15 | JVM Language | ⭐⭐⭐⭐⭐ | Parser, AST, Code Generation |
| 16 | Lock-Free Algorithms | ⭐⭐⭐⭐⭐⭐ | AtomicReference, VarHandle, ABA |
| 17 | GraalVM & JIT | ⭐⭐⭐⭐⭐⭐ | Native Image, AOT, Optimizations |
| 18 | Distributed TX | ⭐⭐⭐⭐⭐⭐ | 2PC, Saga, Compensation |
| 19 | Zero-Copy & Off-Heap | ⭐⭐⭐⭐⭐⭐ | DirectBuffer, Unsafe, mmap |
| 20 | Microservices Framework | ⭐⭐⭐⭐⭐⭐ | Service Mesh, Circuit Breaker |

---

## Common Patterns Cheat Sheet

### Generics

```java
// Basic generic class
class Box<T> {
    private T value;
    public T get() { return value; }
    public void set(T value) { this.value = value; }
}

// Bounded type parameter
class NumberBox<T extends Number> {
    private T value;
    public double doubleValue() { return value.doubleValue(); }
}

// Wildcards
void process(List<?> list) { }                    // Unknown type
void processNumbers(List<? extends Number> list) { }  // Upper bound
void addNumbers(List<? super Integer> list) { }   // Lower bound

// Multiple bounds
class Util<T extends Comparable<T> & Serializable> { }
```

### Concurrency

```java
// ExecutorService patterns
ExecutorService executor = Executors.newFixedThreadPool(4);
Future<Result> future = executor.submit(() -> doWork());
Result result = future.get(10, TimeUnit.SECONDS);
executor.shutdown();

// Lock patterns
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // Critical section
} finally {
    lock.unlock();  // Always in finally!
}

// Atomic operations
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();
counter.compareAndSet(expected, newValue);

// CompletableFuture
CompletableFuture.supplyAsync(() -> fetch())
    .thenApply(this::transform)
    .thenAccept(this::process)
    .exceptionally(ex -> handleError(ex));
```

### Streams

```java
// Common operations
list.stream()
    .filter(x -> x > 0)           // Keep only positive
    .map(String::valueOf)         // Transform
    .sorted()                     // Sort
    .distinct()                   // Remove duplicates
    .limit(10)                    // First 10
    .skip(5)                      // Skip first 5
    .forEach(System.out::println);

// Collectors
.collect(Collectors.toList())
.collect(Collectors.toSet())
.collect(Collectors.joining(", "))
.collect(Collectors.groupingBy(User::getCity))
.collect(Collectors.partitioningBy(x -> x > 0))
.collect(Collectors.summarizingInt(User::getAge))

// Reduce
.reduce(0, Integer::sum)
.reduce((a, b) -> a + b)
.reduce(Integer::max)
```

### NIO.2

```java
// Path operations
Path path = Paths.get("/home/user/file.txt");
Path parent = path.getParent();
Path filename = path.getFileName();
Path absolute = path.toAbsolutePath();
Path normalized = path.normalize();

// File operations
Files.exists(path)
Files.isDirectory(path)
Files.createFile(path)
Files.createDirectories(path)
Files.copy(source, target, REPLACE_EXISTING)
Files.move(source, target, ATOMIC_MOVE)
Files.delete(path)
Files.readAllLines(path)
Files.write(path, lines)

// Walking directory tree
try (Stream<Path> paths = Files.walk(root)) {
    paths.filter(Files::isRegularFile)
         .filter(p -> p.toString().endsWith(".java"))
         .forEach(System.out::println);
}

// Watch service
WatchService watcher = FileSystems.getDefault().newWatchService();
path.register(watcher, ENTRY_CREATE, ENTRY_MODIFY, ENTRY_DELETE);
WatchKey key = watcher.take();
for (WatchEvent<?> event : key.pollEvents()) {
    // Handle event
}
```

### Reflection

```java
// Class inspection
Class<?> clazz = obj.getClass();
String name = clazz.getName();
Package pkg = clazz.getPackage();
Class<?> superClass = clazz.getSuperclass();
Class<?>[] interfaces = clazz.getInterfaces();

// Field access
Field field = clazz.getDeclaredField("fieldName");
field.setAccessible(true);
Object value = field.get(obj);
field.set(obj, newValue);

// Method invocation
Method method = clazz.getDeclaredMethod("methodName", paramTypes);
method.setAccessible(true);
Object result = method.invoke(obj, args);

// Constructor
Constructor<?> ctor = clazz.getDeclaredConstructor(paramTypes);
ctor.setAccessible(true);
Object instance = ctor.newInstance(args);

// Annotations
Annotation[] annotations = clazz.getAnnotations();
MyAnnotation ann = clazz.getAnnotation(MyAnnotation.class);
boolean present = clazz.isAnnotationPresent(MyAnnotation.class);
```

### Annotations

```java
// Define annotation
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Timed {
    TimeUnit unit() default TimeUnit.MILLISECONDS;
}

// Use annotation
@Timed(unit = TimeUnit.SECONDS)
public void myMethod() { }

// Process annotation
for (Method method : clazz.getDeclaredMethods()) {
    if (method.isAnnotationPresent(Timed.class)) {
        Timed timed = method.getAnnotation(Timed.class);
        // Use timed.unit()
    }
}
```

---

## Performance Comparison Tables

### Collection Operations

| Operation | ArrayList | LinkedList | HashSet | TreeSet |
|-----------|-----------|------------|---------|---------|
| add(E) | O(1)* | O(1) | O(1) | O(log n) |
| add(i,E) | O(n) | O(n) | N/A | N/A |
| get(i) | O(1) | O(n) | N/A | N/A |
| remove(i) | O(n) | O(n) | N/A | N/A |
| contains(E) | O(n) | O(n) | O(1) | O(log n) |
| iterator.remove() | O(n) | O(1) | O(1) | O(log n) |

\* Amortized, O(n) worst case when resizing

### Concurrent Collections

| Collection | Thread-Safety | Performance | Use Case |
|------------|---------------|-------------|----------|
| Vector | synchronized | Slow | Legacy, avoid |
| Collections.synchronizedList | synchronized | Slow | Simple wrapping |
| CopyOnWriteArrayList | Lock-free reads | Writes expensive | Read-heavy |
| ConcurrentHashMap | Lock-free | Fast | General purpose |
| ConcurrentLinkedQueue | Lock-free | Fast | FIFO queue |
| LinkedBlockingQueue | Locks | Good | Producer-consumer |

### Serialization Performance

| Method | Speed | Size | Cross-Language |
|--------|-------|------|----------------|
| Java Serialization | Slow | Large | No |
| Externalizable | Medium | Medium | No |
| JSON | Medium | Large | Yes |
| Protocol Buffers | Fast | Small | Yes |
| Custom Binary | Fastest | Smallest | Maybe |

---

## JVM Flags Reference

### Memory Settings

```bash
# Heap size
-Xms2g                    # Initial heap size
-Xmx4g                    # Maximum heap size
-XX:MaxMetaspaceSize=512m # Metaspace limit (Java 8+)

# GC Selection
-XX:+UseG1GC              # G1 (default Java 9+)
-XX:+UseZGC               # ZGC (low latency, Java 15+)
-XX:+UseShenandoahGC      # Shenandoah (low latency)
-XX:+UseParallelGC        # Parallel (throughput)

# GC Tuning
-XX:MaxGCPauseMillis=200  # Target pause time
-XX:GCTimeRatio=19        # Throughput goal (1/(1+ratio))
-XX:+UseStringDeduplication # Reduce string memory

# Debugging
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/heapdump.hprof
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xlog:gc*:file=/tmp/gc.log # Java 9+ unified logging
```

### Performance Flags

```bash
# JIT Compilation
-XX:+TieredCompilation    # Use tiered compiler (default)
-XX:CompileThreshold=10000 # Method invocation threshold
-XX:+PrintCompilation     # Log JIT compilation

# Optimizations
-XX:+UseCompressedOops    # Compress object pointers (default on 64-bit)
-XX:+UseCompressedClassPointers
-XX:+AggressiveOpts       # Experimental optimizations

# Profiling
-XX:+UnlockDiagnosticVMOptions
-XX:+LogCompilation
-XX:+PrintInlining
```

---

## Common Pitfalls and Solutions

### 1. ConcurrentModificationException

```java
// WRONG
for (String item : list) {
    if (condition) {
        list.remove(item);  // Exception!
    }
}

// RIGHT
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    if (condition) {
        iter.remove();  // Safe
    }
}

// BETTER (Java 8+)
list.removeIf(item -> condition);
```

### 2. Resource Leaks

```java
// WRONG
FileInputStream fis = new FileInputStream("file.txt");
// Forgot to close!

// RIGHT
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // Use fis
}  // Auto-closed

// ALSO RIGHT
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    // Use fis
} finally {
    if (fis != null) fis.close();
}
```

### 3. Thread Interrupt Handling

```java
// WRONG
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    e.printStackTrace();  // Loses interrupt status!
}

// RIGHT
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();  // Restore status
    // Handle or propagate
}
```

### 4. Optional Misuse

```java
// WRONG
Optional<String> opt = Optional.ofNullable(value);
if (opt.isPresent()) {
    return opt.get();  // Defeats purpose!
} else {
    return "default";
}

// RIGHT
return Optional.ofNullable(value).orElse("default");

// BETTER
return Optional.ofNullable(value)
    .map(String::toUpperCase)
    .orElseThrow(() -> new IllegalStateException("Missing value"));
```

### 5. Stream Reuse

```java
// WRONG
Stream<String> stream = list.stream();
stream.forEach(System.out::println);
stream.count();  // IllegalStateException!

// RIGHT
long count = list.stream()
    .peek(System.out::println)  // Side effect during stream
    .count();
```

---

## Testing Templates

### Unit Test Template

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class MyClassTest {

    private MyClass instance;

    @BeforeEach
    void setUp() {
        instance = new MyClass();
    }

    @Test
    void testNormalCase() {
        assertEquals(expected, instance.method(input));
    }

    @Test
    void testEdgeCase() {
        assertThrows(IllegalArgumentException.class,
            () -> instance.method(invalidInput));
    }

    @Test
    @Timeout(value = 1, unit = TimeUnit.SECONDS)
    void testPerformance() {
        instance.expensiveOperation();
    }
}
```

### Concurrent Test Template

```java
import org.junit.jupiter.api.Test;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

class ConcurrentTest {

    @Test
    void testThreadSafety() throws Exception {
        int threads = 10;
        int iterations = 1000;

        Counter counter = new Counter();
        ExecutorService executor = Executors.newFixedThreadPool(threads);

        CountDownLatch latch = new CountDownLatch(threads);

        for (int i = 0; i < threads; i++) {
            executor.submit(() -> {
                for (int j = 0; j < iterations; j++) {
                    counter.increment();
                }
                latch.countDown();
            });
        }

        latch.await(10, TimeUnit.SECONDS);
        executor.shutdown();

        assertEquals(threads * iterations, counter.get());
    }
}
```

---

## Further Learning Resources

### Books (Must-Read)
1. **Java Concurrency in Practice** - Brian Goetz
2. **Effective Java (3rd Edition)** - Joshua Bloch
3. **Java Performance** - Scott Oaks
4. **Well-Grounded Java Developer** - Benjamin Evans

### Online Resources
- [OpenJDK Source Code](https://github.com/openjdk/jdk)
- [JEPs (Enhancement Proposals)](https://openjdk.org/jeps/0)
- [Baeldung](https://www.baeldung.com/)
- [InfoQ Java](https://www.infoq.com/java/)

### Tools
- **Profilers:** JProfiler, YourKit, Async-Profiler
- **Monitoring:** VisualVM, JConsole, Mission Control
- **Benchmarking:** JMH (Java Microbenchmark Harness)
- **Analysis:** JOL (Java Object Layout), Eclipse MAT

---

## Quick Command Reference

```bash
# Compile
javac -d bin src/**/*.java

# Run with profiling
java -Xlog:gc* -XX:+PrintCompilation MyClass

# Create JAR
jar cvf myapp.jar -C bin .

# Run JAR
java -jar myapp.jar

# JVM tools
jps          # List Java processes
jstat -gc PID 1000  # GC stats every 1s
jmap -heap PID      # Heap summary
jstack PID          # Thread dump
jcmd PID help       # All available commands

# Memory analysis
jmap -dump:format=b,file=heap.bin PID
jhat heap.bin  # Or use Eclipse MAT

# Flight Recorder (low overhead profiling)
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr MyClass
```

---

This quick reference covers the essential concepts and patterns across all 20 projects. Refer back to individual project documentation for deeper explanations and complete implementations.
