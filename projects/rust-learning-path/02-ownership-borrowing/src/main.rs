// Project 02: Ownership & Borrowing
// Deep dive into Rust's ownership system

fn main() {
    println!("🦀 Ownership & Borrowing in Rust");
    println!("==================================\n");

    ownership_basics();
    move_semantics();
    clone_and_copy();
    borrowing_immutable();
    borrowing_mutable();
    borrowing_rules();
    slices_demo();
    string_slices();
    dangling_references();
}

/// Demonstrates basic ownership rules
fn ownership_basics() {
    println!("📦 Ownership Basics");
    println!("-------------------");

    // Rule 1: Each value has exactly one owner
    let s1 = String::from("hello");
    println!("s1 owns: {}", s1);

    // Rule 2: When owner goes out of scope, value is dropped
    {
        let s2 = String::from("scoped");
        println!("s2 is valid here: {}", s2);
    } // s2 is dropped here
    // println!("{}", s2); // ERROR: s2 no longer exists

    // Rule 3: Only one owner at a time
    let s3 = s1;  // Ownership moves from s1 to s3
    println!("s3 now owns: {}", s3);
    // println!("{}", s1); // ERROR: s1 is no longer valid

    println!();
}

/// Demonstrates move semantics
fn move_semantics() {
    println!("🚚 Move Semantics");
    println!("-----------------");

    // Heap-allocated data is moved
    let s1 = String::from("hello");
    let s2 = s1;  // s1's data is moved to s2
    // s1 is now invalid!

    println!("s2: {}", s2);
    // println!("s1: {}", s1); // ERROR: value used after move

    // Passing to function moves ownership
    let s3 = String::from("world");
    takes_ownership(s3);
    // println!("{}", s3); // ERROR: s3 was moved

    // Function can return ownership
    let s4 = gives_ownership();
    println!("s4: {}", s4);

    // Take and give back ownership
    let s5 = String::from("roundtrip");
    let s5 = takes_and_gives_back(s5);
    println!("s5 after roundtrip: {}", s5);

    println!();
}

/// Demonstrates clone and copy
fn clone_and_copy() {
    println!("📋 Clone vs Copy");
    println!("----------------");

    // Clone: Explicit deep copy
    let s1 = String::from("hello");
    let s2 = s1.clone();  // Explicitly copy heap data
    println!("s1: {}, s2: {} (both valid!)", s1, s2);

    // Copy: Implicit copy for stack-only types
    let x = 5;
    let y = x;  // i32 implements Copy trait
    println!("x: {}, y: {} (both valid!)", x, y);

    // Types that implement Copy:
    // - All integers, floats, booleans, char
    // - Tuples containing only Copy types
    let tuple = (5, 3.14, 'a');
    let tuple_copy = tuple;
    println!("Both tuples valid: {:?}, {:?}", tuple, tuple_copy);

    println!();
}

/// Demonstrates immutable borrowing
fn borrowing_immutable() {
    println!("👀 Immutable Borrowing");
    println!("----------------------");

    let s1 = String::from("hello");

    // Create immutable references (borrowing)
    let len = calculate_length(&s1);
    println!("The length of '{}' is {}", s1, len);
    // s1 is still valid because we only borrowed it!

    // Multiple immutable references are OK
    let r1 = &s1;
    let r2 = &s1;
    let r3 = &s1;
    println!("Multiple refs: {}, {}, {}", r1, r2, r3);

    println!();
}

/// Demonstrates mutable borrowing
fn borrowing_mutable() {
    println!("✏️  Mutable Borrowing");
    println!("---------------------");

    let mut s = String::from("hello");

    // Create a mutable reference
    change(&mut s);
    println!("After change: {}", s);

    // Can only have ONE mutable reference at a time
    let r1 = &mut s;
    // let r2 = &mut s; // ERROR: cannot borrow as mutable more than once
    r1.push_str("!");
    println!("After r1: {}", r1);

    // After r1 is done, we can create another mutable ref
    let r2 = &mut s;
    r2.push_str("!");
    println!("After r2: {}", r2);

    println!();
}

/// Demonstrates borrowing rules
fn borrowing_rules() {
    println!("📜 Borrowing Rules");
    println!("------------------");

    let mut s = String::from("hello");

    // Rule: Can't have mutable ref while immutable refs exist
    let r1 = &s;     // OK
    let r2 = &s;     // OK
    println!("{} and {}", r1, r2);
    // r1 and r2 are no longer used after this point

    let r3 = &mut s; // OK - no immutable refs active
    r3.push_str(" world");
    println!("{}", r3);

    // The scope of references ends at their last use
    let r4 = &s;
    println!("{}", r4);
    // r4 is no longer used

    let r5 = &mut s;
    r5.push_str("!");
    println!("{}", r5);

    println!();
}

/// Demonstrates slices
fn slices_demo() {
    println!("🔪 Slices");
    println!("---------");

    // Array slices
    let arr = [1, 2, 3, 4, 5];

    let slice1 = &arr[1..3];  // Elements 1, 2 (index 1,2)
    println!("Slice [1..3]: {:?}", slice1);

    let slice2 = &arr[..3];   // From start to 3
    println!("Slice [..3]: {:?}", slice2);

    let slice3 = &arr[2..];   // From 2 to end
    println!("Slice [2..]: {:?}", slice3);

    let slice4 = &arr[..];    // Entire array
    println!("Slice [..]: {:?}", slice4);

    println!();
}

/// Demonstrates string slices
fn string_slices() {
    println!("📝 String Slices");
    println!("----------------");

    let s = String::from("hello world");

    // String slices (&str)
    let hello = &s[0..5];
    let world = &s[6..11];
    println!("'{}' and '{}'", hello, world);

    // Using string slices prevents errors
    let word = first_word(&s);
    println!("First word: {}", word);

    // String literals are slices
    let literal: &str = "hello";  // &str type
    println!("Literal: {}", literal);

    // Function that works with both String and &str
    let s1 = String::from("hello");
    let s2 = "world";
    print_slice(&s1);  // String (coerced to &str)
    print_slice(s2);   // Already &str

    println!();
}

/// Demonstrates why dangling references are prevented
fn dangling_references() {
    println!("⚠️  Dangling References (Prevented!)");
    println!("-------------------------------------");

    // This would create a dangling reference (doesn't compile):
    // let reference_to_nothing = dangle();

    // Instead, return the String itself (transfer ownership)
    let s = no_dangle();
    println!("Valid string: {}", s);

    println!();
}

// Helper functions

fn takes_ownership(s: String) {
    println!("  takes_ownership: {}", s);
} // s is dropped here

fn gives_ownership() -> String {
    String::from("ownership given")
}

fn takes_and_gives_back(s: String) -> String {
    s  // Return ownership
}

fn calculate_length(s: &String) -> usize {
    s.len()
} // s goes out of scope, but doesn't drop the String (it doesn't own it)

fn change(s: &mut String) {
    s.push_str(", world");
}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}

fn print_slice(s: &str) {
    println!("  Slice: {}", s);
}

// This would cause a compile error (dangling reference)
/*
fn dangle() -> &String {
    let s = String::from("hello");
    &s  // ERROR: s will be dropped, reference would be invalid!
}
*/

fn no_dangle() -> String {
    let s = String::from("hello");
    s  // Transfer ownership out
}

// Exercise Solutions (uncomment to test)

/*
/// Exercise 2: Get first word without taking ownership
fn first_word_exercise(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &byte) in bytes.iter().enumerate() {
        if byte == b' ' {
            return &s[..i];
        }
    }
    &s[..]
}

/// Exercise 3: Take ownership and modify
fn take_and_modify(mut v: Vec<i32>) -> Vec<i32> {
    v.push(42);
    v
}

/// Exercise 3: Borrow mutably and modify in place
fn borrow_and_modify(v: &mut Vec<i32>) {
    v.push(42);
}

/// Exercise 3: Borrow immutably and compute
fn borrow_and_compute(v: &Vec<i32>) -> i32 {
    v.iter().sum()
}
*/
