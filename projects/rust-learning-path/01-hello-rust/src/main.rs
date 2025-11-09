// Project 01: Hello Rust - Variables & Types
// Comprehensive examples of Rust fundamentals

fn main() {
    println!("🦀 Welcome to Rust!");
    println!("==================\n");

    // Run all example functions
    variables_and_mutability();
    integer_types();
    floating_point();
    boolean_and_char();
    tuples();
    arrays();
    string_types();
    functions_demo();
    control_flow();
}

/// Demonstrates variables, mutability, and shadowing
fn variables_and_mutability() {
    println!("📦 Variables and Mutability");
    println!("---------------------------");

    // Immutable variable (default)
    let x = 5;
    println!("Immutable x: {}", x);

    // This would cause a compiler error:
    // x = 6;

    // Mutable variable
    let mut y = 5;
    println!("Mutable y before: {}", y);
    y = 6;
    println!("Mutable y after: {}", y);

    // Shadowing - creates a new variable
    let z = 5;
    let z = z + 1;  // New variable, same name
    let z = z * 2;  // Another new variable
    println!("Shadowed z: {}", z);

    // Shadowing can change type
    let spaces = "   ";  // &str
    let spaces = spaces.len();  // usize
    println!("Number of spaces: {}", spaces);

    println!();
}

/// Demonstrates integer types and literals
fn integer_types() {
    println!("🔢 Integer Types");
    println!("----------------");

    // Different integer types
    let a: i8 = 127;  // -128 to 127
    let b: u8 = 255;  // 0 to 255
    let c: i32 = 98_222;  // Default integer type
    let d: u64 = 1_000_000_000;

    println!("i8: {}, u8: {}, i32: {}, u64: {}", a, b, c, d);

    // Number literals
    let decimal = 98_222;
    let hex = 0xff;
    let octal = 0o77;
    let binary = 0b1111_0000;
    let byte = b'A';

    println!("Decimal: {}", decimal);
    println!("Hex: {}", hex);
    println!("Octal: {}", octal);
    println!("Binary: {}", binary);
    println!("Byte: {}", byte);

    // Arithmetic operations
    let sum = 5 + 10;
    let difference = 95 - 4;
    let product = 4 * 30;
    let quotient = 56 / 2;
    let remainder = 43 % 5;

    println!("Sum: {}, Diff: {}, Prod: {}, Quot: {}, Rem: {}",
             sum, difference, product, quotient, remainder);

    // Checked arithmetic (safe from overflow)
    let x: u8 = 255;
    match x.checked_add(1) {
        Some(val) => println!("Result: {}", val),
        None => println!("Overflow detected!"),
    }

    println!();
}

/// Demonstrates floating-point types
fn floating_point() {
    println!("🎯 Floating-Point Types");
    println!("-----------------------");

    let x = 2.0;      // f64 (default)
    let y: f32 = 3.0; // f32 (explicit)

    println!("f64: {}, f32: {}", x, y);

    // Floating-point operations
    let sum = x + 1.5;
    let product = y * 2.5;
    let division = x / y as f64;

    println!("Sum: {}, Product: {}, Division: {}", sum, product, division);

    // Floating-point precision issue
    let imprecise = 0.1 + 0.2;
    println!("0.1 + 0.2 = {} (not exactly 0.3!)", imprecise);

    println!();
}

/// Demonstrates boolean and character types
fn boolean_and_char() {
    println!("✅ Boolean and Character Types");
    println!("------------------------------");

    // Boolean
    let t = true;
    let f: bool = false;
    println!("Boolean: t = {}, f = {}", t, f);

    // Character (Unicode)
    let c = 'z';
    let z = 'ℤ';
    let heart = '😻';

    println!("Characters: {}, {}, {}", c, z, heart);
    println!("Char size: {} bytes", std::mem::size_of::<char>());

    println!();
}

/// Demonstrates tuple types
fn tuples() {
    println!("📦 Tuples");
    println!("---------");

    // Create a tuple
    let tup: (i32, f64, u8) = (500, 6.4, 1);

    // Destructure a tuple
    let (x, y, z) = tup;
    println!("Destructured: x = {}, y = {}, z = {}", x, y, z);

    // Access by index
    let first = tup.0;
    let second = tup.1;
    let third = tup.2;
    println!("By index: {}, {}, {}", first, second, third);

    // Tuple as function return value
    let (min, max) = min_max(vec![5, 2, 8, 1, 9]);
    println!("Min: {}, Max: {}", min, max);

    // Unit type (empty tuple)
    let unit: () = ();
    println!("Unit type: {:?}", unit);

    println!();
}

/// Demonstrates array types
fn arrays() {
    println!("📚 Arrays");
    println!("---------");

    // Create an array
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    println!("Array: {:?}", arr);

    // Initialize with same value
    let zeros = [0; 10];
    println!("Zeros: {:?}", zeros);

    // Access elements
    let first = arr[0];
    let second = arr[1];
    println!("First: {}, Second: {}", first, second);

    // Array length
    println!("Array length: {}", arr.len());

    // Iterate over array
    print!("Elements: ");
    for element in arr.iter() {
        print!("{} ", element);
    }
    println!();

    // Array slicing
    let slice = &arr[1..4];  // Elements at indices 1, 2, 3
    println!("Slice [1..4]: {:?}", slice);

    println!();
}

/// Demonstrates string types
fn string_types() {
    println!("📝 String Types");
    println!("---------------");

    // String literal (&str)
    let s1 = "Hello, world!";
    println!("String literal (&str): {}", s1);

    // String (owned, growable)
    let mut s2 = String::from("Hello");
    s2.push_str(", world!");
    println!("String (owned): {}", s2);

    // Convert &str to String
    let s3 = "initial".to_string();
    println!("To String: {}", s3);

    // String length
    println!("Length: {}", s2.len());

    // String contains
    if s2.contains("world") {
        println!("Contains 'world'!");
    }

    // String replacement
    let s4 = s2.replace("world", "Rust");
    println!("Replaced: {}", s4);

    println!();
}

/// Demonstrates function definitions and calls
fn functions_demo() {
    println!("🔧 Functions");
    println!("------------");

    // Call functions
    let sum = add(5, 3);
    println!("5 + 3 = {}", sum);

    let product = multiply(4, 7);
    println!("4 × 7 = {}", product);

    greet("Rustacean");

    let is_even = is_even_number(42);
    println!("Is 42 even? {}", is_even);

    // Expression vs statement
    let y = {
        let x = 3;
        x + 1  // No semicolon = expression (returns value)
    };
    println!("Block expression result: {}", y);

    println!();
}

/// Demonstrates control flow (if, loops)
fn control_flow() {
    println!("🔀 Control Flow");
    println!("---------------");

    // If expressions
    let number = 6;
    if number % 4 == 0 {
        println!("{} is divisible by 4", number);
    } else if number % 3 == 0 {
        println!("{} is divisible by 3", number);
    } else {
        println!("{} is not divisible by 4 or 3", number);
    }

    // If as expression
    let condition = true;
    let value = if condition { 5 } else { 6 };
    println!("Conditional value: {}", value);

    // Loop with break
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;  // Return value from loop
        }
    };
    println!("Loop result: {}", result);

    // While loop
    let mut number = 3;
    while number != 0 {
        print!("{} ", number);
        number -= 1;
    }
    println!("Liftoff!");

    // For loop with range
    print!("Countdown: ");
    for number in (1..4).rev() {
        print!("{} ", number);
    }
    println!("Go!");

    // For loop with array
    let arr = [10, 20, 30, 40, 50];
    print!("Array elements: ");
    for element in arr.iter() {
        print!("{} ", element);
    }
    println!();

    println!();
}

// Helper functions

/// Adds two numbers
fn add(a: i32, b: i32) -> i32 {
    a + b  // Last expression is returned (no semicolon)
}

/// Multiplies two numbers
fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

/// Greets a person
fn greet(name: &str) {
    println!("Hello, {}!", name);
}

/// Checks if a number is even
fn is_even_number(n: i32) -> bool {
    n % 2 == 0
}

/// Returns minimum and maximum from a vector
fn min_max(numbers: Vec<i32>) -> (i32, i32) {
    let mut min = numbers[0];
    let mut max = numbers[0];

    for &num in numbers.iter() {
        if num < min {
            min = num;
        }
        if num > max {
            max = num;
        }
    }

    (min, max)
}

// Exercise solutions (uncomment to test)

/*
/// Exercise 1: Temperature converter
fn celsius_to_fahrenheit(c: f64) -> f64 {
    (c * 9.0 / 5.0) + 32.0
}

fn fahrenheit_to_celsius(f: f64) -> f64 {
    (f - 32.0) * 5.0 / 9.0
}

/// Exercise 2: Fibonacci numbers
fn fibonacci(n: u32) -> Vec<u32> {
    let mut fib = vec![0, 1];
    for i in 2..n {
        let next = fib[(i - 1) as usize] + fib[(i - 2) as usize];
        fib.push(next);
    }
    fib
}

/// Exercise 4: Array sum
fn array_sum(arr: &[i32]) -> i32 {
    let mut sum = 0;
    for &num in arr {
        sum += num;
    }
    sum
}

/// Exercise 4: Array maximum
fn array_max(arr: &[i32]) -> i32 {
    let mut max = arr[0];
    for &num in arr {
        if num > max {
            max = num;
        }
    }
    max
}
*/
