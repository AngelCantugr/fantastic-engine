// Project 03: Error Handling & CLI Tool
// Comprehensive examples of error handling in Rust

use std::fs;
use std::io;
use std::num::ParseIntError;
use std::fmt;

fn main() {
    println!("🦀 Error Handling in Rust");
    println!("=========================\n");

    option_basics();
    result_basics();
    question_mark_operator();
    combinators_demo();
    custom_errors_demo();
    panic_vs_result();
    real_world_example();
    cli_tool_example();
}

/// Demonstrates Option<T> basics
fn option_basics() {
    println!("❓ Option<T> Basics");
    println!("-------------------");

    // Creating Options
    let some_number: Option<i32> = Some(5);
    let no_number: Option<i32> = None;

    println!("some_number: {:?}", some_number);
    println!("no_number: {:?}", no_number);

    // Pattern matching
    match some_number {
        Some(n) => println!("Got a number: {}", n),
        None => println!("No number"),
    }

    // if let (syntactic sugar)
    if let Some(n) = some_number {
        println!("if let found: {}", n);
    }

    // Unwrap (dangerous - will panic if None)
    let value = some_number.unwrap();
    println!("Unwrapped: {}", value);

    // unwrap_or: Provide default value
    let value_or_default = no_number.unwrap_or(0);
    println!("With default: {}", value_or_default);

    // unwrap_or_else: Compute default lazily
    let value_or_computed = no_number.unwrap_or_else(|| {
        println!("  Computing default...");
        42
    });
    println!("With computed default: {}", value_or_computed);

    // Common Option use case: accessing collections
    let numbers = vec![1, 2, 3, 4, 5];
    let first = numbers.get(0);      // Some(&1)
    let tenth = numbers.get(10);     // None

    println!("First element: {:?}", first);
    println!("Tenth element: {:?}", tenth);

    // Option in function returns
    let found = find_even(&[1, 3, 4, 7, 9]);
    match found {
        Some(n) => println!("Found even number: {}", n),
        None => println!("No even number found"),
    }

    println!();
}

/// Demonstrates Result<T, E> basics
fn result_basics() {
    println!("✅ Result<T, E> Basics");
    println!("----------------------");

    // Creating Results
    let success: Result<i32, String> = Ok(42);
    let failure: Result<i32, String> = Err("something went wrong".to_string());

    println!("success: {:?}", success);
    println!("failure: {:?}", failure);

    // Pattern matching
    match divide(10, 2) {
        Ok(result) => println!("10 / 2 = {}", result),
        Err(e) => println!("Error: {}", e),
    }

    match divide(10, 0) {
        Ok(result) => println!("10 / 0 = {}", result),
        Err(e) => println!("Error: {}", e),
    }

    // unwrap and expect (will panic on Err)
    let value = divide(20, 4).unwrap();
    println!("20 / 4 = {}", value);

    // expect with custom message
    let value = divide(15, 3).expect("Division should work");
    println!("15 / 3 = {}", value);

    // unwrap_or: Provide default on error
    let value = divide(10, 0).unwrap_or(0);
    println!("10 / 0 with default: {}", value);

    // is_ok() and is_err()
    let result = divide(8, 2);
    if result.is_ok() {
        println!("Division succeeded!");
    }

    let result = divide(8, 0);
    if result.is_err() {
        println!("Division failed!");
    }

    println!();
}

/// Demonstrates the ? operator for error propagation
fn question_mark_operator() {
    println!("❓ The ? Operator");
    println!("-----------------");

    // Without ? operator (verbose)
    match divide_and_add_verbose(20, 4, 5) {
        Ok(result) => println!("Verbose result: {}", result),
        Err(e) => println!("Verbose error: {}", e),
    }

    // With ? operator (concise)
    match divide_and_add(20, 4, 5) {
        Ok(result) => println!("Concise result: {}", result),
        Err(e) => println!("Concise error: {}", e),
    }

    // Error propagation
    match divide_and_add(20, 0, 5) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => println!("Propagated error: {}", e),
    }

    // ? with Option
    match first_and_second(&[1, 2, 3]) {
        Some((a, b)) => println!("First two: {} and {}", a, b),
        None => println!("Not enough elements"),
    }

    match first_and_second(&[1]) {
        Some((a, b)) => println!("First two: {} and {}", a, b),
        None => println!("Not enough elements"),
    }

    println!();
}

/// Demonstrates combinators (map, and_then, etc.)
fn combinators_demo() {
    println!("🔗 Combinators");
    println!("--------------");

    // map: Transform the value inside Option/Result
    let number = Some(5);
    let doubled = number.map(|n| n * 2);
    println!("Mapped: {:?}", doubled);

    let result: Result<i32, String> = Ok(10);
    let squared = result.map(|n| n * n);
    println!("Squared: {:?}", squared);

    // and_then: Chain operations that return Option/Result
    let result = Some("42")
        .and_then(|s| s.parse::<i32>().ok())
        .map(|n| n * 2);
    println!("Parsed and doubled: {:?}", result);

    // or_else: Provide alternative on None/Err
    let no_value: Option<i32> = None;
    let with_alternative = no_value.or_else(|| Some(100));
    println!("With alternative: {:?}", with_alternative);

    // ok_or: Convert Option to Result
    let opt = Some(42);
    let res: Result<i32, &str> = opt.ok_or("No value found");
    println!("Option to Result: {:?}", res);

    // Chaining multiple operations
    let result = parse_and_process("  123  ");
    match result {
        Ok(n) => println!("Chained result: {}", n),
        Err(e) => println!("Chained error: {}", e),
    }

    println!();
}

/// Demonstrates custom error types
fn custom_errors_demo() {
    println!("🎨 Custom Error Types");
    println!("---------------------");

    // Using custom error type
    match validate_age("25") {
        Ok(age) => println!("Valid age: {}", age),
        Err(e) => println!("Error: {}", e),
    }

    match validate_age("abc") {
        Ok(age) => println!("Valid age: {}", age),
        Err(e) => println!("Error: {}", e),
    }

    match validate_age("150") {
        Ok(age) => println!("Valid age: {}", age),
        Err(e) => println!("Error: {}", e),
    }

    match validate_age("-5") {
        Ok(age) => println!("Valid age: {}", age),
        Err(e) => println!("Error: {}", e),
    }

    println!();
}

/// Demonstrates when to use panic! vs Result
fn panic_vs_result() {
    println!("💥 panic! vs Result");
    println!("-------------------");

    // Use Result for expected errors
    match read_file_safe("nonexistent.txt") {
        Ok(content) => println!("File content: {}", content),
        Err(e) => println!("Expected error (Result): {}", e),
    }

    // panic! would be used for programmer errors (bugs)
    // Uncomment to see panic in action:
    // let items = vec![1, 2, 3];
    // let value = items[10];  // This would panic!

    // Safe alternative using get()
    let items = vec![1, 2, 3];
    match items.get(10) {
        Some(value) => println!("Value: {}", value),
        None => println!("Index out of bounds (safe)"),
    }

    println!();
}

/// Real-world example: Processing a file
fn real_world_example() {
    println!("🌍 Real-World Example");
    println!("---------------------");

    // Create a test file
    let test_data = "10\n20\n30\nabc\n40\n";
    fs::write("/tmp/numbers.txt", test_data).ok();

    match process_number_file("/tmp/numbers.txt") {
        Ok(sum) => println!("Sum of numbers: {}", sum),
        Err(e) => println!("Processing error: {}", e),
    }

    // Clean up
    fs::remove_file("/tmp/numbers.txt").ok();

    println!();
}

/// Demonstrates CLI tool pattern
fn cli_tool_example() {
    println!("🖥️  CLI Tool Pattern");
    println!("-------------------");

    // Simulate CLI arguments
    let args = vec![
        "program".to_string(),
        "add".to_string(),
        "10".to_string(),
        "20".to_string(),
    ];

    match run_calculator(&args) {
        Ok(result) => println!("Calculator result: {}", result),
        Err(e) => eprintln!("Calculator error: {}", e),
    }

    // Try with invalid operation
    let args = vec![
        "program".to_string(),
        "invalid".to_string(),
        "10".to_string(),
        "20".to_string(),
    ];

    match run_calculator(&args) {
        Ok(result) => println!("Calculator result: {}", result),
        Err(e) => eprintln!("Calculator error: {}", e),
    }

    println!();
}

// Helper functions

/// Divides two numbers, returns Result
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

/// Finds first even number in slice
fn find_even(numbers: &[i32]) -> Option<i32> {
    for &num in numbers {
        if num % 2 == 0 {
            return Some(num);
        }
    }
    None
}

/// Divide and add without ? operator (verbose)
fn divide_and_add_verbose(a: i32, b: i32, c: i32) -> Result<i32, String> {
    match divide(a, b) {
        Ok(result) => Ok(result + c),
        Err(e) => Err(e),
    }
}

/// Divide and add with ? operator (concise)
fn divide_and_add(a: i32, b: i32, c: i32) -> Result<i32, String> {
    let result = divide(a, b)?;  // Propagates error automatically
    Ok(result + c)
}

/// Gets first two elements using ? with Option
fn first_and_second(numbers: &[i32]) -> Option<(i32, i32)> {
    let first = numbers.get(0)?;   // Returns None if not found
    let second = numbers.get(1)?;  // Returns None if not found
    Some((*first, *second))
}

/// Parses and processes a string using combinators
fn parse_and_process(input: &str) -> Result<i32, String> {
    input
        .trim()
        .parse::<i32>()
        .map(|n| n * 2)
        .map_err(|e| format!("Parse error: {}", e))
}

/// Custom error type
#[derive(Debug)]
enum AgeError {
    ParseError(ParseIntError),
    TooYoung,
    TooOld,
    Negative,
}

impl fmt::Display for AgeError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            AgeError::ParseError(e) => write!(f, "Failed to parse age: {}", e),
            AgeError::TooYoung => write!(f, "Age must be at least 18"),
            AgeError::TooOld => write!(f, "Age must be less than 120"),
            AgeError::Negative => write!(f, "Age cannot be negative"),
        }
    }
}

impl std::error::Error for AgeError {}

// Convert ParseIntError to AgeError
impl From<ParseIntError> for AgeError {
    fn from(err: ParseIntError) -> Self {
        AgeError::ParseError(err)
    }
}

/// Validates age with custom error type
fn validate_age(input: &str) -> Result<u32, AgeError> {
    let age: i32 = input.parse()?;  // ? converts ParseIntError to AgeError

    if age < 0 {
        return Err(AgeError::Negative);
    }
    if age < 18 {
        return Err(AgeError::TooYoung);
    }
    if age > 120 {
        return Err(AgeError::TooOld);
    }

    Ok(age as u32)
}

/// Safe file reading with Result
fn read_file_safe(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)
}

/// Processes a file of numbers, returns sum
fn process_number_file(path: &str) -> Result<i32, String> {
    let content = fs::read_to_string(path)
        .map_err(|e| format!("Failed to read file: {}", e))?;

    let mut sum = 0;
    let mut valid_count = 0;

    for (line_num, line) in content.lines().enumerate() {
        match line.trim().parse::<i32>() {
            Ok(num) => {
                sum += num;
                valid_count += 1;
            }
            Err(_) => {
                println!("  Warning: Skipping invalid number on line {}: '{}'",
                        line_num + 1, line);
            }
        }
    }

    if valid_count == 0 {
        return Err("No valid numbers found in file".to_string());
    }

    Ok(sum)
}

/// Simple calculator CLI
fn run_calculator(args: &[String]) -> Result<i32, String> {
    if args.len() != 4 {
        return Err(format!("Usage: {} <operation> <num1> <num2>", args[0]));
    }

    let operation = &args[1];
    let num1: i32 = args[2].parse()
        .map_err(|_| format!("Invalid number: {}", args[2]))?;
    let num2: i32 = args[3].parse()
        .map_err(|_| format!("Invalid number: {}", args[3]))?;

    match operation.as_str() {
        "add" => Ok(num1 + num2),
        "sub" => Ok(num1 - num2),
        "mul" => Ok(num1 * num2),
        "div" => {
            if num2 == 0 {
                Err("Cannot divide by zero".to_string())
            } else {
                Ok(num1 / num2)
            }
        }
        _ => Err(format!("Unknown operation: {}", operation)),
    }
}

// Exercise Solutions (uncomment to test)

/*
/// Exercise 1: Safe division
fn safe_divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}

/// Exercise 2: Parse and validate
fn parse_and_validate(input: &str) -> Result<i32, String> {
    let num: i32 = input.parse()
        .map_err(|_| "Invalid number format".to_string())?;

    if num < 1 || num > 100 {
        return Err("Number must be between 1 and 100".to_string());
    }

    Ok(num)
}

/// Exercise 3: File line counter (would be in main)
fn count_lines(filename: &str) -> Result<usize, String> {
    let content = std::fs::read_to_string(filename)
        .map_err(|e| format!("Failed to read file '{}': {}", filename, e))?;

    Ok(content.lines().count())
}

/// Exercise 4: Custom validation error
#[derive(Debug)]
enum ValidationError {
    InvalidEmail,
    TooShort,
    TooLong,
}

impl fmt::Display for ValidationError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ValidationError::InvalidEmail => write!(f, "Email format is invalid"),
            ValidationError::TooShort => write!(f, "Username is too short"),
            ValidationError::TooLong => write!(f, "Username is too long"),
        }
    }
}

impl std::error::Error for ValidationError {}

/// Exercise 5: Option combinators chain
fn process_optional_string(input: Option<String>) -> String {
    input
        .map(|s| s.to_uppercase())
        .map(|s| s.chars().take(5).collect())
        .unwrap_or_else(|| "DEFAULT".to_string())
}
*/
