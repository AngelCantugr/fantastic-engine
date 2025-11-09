// Project 04: Collections & Data Processing
// Comprehensive examples of Rust collections and iterators

use std::collections::{HashMap, HashSet};

fn main() {
    println!("🦀 Collections & Data Processing");
    println!("=================================\n");

    vec_basics();
    vec_operations();
    hashmap_basics();
    hashmap_advanced();
    hashset_demo();
    iterator_basics();
    iterator_combinators();
    closures_demo();
    data_pipelines();
    real_world_examples();
}

/// Demonstrates Vec<T> basics
fn vec_basics() {
    println!("📦 Vec<T> Basics");
    println!("----------------");

    // Creating vectors
    let v1: Vec<i32> = Vec::new();
    let v2 = vec![1, 2, 3, 4, 5];
    let v3: Vec<i32> = Vec::with_capacity(10);

    println!("Empty vec: {:?}", v1);
    println!("Vec macro: {:?}", v2);
    println!("With capacity: {} (len: {}, cap: {})",
             v3.len(), v3.len(), v3.capacity());

    // Adding elements
    let mut v = Vec::new();
    v.push(1);
    v.push(2);
    v.push(3);
    println!("After pushing: {:?}", v);

    // Accessing elements
    let third = v[2];                    // Panics if out of bounds
    let third_safe = v.get(2);           // Returns Option
    println!("Third element: {}", third);
    println!("Third element (safe): {:?}", third_safe);

    // Getting first and last
    if let Some(&first) = v.first() {
        println!("First: {}", first);
    }
    if let Some(&last) = v.last() {
        println!("Last: {}", last);
    }

    // Removing elements
    let last = v.pop();
    println!("Popped: {:?}, Vec now: {:?}", last, v);

    // Length and capacity
    println!("Length: {}, Capacity: {}", v.len(), v.capacity());

    println!();
}

/// Demonstrates Vec operations
fn vec_operations() {
    println!("🔧 Vec Operations");
    println!("-----------------");

    let mut v = vec![1, 2, 3, 4, 5];

    // Insert and remove at specific index
    v.insert(2, 100);
    println!("After insert at 2: {:?}", v);

    v.remove(2);
    println!("After remove at 2: {:?}", v);

    // Iteration - three ways
    println!("Immutable iteration:");
    for item in &v {
        print!("{} ", item);
    }
    println!();

    println!("Mutable iteration:");
    for item in &mut v {
        *item *= 2;
    }
    println!("Doubled: {:?}", v);

    println!("Consuming iteration:");
    let v2 = vec![1, 2, 3];
    for item in v2 {  // v2 is moved
        print!("{} ", item);
    }
    println!();
    // println!("{:?}", v2);  // Error: v2 was moved

    // Slicing
    let slice = &v[1..4];
    println!("Slice [1..4]: {:?}", slice);

    // Splitting
    let (left, right) = v.split_at(2);
    println!("Split at 2: {:?} and {:?}", left, right);

    // Concatenation
    let mut v1 = vec![1, 2, 3];
    let v2 = vec![4, 5, 6];
    v1.extend(v2);
    println!("Extended: {:?}", v1);

    // Sorting
    let mut v = vec![5, 2, 8, 1, 9];
    v.sort();
    println!("Sorted: {:?}", v);

    // Reverse
    v.reverse();
    println!("Reversed: {:?}", v);

    // Contains
    if v.contains(&8) {
        println!("Contains 8!");
    }

    println!();
}

/// Demonstrates HashMap basics
fn hashmap_basics() {
    println!("🗺️  HashMap<K, V> Basics");
    println!("------------------------");

    // Creating HashMap
    let mut scores = HashMap::new();

    // Inserting
    scores.insert("Blue", 10);
    scores.insert("Red", 50);
    println!("Scores: {:?}", scores);

    // Accessing
    match scores.get("Blue") {
        Some(&score) => println!("Blue score: {}", score),
        None => println!("Blue not found"),
    }

    // Checking existence
    if scores.contains_key("Blue") {
        println!("Blue team exists");
    }

    // Updating
    scores.insert("Blue", 25);  // Replaces old value
    println!("After update: {:?}", scores);

    // Insert only if doesn't exist
    scores.entry("Yellow").or_insert(50);
    scores.entry("Blue").or_insert(100);  // Won't change Blue
    println!("After or_insert: {:?}", scores);

    // Iteration
    println!("All scores:");
    for (key, value) in &scores {
        println!("  {}: {}", key, value);
    }

    // Remove
    scores.remove("Yellow");
    println!("After removing Yellow: {:?}", scores);

    println!();
}

/// Demonstrates advanced HashMap patterns
fn hashmap_advanced() {
    println!("🎯 HashMap Advanced Patterns");
    println!("----------------------------");

    // Update based on old value
    let text = "hello world wonderful world";
    let mut word_count = HashMap::new();

    for word in text.split_whitespace() {
        let count = word_count.entry(word).or_insert(0);
        *count += 1;
    }
    println!("Word count: {:?}", word_count);

    // Creating from iterator
    let teams = vec![
        ("Blue".to_string(), 10),
        ("Red".to_string(), 50),
    ];
    let scores: HashMap<_, _> = teams.into_iter().collect();
    println!("From iterator: {:?}", scores);

    // Nested HashMap
    let mut player_stats: HashMap<String, HashMap<String, i32>> = HashMap::new();

    let mut alice_stats = HashMap::new();
    alice_stats.insert("score".to_string(), 100);
    alice_stats.insert("level".to_string(), 5);
    player_stats.insert("Alice".to_string(), alice_stats);

    println!("Player stats: {:?}", player_stats);

    // Get with default
    let score = player_stats
        .get("Alice")
        .and_then(|stats| stats.get("score"))
        .unwrap_or(&0);
    println!("Alice's score: {}", score);

    println!();
}

/// Demonstrates HashSet
fn hashset_demo() {
    println!("📚 HashSet<T>");
    println!("-------------");

    // Creating HashSet
    let mut set = HashSet::new();

    // Adding elements
    set.insert(1);
    set.insert(2);
    set.insert(3);
    set.insert(2);  // Duplicate - won't be added
    println!("Set: {:?}", set);

    // Checking membership
    if set.contains(&2) {
        println!("Set contains 2");
    }

    // Creating from Vec (removes duplicates)
    let numbers = vec![1, 2, 2, 3, 3, 3, 4, 5];
    let unique: HashSet<_> = numbers.into_iter().collect();
    println!("Unique numbers: {:?}", unique);

    // Set operations
    let a: HashSet<_> = [1, 2, 3, 4].iter().cloned().collect();
    let b: HashSet<_> = [3, 4, 5, 6].iter().cloned().collect();

    println!("A: {:?}", a);
    println!("B: {:?}", b);

    // Union
    let union: HashSet<_> = a.union(&b).cloned().collect();
    println!("Union: {:?}", union);

    // Intersection
    let intersection: HashSet<_> = a.intersection(&b).cloned().collect();
    println!("Intersection: {:?}", intersection);

    // Difference
    let difference: HashSet<_> = a.difference(&b).cloned().collect();
    println!("Difference (A - B): {:?}", difference);

    // Symmetric difference
    let sym_diff: HashSet<_> = a.symmetric_difference(&b).cloned().collect();
    println!("Symmetric difference: {:?}", sym_diff);

    // Subset check
    let small: HashSet<_> = [1, 2].iter().cloned().collect();
    if small.is_subset(&a) {
        println!("{:?} is subset of {:?}", small, a);
    }

    println!();
}

/// Demonstrates iterator basics
fn iterator_basics() {
    println!("🔄 Iterator Basics");
    println!("------------------");

    let v = vec![1, 2, 3, 4, 5];

    // Three types of iterators
    println!("iter() - borrows:");
    for item in v.iter() {
        print!("{} ", item);
    }
    println!();

    let mut v2 = vec![1, 2, 3];
    println!("iter_mut() - mutably borrows:");
    for item in v2.iter_mut() {
        *item *= 2;
    }
    println!("{:?}", v2);

    println!("into_iter() - takes ownership:");
    let v3 = vec![1, 2, 3];
    for item in v3.into_iter() {
        print!("{} ", item);
    }
    println!();
    // println!("{:?}", v3);  // Error: v3 was moved

    // Manual iteration
    let v = vec![1, 2, 3];
    let mut iter = v.iter();
    println!("Manual next(): {:?}", iter.next());
    println!("Manual next(): {:?}", iter.next());
    println!("Manual next(): {:?}", iter.next());
    println!("Manual next(): {:?}", iter.next());

    println!();
}

/// Demonstrates iterator combinators
fn iterator_combinators() {
    println!("🎨 Iterator Combinators");
    println!("-----------------------");

    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    // map - transform each element
    let doubled: Vec<_> = numbers.iter().map(|x| x * 2).collect();
    println!("Doubled: {:?}", doubled);

    // filter - keep only matching elements
    let evens: Vec<_> = numbers.iter().filter(|&&x| x % 2 == 0).collect();
    println!("Evens: {:?}", evens);

    // filter + map
    let even_squares: Vec<_> = numbers.iter()
        .filter(|&&x| x % 2 == 0)
        .map(|x| x * x)
        .collect();
    println!("Even squares: {:?}", even_squares);

    // take and skip
    let first_three: Vec<_> = numbers.iter().take(3).collect();
    println!("First 3: {:?}", first_three);

    let skip_five: Vec<_> = numbers.iter().skip(5).collect();
    println!("Skip 5: {:?}", skip_five);

    // enumerate - add index
    for (i, &value) in numbers.iter().enumerate() {
        println!("  [{}] = {}", i, value);
    }

    // zip - combine two iterators
    let names = vec!["Alice", "Bob", "Charlie"];
    let scores = vec![95, 87, 92];
    let paired: Vec<_> = names.iter().zip(scores.iter()).collect();
    println!("Paired: {:?}", paired);

    // fold - accumulate a value
    let sum = numbers.iter().fold(0, |acc, x| acc + x);
    println!("Sum (fold): {}", sum);

    let product = numbers.iter().fold(1, |acc, x| acc * x);
    println!("Product (fold): {}", product);

    // sum and product (shortcuts)
    let sum: i32 = numbers.iter().sum();
    let product: i32 = numbers.iter().product();
    println!("Sum: {}, Product: {}", sum, product);

    // any and all
    let has_even = numbers.iter().any(|&x| x % 2 == 0);
    let all_positive = numbers.iter().all(|&x| x > 0);
    println!("Has even: {}, All positive: {}", has_even, all_positive);

    // find - first matching element
    let first_even = numbers.iter().find(|&&x| x % 2 == 0);
    println!("First even: {:?}", first_even);

    // position - index of first match
    let position = numbers.iter().position(|&x| x > 5);
    println!("Position of first > 5: {:?}", position);

    // max and min
    let max = numbers.iter().max();
    let min = numbers.iter().min();
    println!("Max: {:?}, Min: {:?}", max, min);

    // chain - concatenate iterators
    let v1 = vec![1, 2, 3];
    let v2 = vec![4, 5, 6];
    let chained: Vec<_> = v1.iter().chain(v2.iter()).collect();
    println!("Chained: {:?}", chained);

    // flat_map - map and flatten
    let nested = vec![vec![1, 2], vec![3, 4], vec![5, 6]];
    let flattened: Vec<_> = nested.iter().flat_map(|v| v.iter()).collect();
    println!("Flattened: {:?}", flattened);

    println!();
}

/// Demonstrates closures
fn closures_demo() {
    println!("🎭 Closures");
    println!("-----------");

    // Basic closure
    let add_one = |x| x + 1;
    println!("5 + 1 = {}", add_one(5));

    // Multiple parameters
    let add = |x, y| x + y;
    println!("3 + 4 = {}", add(3, 4));

    // Type annotations (optional but explicit)
    let multiply = |x: i32, y: i32| -> i32 { x * y };
    println!("3 × 4 = {}", multiply(3, 4));

    // Capturing environment
    let multiplier = 2;
    let times_two = |x| x * multiplier;
    println!("5 × {} = {}", multiplier, times_two(5));

    // Mutable capture
    let mut count = 0;
    let mut increment = || {
        count += 1;
        count
    };
    println!("Count: {}", increment());
    println!("Count: {}", increment());
    println!("Count: {}", increment());

    // move keyword - takes ownership
    let text = String::from("hello");
    let printer = move || println!("Text: {}", text);
    printer();
    // println!("{}", text);  // Error: text was moved

    // Using closures with iterators
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<_> = numbers.iter().map(|x| x * 2).collect();
    println!("Doubled with closure: {:?}", doubled);

    // Closure as parameter
    fn apply<F>(value: i32, f: F) -> i32
    where
        F: Fn(i32) -> i32,
    {
        f(value)
    }

    let result = apply(10, |x| x * x);
    println!("Apply square to 10: {}", result);

    println!();
}

/// Demonstrates data processing pipelines
fn data_pipelines() {
    println!("⚙️  Data Processing Pipelines");
    println!("-----------------------------");

    // Pipeline 1: Filter, map, sum
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let result: i32 = numbers.iter()
        .filter(|&&x| x % 2 == 0)      // Keep evens
        .map(|&x| x * x)                // Square them
        .sum();                         // Sum them up
    println!("Sum of even squares: {}", result);

    // Pipeline 2: Complex transformation
    let words = vec!["hello", "world", "rust", "is", "awesome"];
    let result: Vec<_> = words.iter()
        .filter(|s| s.len() > 2)              // Words longer than 2
        .map(|s| s.to_uppercase())            // Uppercase
        .map(|s| format!("{}!", s))           // Add exclamation
        .collect();
    println!("Transformed: {:?}", result);

    // Pipeline 3: Grouping data
    let items = vec![
        ("apple", 5),
        ("banana", 3),
        ("apple", 2),
        ("orange", 4),
        ("banana", 1),
    ];

    let grouped = items.iter()
        .fold(HashMap::new(), |mut acc, (name, count)| {
            *acc.entry(name).or_insert(0) += count;
            acc
        });
    println!("Grouped: {:?}", grouped);

    // Pipeline 4: Find and transform
    let result = vec![10, 20, 30, 40, 50]
        .iter()
        .find(|&&x| x > 25)
        .map(|&x| x * 2);
    println!("First > 25, doubled: {:?}", result);

    println!();
}

/// Real-world examples
fn real_world_examples() {
    println!("🌍 Real-World Examples");
    println!("----------------------");

    // Example 1: Word frequency counter
    println!("Word Frequency Counter:");
    let text = "the quick brown fox jumps over the lazy dog the fox";
    let word_freq = count_words(text);
    for (word, count) in &word_freq {
        println!("  '{}': {}", word, count);
    }

    // Example 2: Data filtering and statistics
    println!("\nStudent Grades:");
    let grades = vec![85, 92, 78, 95, 88, 73, 91, 87];
    let stats = calculate_statistics(&grades);
    println!("  Average: {:.2}", stats.0);
    println!("  Passing (≥80): {:?}", stats.1);

    // Example 3: Deduplication
    println!("\nDeduplication:");
    let numbers = vec![1, 2, 3, 2, 4, 1, 5, 3];
    let unique = deduplicate(numbers);
    println!("  Unique: {:?}", unique);

    // Example 4: Top N items
    println!("\nTop 3 scores:");
    let scores = vec![85, 92, 78, 95, 88, 73, 91, 87];
    let top_three = top_n(&scores, 3);
    println!("  {:?}", top_three);

    // Example 5: Data transformation
    println!("\nData Transformation:");
    let data = vec![
        ("Alice", 25),
        ("Bob", 30),
        ("Charlie", 35),
        ("Diana", 28),
    ];
    let transformed = transform_data(data);
    println!("  {:?}", transformed);

    println!();
}

// Helper functions

/// Counts word frequency
fn count_words(text: &str) -> HashMap<&str, usize> {
    text.split_whitespace()
        .fold(HashMap::new(), |mut acc, word| {
            *acc.entry(word).or_insert(0) += 1;
            acc
        })
}

/// Calculates average and filters passing grades
fn calculate_statistics(grades: &[i32]) -> (f64, Vec<i32>) {
    let average = grades.iter().sum::<i32>() as f64 / grades.len() as f64;
    let passing = grades.iter()
        .filter(|&&g| g >= 80)
        .copied()
        .collect();
    (average, passing)
}

/// Removes duplicates while preserving order
fn deduplicate<T: Eq + std::hash::Hash + Clone>(items: Vec<T>) -> Vec<T> {
    let mut seen = HashSet::new();
    items.into_iter()
        .filter(|item| seen.insert(item.clone()))
        .collect()
}

/// Returns top N items
fn top_n<T: Ord + Clone>(items: &[T], n: usize) -> Vec<T> {
    let mut sorted = items.to_vec();
    sorted.sort_by(|a, b| b.cmp(a));  // Descending
    sorted.into_iter().take(n).collect()
}

/// Transforms data into HashMap
fn transform_data(data: Vec<(&str, i32)>) -> HashMap<String, i32> {
    data.into_iter()
        .map(|(name, age)| (name.to_uppercase(), age + 1))
        .collect()
}

// Exercise Solutions (uncomment to test)

/*
/// Exercise 1: Remove duplicates preserving order
fn remove_duplicates<T: Eq + std::hash::Hash + Clone>(vec: Vec<T>) -> Vec<T> {
    let mut seen = HashSet::new();
    vec.into_iter()
        .filter(|item| seen.insert(item.clone()))
        .collect()
}

/// Exercise 1: Rotate left
fn rotate_left<T>(mut vec: Vec<T>, n: usize) -> Vec<T> {
    if vec.is_empty() || n == 0 {
        return vec;
    }
    let n = n % vec.len();
    vec.rotate_left(n);
    vec
}

/// Exercise 1: Partition
fn partition<T, F>(vec: Vec<T>, predicate: F) -> (Vec<T>, Vec<T>)
where
    F: Fn(&T) -> bool,
{
    let mut true_vec = Vec::new();
    let mut false_vec = Vec::new();

    for item in vec {
        if predicate(&item) {
            true_vec.push(item);
        } else {
            false_vec.push(item);
        }
    }

    (true_vec, false_vec)
}

/// Exercise 2: Word frequency with top N
fn top_words(text: &str, n: usize) -> Vec<(&str, usize)> {
    let mut freq: HashMap<&str, usize> = HashMap::new();

    for word in text.split_whitespace() {
        *freq.entry(word).or_insert(0) += 1;
    }

    let mut items: Vec<_> = freq.into_iter().collect();
    items.sort_by(|a, b| b.1.cmp(&a.1));
    items.into_iter().take(n).collect()
}

/// Exercise 3: Data pipeline
fn process_numbers(numbers: Vec<i32>) -> i32 {
    numbers.into_iter()
        .filter(|&x| x >= 10)
        .map(|x| x * x)
        .take(5)
        .sum()
}

/// Exercise 4: Fibonacci iterator
struct Fibonacci {
    curr: u32,
    next: u32,
}

impl Fibonacci {
    fn new() -> Self {
        Fibonacci { curr: 0, next: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        let current = self.curr;
        self.curr = self.next;
        self.next = current + self.next;
        Some(current)
    }
}

/// Exercise 5: map_vec with closure
fn map_vec<F>(vec: Vec<i32>, f: F) -> Vec<i32>
where
    F: Fn(i32) -> i32,
{
    vec.into_iter().map(f).collect()
}
*/
