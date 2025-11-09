// Project 07: Concurrent Processor
// Comprehensive examples of concurrency and parallelism in Rust

use std::sync::{Arc, Mutex, RwLock, mpsc};
use std::thread;
use std::time::Duration;

fn main() {
    println!("🦀 Concurrency & Parallelism in Rust");
    println!("=====================================\n");

    // Run all example functions
    basic_threads();
    thread_with_move();
    thread_return_values();
    message_passing_basic();
    message_passing_multiple_senders();
    shared_state_mutex();
    shared_state_arc_mutex();
    rwlock_example();
    send_sync_traits();
    thread_pool_pattern();
    producer_consumer_pattern();
    parallel_computation();
    error_handling_threads();
}

// ============================================================================
// 1. BASIC THREADS
// ============================================================================

fn basic_threads() {
    println!("🧵 Basic Thread Creation");
    println!("-------------------------");

    let handle = thread::spawn(|| {
        for i in 1..5 {
            println!("  Child thread: {}", i);
            thread::sleep(Duration::from_millis(10));
        }
    });

    for i in 1..3 {
        println!("Main thread: {}", i);
        thread::sleep(Duration::from_millis(10));
    }

    // Wait for thread to finish
    handle.join().unwrap();
    println!("Child thread completed!\n");
}

// ============================================================================
// 2. THREAD WITH MOVE CLOSURE
// ============================================================================

fn thread_with_move() {
    println!("📦 Thread with Move Closure");
    println!("----------------------------");

    let v = vec![1, 2, 3, 4, 5];

    let handle = thread::spawn(move || {
        println!("  Vector in thread: {:?}", v);
        v.len()  // Can return values!
    });

    // v is no longer accessible here (moved into thread)
    // println!("{:?}", v);  // ERROR!

    let len = handle.join().unwrap();
    println!("Vector length from thread: {}\n", len);
}

// ============================================================================
// 3. THREAD RETURN VALUES
// ============================================================================

fn thread_return_values() {
    println!("↩️  Thread Return Values");
    println!("------------------------");

    let handles: Vec<_> = (0..5)
        .map(|i| {
            thread::spawn(move || {
                thread::sleep(Duration::from_millis(i * 10));
                i * i  // Return square
            })
        })
        .collect();

    let results: Vec<_> = handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect();

    println!("Results: {:?}\n", results);
}

// ============================================================================
// 4. MESSAGE PASSING - BASIC CHANNEL
// ============================================================================

fn message_passing_basic() {
    println!("📨 Message Passing - Basic");
    println!("--------------------------");

    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let messages = vec![
            "Hello",
            "from",
            "the",
            "thread",
        ];

        for msg in messages {
            tx.send(msg).unwrap();
            thread::sleep(Duration::from_millis(100));
        }
    });

    // Receive messages
    for received in rx {
        println!("  Received: {}", received);
    }

    println!();
}

// ============================================================================
// 5. MESSAGE PASSING - MULTIPLE SENDERS
// ============================================================================

fn message_passing_multiple_senders() {
    println!("📬 Multiple Senders (mpsc)");
    println!("--------------------------");

    let (tx, rx) = mpsc::channel();
    let mut handles = vec![];

    for i in 0..3 {
        let tx_clone = tx.clone();
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let msg = format!("Thread {} - Message {}", i, j);
                tx_clone.send(msg).unwrap();
                thread::sleep(Duration::from_millis(50));
            }
        });
        handles.push(handle);
    }

    // Drop the original sender
    drop(tx);

    // Collect all messages
    for received in rx {
        println!("  {}", received);
    }

    // Wait for all threads
    for handle in handles {
        handle.join().unwrap();
    }

    println!();
}

// ============================================================================
// 6. SHARED STATE - MUTEX
// ============================================================================

fn shared_state_mutex() {
    println!("🔒 Shared State - Mutex");
    println!("-----------------------");

    let m = Mutex::new(5);

    {
        let mut num = m.lock().unwrap();
        *num = 6;
        println!("  Locked and modified: {}", num);
    }  // Lock is released here (RAII)

    println!("  Final value: {:?}\n", m);
}

// ============================================================================
// 7. SHARED STATE - ARC + MUTEX
// ============================================================================

fn shared_state_arc_mutex() {
    println!("🔗 Shared State - Arc<Mutex<T>>");
    println!("--------------------------------");

    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for i in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter_clone.lock().unwrap();
            *num += 1;
            println!("  Thread {} incremented counter", i);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final counter value: {}\n", *counter.lock().unwrap());
}

// ============================================================================
// 8. RWLOCK EXAMPLE
// ============================================================================

fn rwlock_example() {
    println!("📚 RwLock - Read-Write Lock");
    println!("---------------------------");

    let data = Arc::new(RwLock::new(vec![1, 2, 3]));
    let mut handles = vec![];

    // Spawn multiple readers
    for i in 0..3 {
        let data_clone = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let r = data_clone.read().unwrap();
            println!("  Reader {}: {:?}", i, *r);
            thread::sleep(Duration::from_millis(100));
        });
        handles.push(handle);
    }

    // Spawn a writer
    let data_clone = Arc::clone(&data);
    let handle = thread::spawn(move || {
        thread::sleep(Duration::from_millis(50));
        let mut w = data_clone.write().unwrap();
        w.push(4);
        println!("  Writer: Added element 4");
    });
    handles.push(handle);

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final data: {:?}\n", *data.read().unwrap());
}

// ============================================================================
// 9. SEND AND SYNC TRAITS
// ============================================================================

fn send_sync_traits() {
    println!("🏷️  Send and Sync Traits");
    println!("------------------------");

    // Helper functions to check Send and Sync
    fn is_send<T: Send>() -> &'static str {
        "Send ✓"
    }

    fn is_sync<T: Sync>() -> &'static str {
        "Sync ✓"
    }

    // Most types are Send and Sync
    println!("  Vec<i32>: {} {}", is_send::<Vec<i32>>(), is_sync::<Vec<i32>>());
    println!("  String: {} {}", is_send::<String>(), is_sync::<String>());
    println!("  Arc<i32>: {} {}", is_send::<Arc<i32>>(), is_sync::<Arc<i32>>());
    println!("  Mutex<i32>: {} {}", is_send::<Mutex<i32>>(), is_sync::<Mutex<i32>>());

    // Rc is NOT Send or Sync
    use std::rc::Rc;
    // println!("Rc<i32>: {} {}", is_send::<Rc<i32>>(), is_sync::<Rc<i32>>());  // ERROR!

    println!("  Rc<i32>: NOT Send, NOT Sync ✗");

    println!();
}

// ============================================================================
// 10. THREAD POOL PATTERN
// ============================================================================

fn thread_pool_pattern() {
    println!("🏊 Thread Pool Pattern");
    println!("----------------------");

    const NUM_THREADS: usize = 4;
    let (tx, rx) = mpsc::channel();
    let rx = Arc::new(Mutex::new(rx));
    let mut handles = vec![];

    // Create worker threads
    for id in 0..NUM_THREADS {
        let rx_clone = Arc::clone(&rx);
        let handle = thread::spawn(move || {
            loop {
                let job = rx_clone.lock().unwrap().recv();
                match job {
                    Ok(num) => {
                        println!("  Worker {} processing: {}", id, num);
                        thread::sleep(Duration::from_millis(50));
                    }
                    Err(_) => {
                        println!("  Worker {} shutting down", id);
                        break;
                    }
                }
            }
        });
        handles.push(handle);
    }

    // Send work to the pool
    for i in 0..10 {
        tx.send(i).unwrap();
    }

    // Close the channel
    drop(tx);

    // Wait for all workers
    for handle in handles {
        handle.join().unwrap();
    }

    println!();
}

// ============================================================================
// 11. PRODUCER-CONSUMER PATTERN
// ============================================================================

fn producer_consumer_pattern() {
    println!("🏭 Producer-Consumer Pattern");
    println!("----------------------------");

    let (tx, rx) = mpsc::channel();

    // Producer thread
    let producer = thread::spawn(move || {
        for i in 0..5 {
            println!("  Producer: Creating item {}", i);
            tx.send(i).unwrap();
            thread::sleep(Duration::from_millis(100));
        }
        println!("  Producer: Done");
    });

    // Consumer thread
    let consumer = thread::spawn(move || {
        for item in rx {
            println!("  Consumer: Processing item {}", item);
            thread::sleep(Duration::from_millis(150));
        }
        println!("  Consumer: Done");
    });

    producer.join().unwrap();
    consumer.join().unwrap();

    println!();
}

// ============================================================================
// 12. PARALLEL COMPUTATION
// ============================================================================

fn parallel_computation() {
    println!("⚡ Parallel Computation");
    println!("----------------------");

    let data = vec![1, 2, 3, 4, 5, 6, 7, 8];
    let chunk_size = 2;
    let chunks: Vec<_> = data.chunks(chunk_size).collect();

    let handles: Vec<_> = chunks
        .into_iter()
        .map(|chunk| {
            let chunk = chunk.to_vec();
            thread::spawn(move || {
                let sum: i32 = chunk.iter().sum();
                println!("  Chunk {:?} sum: {}", chunk, sum);
                sum
            })
        })
        .collect();

    let results: Vec<_> = handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect();

    let total: i32 = results.iter().sum();
    println!("Total sum: {}\n", total);
}

// ============================================================================
// 13. ERROR HANDLING IN THREADS
// ============================================================================

fn error_handling_threads() {
    println!("❌ Error Handling in Threads");
    println!("-----------------------------");

    // Thread that panics
    let handle1 = thread::spawn(|| {
        panic!("Thread 1 panicked!");
    });

    // Thread that succeeds
    let handle2 = thread::spawn(|| {
        println!("  Thread 2 succeeded");
        42
    });

    // Join and handle errors
    match handle1.join() {
        Ok(_) => println!("Thread 1 succeeded"),
        Err(e) => println!("  Thread 1 panicked: {:?}", e),
    }

    match handle2.join() {
        Ok(val) => println!("  Thread 2 returned: {}", val),
        Err(e) => println!("Thread 2 panicked: {:?}", e),
    }

    println!();
}

// ============================================================================
// REAL-WORLD EXAMPLES
// ============================================================================

// Example 1: Concurrent File Processor
fn _concurrent_file_processor() {
    struct FileProcessor {
        files: Vec<String>,
    }

    impl FileProcessor {
        fn process_parallel(&self) -> Vec<usize> {
            let mut handles = vec![];

            for file in &self.files {
                let file = file.clone();
                let handle = thread::spawn(move || {
                    // Simulate processing
                    thread::sleep(Duration::from_millis(10));
                    file.len()
                });
                handles.push(handle);
            }

            handles
                .into_iter()
                .map(|h| h.join().unwrap())
                .collect()
        }
    }
}

// Example 2: Thread-Safe Counter
struct Counter {
    count: Arc<Mutex<i32>>,
}

impl Counter {
    fn new() -> Self {
        Counter {
            count: Arc::new(Mutex::new(0)),
        }
    }

    fn increment(&self) {
        let mut count = self.count.lock().unwrap();
        *count += 1;
    }

    fn value(&self) -> i32 {
        *self.count.lock().unwrap()
    }
}

// Example 3: Task Queue
struct TaskQueue<T> {
    queue: Arc<Mutex<Vec<T>>>,
}

impl<T> TaskQueue<T> {
    fn new() -> Self {
        TaskQueue {
            queue: Arc::new(Mutex::new(Vec::new())),
        }
    }

    fn push(&self, task: T) {
        let mut queue = self.queue.lock().unwrap();
        queue.push(task);
    }

    fn pop(&self) -> Option<T> {
        let mut queue = self.queue.lock().unwrap();
        queue.pop()
    }

    fn len(&self) -> usize {
        let queue = self.queue.lock().unwrap();
        queue.len()
    }
}

// ============================================================================
// EXERCISE SOLUTIONS (Commented out)
// ============================================================================

/*
/// Exercise 1: Parallel Counter
fn parallel_counter() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                let mut num = counter_clone.lock().unwrap();
                *num += 1;
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    assert_eq!(*counter.lock().unwrap(), 10000);
    println!("Counter: {}", *counter.lock().unwrap());
}

/// Exercise 2: Producer-Consumer with multiple producers
fn multi_producer_consumer() {
    let (tx, rx) = mpsc::channel();

    // Spawn 3 producers
    for i in 0..3 {
        let tx_clone = tx.clone();
        thread::spawn(move || {
            for j in 0..5 {
                tx_clone.send((i, j)).unwrap();
                thread::sleep(Duration::from_millis(10));
            }
        });
    }

    drop(tx);

    // Single consumer
    let consumer = thread::spawn(move || {
        let mut count = 0;
        for (producer, value) in rx {
            println!("Producer {} sent {}", producer, value);
            count += 1;
        }
        count
    });

    let total = consumer.join().unwrap();
    println!("Total messages: {}", total);
}

/// Exercise 3: Parallel Map
fn parallel_map<T, F, R>(data: Vec<T>, f: F) -> Vec<R>
where
    T: Send + 'static,
    F: Fn(T) -> R + Send + Sync + 'static,
    R: Send + 'static,
{
    use std::sync::Arc;

    let f = Arc::new(f);
    let handles: Vec<_> = data
        .into_iter()
        .map(|item| {
            let f_clone = Arc::clone(&f);
            thread::spawn(move || f_clone(item))
        })
        .collect();

    handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect()
}

/// Exercise 4: Read-Write Cache
struct Cache<K, V> {
    data: Arc<RwLock<std::collections::HashMap<K, V>>>,
}

impl<K, V> Cache<K, V>
where
    K: Eq + std::hash::Hash + Clone,
    V: Clone,
{
    fn new() -> Self {
        Cache {
            data: Arc::new(RwLock::new(std::collections::HashMap::new())),
        }
    }

    fn get(&self, key: &K) -> Option<V> {
        let data = self.data.read().unwrap();
        data.get(key).cloned()
    }

    fn insert(&self, key: K, value: V) {
        let mut data = self.data.write().unwrap();
        data.insert(key, value);
    }
}
*/
