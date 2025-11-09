//! Project 09: Unsafe Rust & FFI Examples
//!
//! This project demonstrates various unsafe Rust features and FFI (Foreign Function Interface).
//!
//! ⚠️ WARNING: This code intentionally uses unsafe features for educational purposes.
//! In production code, minimize unsafe usage and thoroughly document safety contracts!

use std::alloc::{alloc, dealloc, Layout};
use std::os::raw::{c_char, c_int};
use std::ffi::{CString, CStr};
use std::ptr;

// =============================================================================
// SECTION 1: Raw Pointers
// =============================================================================

/// Demonstrates creating and using raw pointers
fn raw_pointer_basics() {
    println!("\n=== RAW POINTER BASICS ===");

    let mut num = 42;

    // Creating raw pointers (SAFE - no dereference yet)
    let r1 = &num as *const i32;          // Immutable raw pointer
    let r2 = &mut num as *mut i32;        // Mutable raw pointer

    println!("Created raw pointers:");
    println!("  *const i32: {:?}", r1);
    println!("  *mut i32:   {:?}", r2);

    // Dereferencing raw pointers (UNSAFE!)
    unsafe {
        println!("\nDereferencing pointers:");
        println!("  Value through *const: {}", *r1);

        // Modify through mutable raw pointer
        *r2 = 100;
        println!("  Modified through *mut: {}", *r2);
        println!("  Original variable: {}", num);
    }

    // Creating arbitrary memory address (dangerous!)
    let address: usize = 0x12345usize;
    let ptr = address as *const i32;

    println!("\nPointer to arbitrary address: {:?}", ptr);
    // NOTE: Dereferencing this would be UNDEFINED BEHAVIOR!
    // unsafe { let x = *ptr; }  // DON'T DO THIS!
}

/// Demonstrates pointer arithmetic and null pointers
fn raw_pointer_operations() {
    println!("\n=== RAW POINTER OPERATIONS ===");

    let array = [1, 2, 3, 4, 5];
    let ptr = array.as_ptr();

    println!("Array: {:?}", array);

    unsafe {
        // Pointer arithmetic
        println!("\nPointer arithmetic:");
        for i in 0..array.len() {
            let element_ptr = ptr.add(i);
            println!("  Element {}: {}", i, *element_ptr);
        }
    }

    // Null pointer operations
    let null_ptr: *const i32 = ptr::null();

    println!("\nNull pointer checks:");
    println!("  Is null: {}", null_ptr.is_null());

    if !null_ptr.is_null() {
        unsafe {
            println!("  Value: {}", *null_ptr);
        }
    } else {
        println!("  ⚠️  Skipped dereferencing null pointer");
    }
}

// =============================================================================
// SECTION 2: Unsafe Functions
// =============================================================================

/// # Safety
///
/// The caller must ensure that:
/// - `ptr` is non-null
/// - `ptr` points to valid, initialized memory
/// - `ptr` is properly aligned for type T
unsafe fn read_raw<T>(ptr: *const T) -> T
where
    T: Copy,
{
    *ptr
}

/// # Safety
///
/// The caller must ensure that:
/// - `ptr` is non-null and points to valid memory
/// - `value` is a valid instance of T
unsafe fn write_raw<T>(ptr: *mut T, value: T) {
    *ptr = value;
}

fn unsafe_function_examples() {
    println!("\n=== UNSAFE FUNCTIONS ===");

    let x = 42;
    let ptr = &x as *const i32;

    unsafe {
        let value = read_raw(ptr);
        println!("Read value: {}", value);
    }

    let mut y = 0;
    let mut_ptr = &mut y as *mut i32;

    unsafe {
        write_raw(mut_ptr, 100);
    }
    println!("Written value: {}", y);
}

// =============================================================================
// SECTION 3: Manual Memory Management
// =============================================================================

/// Custom box-like type using manual allocation
struct ManualBox<T> {
    ptr: *mut T,
}

impl<T> ManualBox<T> {
    /// Create a new ManualBox with a value
    fn new(value: T) -> Self {
        unsafe {
            // Allocate memory
            let layout = Layout::new::<T>();
            let ptr = alloc(layout) as *mut T;

            if ptr.is_null() {
                panic!("Allocation failed");
            }

            // Write value to allocated memory
            ptr::write(ptr, value);

            ManualBox { ptr }
        }
    }

    /// Get a reference to the value
    fn get(&self) -> &T {
        unsafe { &*self.ptr }
    }

    /// Get a mutable reference to the value
    fn get_mut(&mut self) -> &mut T {
        unsafe { &mut *self.ptr }
    }
}

impl<T> Drop for ManualBox<T> {
    fn drop(&mut self) {
        unsafe {
            // Read the value out (calling its Drop if needed)
            ptr::drop_in_place(self.ptr);

            // Deallocate memory
            let layout = Layout::new::<T>();
            dealloc(self.ptr as *mut u8, layout);
        }
    }
}

fn manual_allocation_example() {
    println!("\n=== MANUAL MEMORY ALLOCATION ===");

    let mut manual_box = ManualBox::new(42);
    println!("ManualBox value: {}", manual_box.get());

    *manual_box.get_mut() = 100;
    println!("Modified value: {}", manual_box.get());

    // Drop is automatically called here
    println!("ManualBox will be dropped now");
}

// =============================================================================
// SECTION 4: FFI - Calling C from Rust
// =============================================================================

// Declare external C functions from the standard C library
extern "C" {
    fn abs(input: c_int) -> c_int;
    fn sqrt(x: f64) -> f64;
    fn strlen(s: *const c_char) -> usize;
}

fn calling_c_functions() {
    println!("\n=== CALLING C FUNCTIONS ===");

    unsafe {
        // Call C's abs function
        let result = abs(-42);
        println!("abs(-42) = {}", result);

        // Call C's sqrt function
        let result = sqrt(16.0);
        println!("sqrt(16.0) = {}", result);

        // Call strlen with a C string
        let c_string = CString::new("Hello, C!").unwrap();
        let len = strlen(c_string.as_ptr());
        println!("strlen('Hello, C!') = {}", len);
    }
}

// =============================================================================
// SECTION 5: FFI - Exposing Rust to C
// =============================================================================

/// Function callable from C
/// # Safety
/// This function is safe to call from C with valid parameters
#[no_mangle]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    a + b
}

/// Function that takes a C string
/// # Safety
/// `name_ptr` must be a valid, null-terminated C string
#[no_mangle]
pub unsafe extern "C" fn rust_greet(name_ptr: *const c_char) {
    if name_ptr.is_null() {
        eprintln!("Error: null pointer passed to rust_greet");
        return;
    }

    let c_str = CStr::from_ptr(name_ptr);
    match c_str.to_str() {
        Ok(name) => println!("Hello from Rust, {}!", name),
        Err(_) => eprintln!("Error: invalid UTF-8 in name"),
    }
}

/// Struct compatible with C
#[repr(C)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}

#[no_mangle]
pub extern "C" fn point_distance(p: Point) -> f64 {
    (p.x * p.x + p.y * p.y).sqrt()
}

fn rust_to_c_examples() {
    println!("\n=== RUST FUNCTIONS CALLABLE FROM C ===");

    // These functions are designed to be called from C,
    // but we can call them from Rust too
    let result = rust_add(10, 32);
    println!("rust_add(10, 32) = {}", result);

    let name = CString::new("Rustacean").unwrap();
    unsafe {
        rust_greet(name.as_ptr());
    }

    let point = Point { x: 3.0, y: 4.0 };
    let distance = point_distance(point);
    println!("Distance of point (3, 4) from origin: {}", distance);
}

// =============================================================================
// SECTION 6: Static Variables
// =============================================================================

static mut COUNTER: i32 = 0;

/// # Safety
/// This function is unsafe because it modifies a static mutable variable.
/// Only call from a single thread or with proper synchronization.
unsafe fn increment_counter() {
    COUNTER += 1;
}

fn static_variable_example() {
    println!("\n=== MUTABLE STATIC VARIABLES ===");

    unsafe {
        println!("Counter before: {}", COUNTER);

        increment_counter();
        increment_counter();
        increment_counter();

        println!("Counter after: {}", COUNTER);
    }
}

// =============================================================================
// SECTION 7: Unsafe Traits
// =============================================================================

/// Trait that guarantees a type can be safely zeroed
unsafe trait Zeroable {
    fn zeroed() -> Self;
}

// SAFE: i32 can be all zeros
unsafe impl Zeroable for i32 {
    fn zeroed() -> Self {
        0
    }
}

// SAFE: f64 with all bits zero represents 0.0
unsafe impl Zeroable for f64 {
    fn zeroed() -> Self {
        0.0
    }
}

#[repr(C)]
struct Vec3 {
    x: f64,
    y: f64,
    z: f64,
}

// SAFE: All fields are Zeroable
unsafe impl Zeroable for Vec3 {
    fn zeroed() -> Self {
        Vec3 { x: 0.0, y: 0.0, z: 0.0 }
    }
}

fn unsafe_trait_example() {
    println!("\n=== UNSAFE TRAITS ===");

    let zero_i32 = i32::zeroed();
    let zero_f64 = f64::zeroed();
    let zero_vec3 = Vec3::zeroed();

    println!("Zeroed i32: {}", zero_i32);
    println!("Zeroed f64: {}", zero_f64);
    println!("Zeroed Vec3: ({}, {}, {})", zero_vec3.x, zero_vec3.y, zero_vec3.z);
}

// =============================================================================
// SECTION 8: Safe Wrappers Around Unsafe Code
// =============================================================================

/// A safe vector-like structure built on unsafe foundations
pub struct SimpleVec<T> {
    ptr: *mut T,
    len: usize,
    capacity: usize,
}

impl<T> SimpleVec<T> {
    /// Create a new empty SimpleVec
    pub fn new() -> Self {
        SimpleVec {
            ptr: ptr::null_mut(),
            len: 0,
            capacity: 0,
        }
    }

    /// Push a value onto the end
    pub fn push(&mut self, value: T) {
        if self.len == self.capacity {
            self.grow();
        }

        unsafe {
            let ptr = self.ptr.add(self.len);
            ptr::write(ptr, value);
        }

        self.len += 1;
    }

    /// Get a reference to an element
    pub fn get(&self, index: usize) -> Option<&T> {
        if index < self.len {
            unsafe {
                Some(&*self.ptr.add(index))
            }
        } else {
            None
        }
    }

    /// Get the length
    pub fn len(&self) -> usize {
        self.len
    }

    /// Check if empty
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// Grow the capacity
    fn grow(&mut self) {
        let new_capacity = if self.capacity == 0 { 1 } else { self.capacity * 2 };

        let new_layout = Layout::array::<T>(new_capacity).unwrap();

        let new_ptr = if self.capacity == 0 {
            unsafe { alloc(new_layout) as *mut T }
        } else {
            let old_layout = Layout::array::<T>(self.capacity).unwrap();
            unsafe {
                std::alloc::realloc(
                    self.ptr as *mut u8,
                    old_layout,
                    new_layout.size(),
                ) as *mut T
            }
        };

        if new_ptr.is_null() {
            panic!("Allocation failed");
        }

        self.ptr = new_ptr;
        self.capacity = new_capacity;
    }
}

impl<T> Drop for SimpleVec<T> {
    fn drop(&mut self) {
        if self.capacity > 0 {
            unsafe {
                // Drop all elements
                for i in 0..self.len {
                    ptr::drop_in_place(self.ptr.add(i));
                }

                // Deallocate memory
                let layout = Layout::array::<T>(self.capacity).unwrap();
                dealloc(self.ptr as *mut u8, layout);
            }
        }
    }
}

fn safe_wrapper_example() {
    println!("\n=== SAFE WRAPPER AROUND UNSAFE CODE ===");

    let mut vec = SimpleVec::new();

    println!("Pushing values...");
    vec.push(1);
    vec.push(2);
    vec.push(3);
    vec.push(4);
    vec.push(5);

    println!("SimpleVec length: {}", vec.len());

    for i in 0..vec.len() {
        if let Some(value) = vec.get(i) {
            println!("  Element {}: {}", i, value);
        }
    }

    // The Drop implementation will clean up when vec goes out of scope
}

// =============================================================================
// SECTION 9: Working with C Strings
// =============================================================================

fn c_string_conversions() {
    println!("\n=== C STRING CONVERSIONS ===");

    // Rust String to C string
    let rust_string = String::from("Hello from Rust!");
    let c_string = CString::new(rust_string.clone()).expect("CString::new failed");

    println!("Rust String: {}", rust_string);
    println!("As C string ptr: {:?}", c_string.as_ptr());

    // C string back to Rust
    unsafe {
        let c_str = CStr::from_ptr(c_string.as_ptr());
        let back_to_rust = c_str.to_str().expect("Invalid UTF-8");
        println!("Back to Rust: {}", back_to_rust);
    }

    // Using with C functions
    unsafe {
        let length = strlen(c_string.as_ptr());
        println!("C string length: {}", length);
    }
}

// =============================================================================
// SECTION 10: Union Types
// =============================================================================

#[repr(C)]
union IntOrFloat {
    i: i32,
    f: f32,
}

fn union_example() {
    println!("\n=== UNION TYPES ===");

    let mut u = IntOrFloat { i: 42 };

    unsafe {
        println!("As integer: {}", u.i);

        u.f = 3.14;
        println!("As float: {}", u.f);

        // Reading the integer representation after writing float
        // This is the bit pattern of the float interpreted as int
        println!("Float bits as int: {}", u.i);
    }

    // This demonstrates type punning - reinterpreting bytes as different types
    let value = 1.0f32;
    let bits = unsafe {
        let u = IntOrFloat { f: value };
        u.i
    };
    println!("Bit representation of 1.0f32: 0x{:08x}", bits);
}

// =============================================================================
// MAIN FUNCTION
// =============================================================================

fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║        Project 09: Unsafe Rust & FFI Examples             ║");
    println!("║                                                            ║");
    println!("║  ⚠️  WARNING: Educational unsafe code ahead!               ║");
    println!("╚════════════════════════════════════════════════════════════╝");

    // Run all examples
    raw_pointer_basics();
    raw_pointer_operations();
    unsafe_function_examples();
    manual_allocation_example();
    calling_c_functions();
    rust_to_c_examples();
    static_variable_example();
    unsafe_trait_example();
    safe_wrapper_example();
    c_string_conversions();
    union_example();

    println!("\n╔════════════════════════════════════════════════════════════╗");
    println!("║                      Key Takeaways                         ║");
    println!("║                                                            ║");
    println!("║  1. Unsafe is a tool, not a crutch                        ║");
    println!("║  2. Always document safety contracts                      ║");
    println!("║  3. Minimize unsafe surface area                          ║");
    println!("║  4. Wrap unsafe in safe abstractions                      ║");
    println!("║  5. Test thoroughly with tools like Miri                  ║");
    println!("╚════════════════════════════════════════════════════════════╝");
}

// =============================================================================
// TESTS
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_manual_box() {
        let mut b = ManualBox::new(42);
        assert_eq!(*b.get(), 42);

        *b.get_mut() = 100;
        assert_eq!(*b.get(), 100);
    }

    #[test]
    fn test_simple_vec() {
        let mut vec = SimpleVec::new();
        assert_eq!(vec.len(), 0);
        assert!(vec.is_empty());

        vec.push(1);
        vec.push(2);
        vec.push(3);

        assert_eq!(vec.len(), 3);
        assert_eq!(vec.get(0), Some(&1));
        assert_eq!(vec.get(1), Some(&2));
        assert_eq!(vec.get(2), Some(&3));
        assert_eq!(vec.get(3), None);
    }

    #[test]
    fn test_rust_add() {
        assert_eq!(rust_add(5, 3), 8);
        assert_eq!(rust_add(-5, 3), -2);
    }

    #[test]
    fn test_point_distance() {
        let p = Point { x: 3.0, y: 4.0 };
        let distance = point_distance(p);
        assert_eq!(distance, 5.0);
    }
}
