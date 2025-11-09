// Project 06: Traits & Generics
// Comprehensive examples of traits, generics, and polymorphism

use std::fmt::{Display, Debug};

fn main() {
    println!("🦀 Traits & Generics in Rust");
    println!("============================\n");

    // Run all example functions
    basic_traits();
    trait_implementations();
    default_implementations();
    generic_functions();
    generic_structs();
    trait_bounds_examples();
    associated_types_demo();
    static_vs_dynamic_dispatch();
    marker_traits_demo();
    real_world_examples();
}

// ============================================================================
// 1. BASIC TRAITS
// ============================================================================

/// Trait defining shared behavior
trait Summary {
    fn summarize(&self) -> String;
}

/// NewsArticle type
struct NewsArticle {
    headline: String,
    location: String,
    author: String,
    content: String,
}

/// Tweet type
struct Tweet {
    username: String,
    content: String,
    reply: bool,
    retweet: bool,
}

/// Implementing Summary for NewsArticle
impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

/// Implementing Summary for Tweet
impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

fn basic_traits() {
    println!("📚 Basic Traits");
    println!("----------------");

    let article = NewsArticle {
        headline: String::from("Rust 2.0 Released!"),
        location: String::from("San Francisco"),
        author: String::from("Jane Doe"),
        content: String::from("Rust continues to evolve..."),
    };

    let tweet = Tweet {
        username: String::from("rustlang"),
        content: String::from("Announcing new features!"),
        reply: false,
        retweet: false,
    };

    println!("Article: {}", article.summarize());
    println!("Tweet: {}", tweet.summarize());
    println!();
}

// ============================================================================
// 2. TRAITS WITH MULTIPLE METHODS
// ============================================================================

trait Drawable {
    fn draw(&self);
    fn color(&self) -> &str;
}

struct Circle {
    radius: f64,
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl Drawable for Circle {
    fn draw(&self) {
        println!("Drawing a circle with radius {}", self.radius);
    }

    fn color(&self) -> &str {
        "red"
    }
}

impl Drawable for Rectangle {
    fn draw(&self) {
        println!("Drawing a rectangle {}x{}", self.width, self.height);
    }

    fn color(&self) -> &str {
        "blue"
    }
}

fn trait_implementations() {
    println!("🎨 Trait Implementations");
    println!("-------------------------");

    let circle = Circle { radius: 5.0 };
    let rectangle = Rectangle { width: 10.0, height: 20.0 };

    circle.draw();
    println!("Circle color: {}", circle.color());

    rectangle.draw();
    println!("Rectangle color: {}", rectangle.color());
    println!();
}

// ============================================================================
// 3. DEFAULT IMPLEMENTATIONS
// ============================================================================

trait Describable {
    fn name(&self) -> String;

    // Default implementation
    fn describe(&self) -> String {
        format!("This is a {}", self.name())
    }

    // Default implementation calling another method
    fn full_description(&self) -> String {
        format!("Full description: {}", self.describe())
    }
}

struct Book {
    title: String,
    author: String,
}

impl Describable for Book {
    fn name(&self) -> String {
        self.title.clone()
    }

    // Override default implementation
    fn describe(&self) -> String {
        format!("'{}' by {}", self.title, self.author)
    }
}

struct Movie {
    title: String,
}

impl Describable for Movie {
    fn name(&self) -> String {
        self.title.clone()
    }
    // Uses default describe() implementation
}

fn default_implementations() {
    println!("📖 Default Implementations");
    println!("--------------------------");

    let book = Book {
        title: String::from("The Rust Programming Language"),
        author: String::from("Steve Klabnik"),
    };

    let movie = Movie {
        title: String::from("Rust: The Movie"),
    };

    println!("Book: {}", book.describe());
    println!("Book full: {}", book.full_description());
    println!("Movie: {}", movie.describe());
    println!("Movie full: {}", movie.full_description());
    println!();
}

// ============================================================================
// 4. GENERIC FUNCTIONS
// ============================================================================

/// Generic function with trait bound
fn print_summary<T: Summary>(item: &T) {
    println!("Summary: {}", item.summarize());
}

/// Generic function with multiple trait bounds
fn print_and_debug<T: Display + Debug>(item: &T) {
    println!("Display: {}", item);
    println!("Debug: {:?}", item);
}

/// Generic function returning largest element
fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];

    for &item in list.iter() {
        if item > largest {
            largest = item;
        }
    }

    largest
}

fn generic_functions() {
    println!("🔧 Generic Functions");
    println!("--------------------");

    let article = NewsArticle {
        headline: String::from("Generic Power"),
        location: String::from("Internet"),
        author: String::from("Ferris"),
        content: String::from("Generics are awesome!"),
    };

    print_summary(&article);

    let numbers = vec![34, 50, 25, 100, 65];
    let largest_num = largest(&numbers);
    println!("Largest number: {}", largest_num);

    let chars = vec!['y', 'm', 'a', 'q'];
    let largest_char = largest(&chars);
    println!("Largest char: {}", largest_char);

    println!();
}

// ============================================================================
// 5. GENERIC STRUCTS
// ============================================================================

/// Single generic type parameter
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn new(x: T, y: T) -> Self {
        Point { x, y }
    }

    fn x(&self) -> &T {
        &self.x
    }

    fn y(&self) -> &T {
        &self.y
    }
}

// Specific implementation for f64
impl Point<f64> {
    fn distance_from_origin(&self) -> f64 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

/// Multiple generic type parameters
struct Pair<T, U> {
    first: T,
    second: U,
}

impl<T, U> Pair<T, U> {
    fn new(first: T, second: U) -> Self {
        Pair { first, second }
    }

    fn swap(self) -> Pair<U, T> {
        Pair {
            first: self.second,
            second: self.first,
        }
    }
}

fn generic_structs() {
    println!("📦 Generic Structs");
    println!("------------------");

    let integer_point = Point::new(5, 10);
    println!("Integer point: ({}, {})", integer_point.x(), integer_point.y());

    let float_point = Point::new(3.0, 4.0);
    println!("Float point: ({}, {})", float_point.x(), float_point.y());
    println!("Distance from origin: {:.2}", float_point.distance_from_origin());

    let pair = Pair::new("hello", 42);
    println!("Pair: ({}, {})", pair.first, pair.second);

    let swapped = pair.swap();
    println!("Swapped: ({}, {})", swapped.first, swapped.second);

    println!();
}

// ============================================================================
// 6. TRAIT BOUNDS WITH WHERE CLAUSES
// ============================================================================

/// Function with inline trait bounds
fn print_inline<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) {
    println!("T (Display): {}", t);
    println!("U (Debug): {:?}", u);
}

/// Same function with where clause (cleaner)
fn print_where<T, U>(t: &T, u: &U)
where
    T: Display + Clone,
    U: Clone + Debug,
{
    println!("T (Display): {}", t);
    println!("U (Debug): {:?}", u);
}

/// Conditional implementation based on trait bounds
impl<T: Display> Point<T> {
    fn display(&self) {
        println!("Point: ({}, {})", self.x, self.y);
    }
}

fn trait_bounds_examples() {
    println!("🎯 Trait Bounds & Where Clauses");
    println!("--------------------------------");

    let text = String::from("Hello");
    let number = 42;

    print_inline(&text, &number);
    print_where(&text, &number);

    let point = Point::new(5, 10);
    point.display();

    println!();
}

// ============================================================================
// 7. ASSOCIATED TYPES
// ============================================================================

trait Container {
    type Item;

    fn get(&self, index: usize) -> Option<&Self::Item>;
    fn len(&self) -> usize;
    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

struct MyVec<T> {
    data: Vec<T>,
}

impl<T> Container for MyVec<T> {
    type Item = T;

    fn get(&self, index: usize) -> Option<&Self::Item> {
        self.data.get(index)
    }

    fn len(&self) -> usize {
        self.data.len()
    }
}

/// Custom iterator with associated type
struct Counter {
    count: u32,
    max: u32,
}

impl Counter {
    fn new(max: u32) -> Counter {
        Counter { count: 0, max }
    }
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.count < self.max {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}

fn associated_types_demo() {
    println!("🔗 Associated Types");
    println!("-------------------");

    let my_vec = MyVec {
        data: vec![1, 2, 3, 4, 5],
    };

    println!("Container length: {}", my_vec.len());
    if let Some(item) = my_vec.get(2) {
        println!("Item at index 2: {}", item);
    }

    let counter = Counter::new(5);
    print!("Counter: ");
    for num in counter {
        print!("{} ", num);
    }
    println!("\n");
}

// ============================================================================
// 8. STATIC VS DYNAMIC DISPATCH
// ============================================================================

/// Static dispatch using impl Trait
fn notify_static(item: &impl Summary) {
    println!("[Static] {}", item.summarize());
}

/// Dynamic dispatch using dyn Trait
fn notify_dynamic(item: &dyn Summary) {
    println!("[Dynamic] {}", item.summarize());
}

/// Returns impl Trait (static dispatch)
fn returns_summary_static() -> impl Summary {
    Tweet {
        username: String::from("rustlang"),
        content: String::from("Static dispatch example"),
        reply: false,
        retweet: false,
    }
}

/// Returns Box<dyn Trait> (dynamic dispatch)
fn returns_summary_dynamic(is_tweet: bool) -> Box<dyn Summary> {
    if is_tweet {
        Box::new(Tweet {
            username: String::from("user"),
            content: String::from("Dynamic dispatch"),
            reply: false,
            retweet: false,
        })
    } else {
        Box::new(NewsArticle {
            headline: String::from("News"),
            location: String::from("Here"),
            author: String::from("Author"),
            content: String::from("Content"),
        })
    }
}

fn static_vs_dynamic_dispatch() {
    println!("⚡ Static vs Dynamic Dispatch");
    println!("-----------------------------");

    let tweet = Tweet {
        username: String::from("ferris"),
        content: String::from("Hello Rust!"),
        reply: false,
        retweet: false,
    };

    notify_static(&tweet);
    notify_dynamic(&tweet);

    let static_item = returns_summary_static();
    println!("Static return: {}", static_item.summarize());

    let dynamic_item = returns_summary_dynamic(true);
    println!("Dynamic return: {}", dynamic_item.summarize());

    // Collection of different types using trait objects
    let items: Vec<Box<dyn Summary>> = vec![
        Box::new(Tweet {
            username: String::from("alice"),
            content: String::from("First tweet"),
            reply: false,
            retweet: false,
        }),
        Box::new(NewsArticle {
            headline: String::from("Breaking News"),
            location: String::from("City"),
            author: String::from("Bob"),
            content: String::from("Something happened"),
        }),
    ];

    println!("\nCollection of trait objects:");
    for item in items.iter() {
        println!("  - {}", item.summarize());
    }

    println!();
}

// ============================================================================
// 9. MARKER TRAITS
// ============================================================================

/// Custom type implementing Copy
#[derive(Debug, Copy, Clone)]
struct SmallData {
    value: i32,
}

/// Type that cannot implement Copy (has String)
#[derive(Debug, Clone)]
struct LargeData {
    name: String,
    value: i32,
}

fn takes_ownership<T>(data: T) {
    println!("Took ownership of data");
}

fn marker_traits_demo() {
    println!("🏷️  Marker Traits (Copy, Clone, Send, Sync)");
    println!("--------------------------------------------");

    // Copy trait - value is copied
    let small = SmallData { value: 42 };
    takes_ownership(small);
    println!("Can still use small: {:?}", small);  // Still valid!

    // No Copy trait - value is moved
    let large = LargeData {
        name: String::from("test"),
        value: 100,
    };
    let large_clone = large.clone();  // Explicit clone
    takes_ownership(large);
    // println!("{:?}", large);  // ERROR: value moved
    println!("Used clone: {:?}", large_clone);

    // Send and Sync are automatically implemented for most types
    fn is_send<T: Send>(_: &T) {
        println!("Type is Send (can be transferred between threads)");
    }

    fn is_sync<T: Sync>(_: &T) {
        println!("Type is Sync (can be referenced from multiple threads)");
    }

    is_send(&small);
    is_sync(&small);

    println!();
}

// ============================================================================
// 10. REAL-WORLD EXAMPLES
// ============================================================================

/// Generic Result wrapper
#[derive(Debug)]
enum MyResult<T, E> {
    Ok(T),
    Err(E),
}

impl<T, E> MyResult<T, E> {
    fn is_ok(&self) -> bool {
        matches!(self, MyResult::Ok(_))
    }

    fn is_err(&self) -> bool {
        matches!(self, MyResult::Err(_))
    }
}

/// Trait for types that can be validated
trait Validate {
    type Error;

    fn validate(&self) -> Result<(), Self::Error>;
}

struct Email {
    address: String,
}

#[derive(Debug)]
struct EmailError {
    message: String,
}

impl Validate for Email {
    type Error = EmailError;

    fn validate(&self) -> Result<(), Self::Error> {
        if self.address.contains('@') {
            Ok(())
        } else {
            Err(EmailError {
                message: String::from("Email must contain @"),
            })
        }
    }
}

/// Generic cache implementation
struct Cache<K, V>
where
    K: Eq + std::hash::Hash,
{
    data: std::collections::HashMap<K, V>,
}

impl<K, V> Cache<K, V>
where
    K: Eq + std::hash::Hash,
{
    fn new() -> Self {
        Cache {
            data: std::collections::HashMap::new(),
        }
    }

    fn insert(&mut self, key: K, value: V) {
        self.data.insert(key, value);
    }

    fn get(&self, key: &K) -> Option<&V> {
        self.data.get(key)
    }
}

fn real_world_examples() {
    println!("🌍 Real-World Examples");
    println!("----------------------");

    // Custom Result type
    let success: MyResult<i32, String> = MyResult::Ok(42);
    let failure: MyResult<i32, String> = MyResult::Err(String::from("error"));

    println!("Success is ok: {}", success.is_ok());
    println!("Failure is err: {}", failure.is_err());

    // Validation trait
    let valid_email = Email {
        address: String::from("user@example.com"),
    };
    let invalid_email = Email {
        address: String::from("not-an-email"),
    };

    match valid_email.validate() {
        Ok(_) => println!("Valid email!"),
        Err(e) => println!("Invalid: {:?}", e),
    }

    match invalid_email.validate() {
        Ok(_) => println!("Valid email!"),
        Err(e) => println!("Invalid: {:?}", e),
    }

    // Generic cache
    let mut cache = Cache::new();
    cache.insert("name", "Ferris");
    cache.insert("language", "Rust");

    if let Some(name) = cache.get(&"name") {
        println!("Cached name: {}", name);
    }

    println!();
}

// ============================================================================
// EXERCISE SOLUTIONS (Commented out)
// ============================================================================

/*
/// Exercise 1: Shape trait with area calculation
trait Shape {
    fn area(&self) -> f64;
    fn perimeter(&self) -> f64;
}

struct Circle {
    radius: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }

    fn perimeter(&self) -> f64 {
        2.0 * std::f64::consts::PI * self.radius
    }
}

/// Exercise 2: Generic Stack
struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    fn new() -> Self {
        Stack { items: Vec::new() }
    }

    fn push(&mut self, item: T) {
        self.items.push(item);
    }

    fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }

    fn peek(&self) -> Option<&T> {
        self.items.last()
    }

    fn is_empty(&self) -> bool {
        self.items.is_empty()
    }

    fn len(&self) -> usize {
        self.items.len()
    }
}

/// Exercise 3: Custom From/Into implementations
struct Celsius(f64);
struct Fahrenheit(f64);

impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Self {
        Fahrenheit(c.0 * 9.0 / 5.0 + 32.0)
    }
}

impl From<Fahrenheit> for Celsius {
    fn from(f: Fahrenheit) -> Self {
        Celsius((f.0 - 32.0) * 5.0 / 9.0)
    }
}
*/
