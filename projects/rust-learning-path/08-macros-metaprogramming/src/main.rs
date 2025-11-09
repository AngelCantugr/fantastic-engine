// Project 08: Macros & Metaprogramming
// Comprehensive examples of declarative and procedural macros in Rust

fn main() {
    println!("🦀 Macros & Metaprogramming in Rust");
    println!("====================================\n");

    // Run all example functions
    basic_macros();
    macro_patterns();
    macro_repetition();
    variadic_macros();
    multiple_patterns();
    macro_hygiene_demo();
    practical_macros();
    debugging_macros();
}

// ============================================================================
// 1. BASIC DECLARATIVE MACROS
// ============================================================================

/// Simple macro without arguments
macro_rules! say_hello {
    () => {
        println!("Hello from a macro!");
    };
}

/// Macro with a single argument
macro_rules! greet {
    ($name:expr) => {
        println!("Hello, {}!", $name);
    };
}

/// Macro that creates a function
macro_rules! create_function {
    ($func_name:ident) => {
        fn $func_name() {
            println!("Function {:?} was called", stringify!($func_name));
        }
    };
}

fn basic_macros() {
    println!("📝 Basic Declarative Macros");
    println!("----------------------------");

    say_hello!();
    greet!("Rustacean");
    greet!("Ferris");

    // Create functions using macro
    create_function!(foo);
    create_function!(bar);

    foo();
    bar();

    println!();
}

// ============================================================================
// 2. MACRO PATTERN DESIGNATORS
// ============================================================================

/// Demonstrates different designators
macro_rules! show_designators {
    // Expression
    (expr: $e:expr) => {
        println!("Expression: {} = {}", stringify!($e), $e);
    };

    // Identifier
    (ident: $i:ident) => {
        println!("Identifier: {}", stringify!($i));
    };

    // Type
    (type: $t:ty) => {
        println!("Type: {}", stringify!($t));
    };

    // Pattern
    (pattern: $p:pat) => {
        let $p = 42;
        println!("Pattern matched!");
    };

    // Block
    (block: $b:block) => {
        println!("Executing block:");
        $b
    };
}

fn macro_patterns() {
    println!("🎯 Macro Pattern Designators");
    println!("------------------------------");

    show_designators!(expr: 2 + 2);
    show_designators!(expr: "hello".len());

    show_designators!(ident: my_variable);

    show_designators!(type: i32);
    show_designators!(type: Vec<String>);

    show_designators!(pattern: _x);

    show_designators!(block: {
        println!("  Inside block!");
        let result = 10 * 5;
        println!("  Result: {}", result);
    });

    println!();
}

// ============================================================================
// 3. MACRO REPETITION
// ============================================================================

/// Zero or more repetitions (*)
macro_rules! vec_of {
    ($($element:expr),*) => {
        {
            let mut v = Vec::new();
            $(
                v.push($element);
            )*
            v
        }
    };
}

/// One or more repetitions (+)
macro_rules! min {
    ($first:expr $(, $rest:expr)+) => {
        {
            let mut minimum = $first;
            $(
                if $rest < minimum {
                    minimum = $rest;
                }
            )+
            minimum
        }
    };
}

/// Optional (?)
macro_rules! print_optional {
    ($value:expr, $format:expr) => {
        println!($format, $value);
    };
    ($value:expr) => {
        println!("{}", $value);
    };
}

fn macro_repetition() {
    println!("🔁 Macro Repetition Patterns");
    println!("-----------------------------");

    let v = vec_of![1, 2, 3, 4, 5];
    println!("Vector: {:?}", v);

    let v2: Vec<i32> = vec_of![];  // Empty vector
    println!("Empty vector: {:?}", v2);

    let minimum = min!(5, 3, 8, 1, 9, 2);
    println!("Minimum: {}", minimum);

    print_optional!(42);
    print_optional!(42, "Value: {}");

    println!();
}

// ============================================================================
// 4. VARIADIC MACROS
// ============================================================================

/// Sum variadic arguments
macro_rules! sum {
    ($($x:expr),+ $(,)?) => {
        {
            let mut total = 0;
            $(
                total += $x;
            )+
            total
        }
    };
}

/// Count arguments
macro_rules! count {
    () => { 0 };
    ($head:expr $(, $tail:expr)*) => {
        1 + count!($($tail),*)
    };
}

/// Print all arguments
macro_rules! print_all {
    ($($arg:expr),* $(,)?) => {
        {
            let mut count = 0;
            $(
                count += 1;
                println!("  Arg {}: {}", count, $arg);
            )*
        }
    };
}

fn variadic_macros() {
    println!("📦 Variadic Macros");
    println!("------------------");

    let total = sum!(1, 2, 3, 4, 5);
    println!("Sum: {}", total);

    let total2 = sum!(10, 20, 30);
    println!("Sum: {}", total2);

    println!("Count: {}", count!(1, 2, 3, 4));
    println!("Count: {}", count!());

    println!("Arguments:");
    print_all!(42, "hello", 3.14, true);

    println!();
}

// ============================================================================
// 5. MULTIPLE PATTERNS
// ============================================================================

/// Calculator with different operations
macro_rules! calculate {
    (add $a:expr, $b:expr) => {
        $a + $b
    };

    (sub $a:expr, $b:expr) => {
        $a - $b
    };

    (mul $a:expr, $b:expr) => {
        $a * $b
    };

    (div $a:expr, $b:expr) => {
        $a / $b
    };

    (pow $a:expr, $b:expr) => {
        ($a as i32).pow($b as u32)
    };
}

/// Type conversion macro
macro_rules! convert {
    ($value:expr => i32) => {
        $value as i32
    };

    ($value:expr => f64) => {
        $value as f64
    };

    ($value:expr => String) => {
        $value.to_string()
    };
}

fn multiple_patterns() {
    println!("🔀 Multiple Pattern Matching");
    println!("-----------------------------");

    println!("5 + 3 = {}", calculate!(add 5, 3));
    println!("10 - 4 = {}", calculate!(sub 10, 4));
    println!("6 * 7 = {}", calculate!(mul 6, 7));
    println!("20 / 4 = {}", calculate!(div 20, 4));
    println!("2 ^ 8 = {}", calculate!(pow 2, 8));

    let x = 42;
    println!("As i32: {}", convert!(x => i32));
    println!("As f64: {}", convert!(x => f64));
    println!("As String: {}", convert!(x => String));

    println!();
}

// ============================================================================
// 6. MACRO HYGIENE
// ============================================================================

/// Demonstrates hygiene - variables don't leak
macro_rules! with_temp {
    ($expr:expr) => {
        {
            let temp = 100;  // Local to macro
            $expr + temp
        }
    };
}

/// Intentional capture with identifier
macro_rules! with_var {
    ($var:ident, $expr:expr) => {
        {
            let $var = 42;
            $expr
        }
    };
}

fn macro_hygiene_demo() {
    println!("🧼 Macro Hygiene");
    println!("----------------");

    let result = with_temp!(10);
    println!("Result: {}", result);

    // This would error - temp not in scope
    // let x = temp;

    let result2 = with_var!(value, value * 2);
    println!("Result with var: {}", result2);

    println!();
}

// ============================================================================
// 7. PRACTICAL UTILITY MACROS
// ============================================================================

/// HashMap creation macro
macro_rules! hashmap {
    ($($key:expr => $value:expr),* $(,)?) => {
        {
            let mut map = std::collections::HashMap::new();
            $(
                map.insert($key, $value);
            )*
            map
        }
    };
}

/// Timing macro
macro_rules! time_it {
    ($name:expr, $code:block) => {
        {
            let start = std::time::Instant::now();
            let result = $code;
            let elapsed = start.elapsed();
            println!("{} took: {:?}", $name, elapsed);
            result
        }
    };
}

/// Conditional logging
macro_rules! debug_log {
    ($($arg:tt)*) => {
        #[cfg(debug_assertions)]
        {
            println!("[DEBUG] {}", format!($($arg)*));
        }
    };
}

/// Struct field printer
macro_rules! print_struct {
    ($struct_name:ident { $($field:ident),* $(,)? }) => {
        {
            println!("{}:", stringify!($struct_name));
            $(
                println!("  {}: {:?}", stringify!($field), $struct_name.$field);
            )*
        }
    };
}

fn practical_macros() {
    println!("🛠️  Practical Utility Macros");
    println!("----------------------------");

    // HashMap creation
    let map = hashmap! {
        "one" => 1,
        "two" => 2,
        "three" => 3,
    };
    println!("HashMap: {:?}", map);

    // Timing
    let _result = time_it!("Computation", {
        let mut sum = 0;
        for i in 0..1000 {
            sum += i;
        }
        sum
    });

    // Debug logging
    debug_log!("This is a debug message");
    debug_log!("Value: {}", 42);

    // Struct printing
    struct Person {
        name: String,
        age: u32,
    }

    let person = Person {
        name: String::from("Alice"),
        age: 30,
    };

    print_struct!(person { name, age });

    println!();
}

// ============================================================================
// 8. DEBUGGING MACROS
// ============================================================================

/// Macro that shows its expansion
macro_rules! show_expansion {
    ($($tt:tt)*) => {
        {
            println!("Macro input: {}", stringify!($($tt)*));
            // Actual expansion would go here
            $($tt)*
        }
    };
}

/// Macro with detailed output
macro_rules! debug_macro {
    ($name:ident = $value:expr) => {
        {
            println!("Creating variable: {}", stringify!($name));
            println!("With value: {}", stringify!($value));
            let $name = $value;
            println!("Variable created!");
            $name
        }
    };
}

fn debugging_macros() {
    println!("🐛 Debugging Macros");
    println!("-------------------");

    show_expansion! {
        let x = 42;
        println!("x = {}", x);
    }

    let y = debug_macro!(my_var = 100);
    println!("y = {}", y);

    println!();
    println!("💡 Tip: Use 'cargo expand' to see full macro expansions!");
    println!();
}

// ============================================================================
// ADVANCED MACRO EXAMPLES
// ============================================================================

/// DSL for simple state machine
macro_rules! state_machine {
    ($($state:ident -> $next:ident),* $(,)?) => {
        {
            use std::collections::HashMap;
            let mut transitions = HashMap::new();
            $(
                transitions.insert(stringify!($state), stringify!($next));
            )*
            transitions
        }
    };
}

/// Generate enum with useful methods
macro_rules! generate_enum {
    ($name:ident { $($variant:ident),* $(,)? }) => {
        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        enum $name {
            $($variant),*
        }

        impl $name {
            fn variants() -> &'static [&'static str] {
                &[$(stringify!($variant)),*]
            }

            fn count() -> usize {
                [$($name::$variant),*].len()
            }
        }
    };
}

/// Trait implementation generator
macro_rules! impl_display {
    ($type:ty, $fmt:expr) => {
        impl std::fmt::Display for $type {
            fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                write!(f, $fmt, self)
            }
        }
    };
}

// Usage examples (in comments to avoid conflicts)

/*
// State machine DSL
let states = state_machine! {
    Start -> Processing,
    Processing -> Complete,
    Complete -> Start,
};

// Enum generation
generate_enum! {
    Color {
        Red,
        Green,
        Blue,
    }
}

println!("Color variants: {:?}", Color::variants());
println!("Color count: {}", Color::count());

// Custom display implementation
struct Point {
    x: i32,
    y: i32,
}

impl_display!(Point, "Point({}, {})");
*/

// ============================================================================
// EXERCISE SOLUTIONS (Commented out)
// ============================================================================

/*
/// Exercise 1: Struct field printer with values
macro_rules! print_fields {
    ($instance:expr, { $($field:ident),* $(,)? }) => {
        {
            println!("Struct instance:");
            $(
                println!("  {}: {:?}", stringify!($field), $instance.$field);
            )*
        }
    };
}

/// Exercise 2: Test case generator
macro_rules! test_cases {
    ($($name:ident: $input:expr => $expected:expr),* $(,)?) => {
        $(
            #[test]
            fn $name() {
                assert_eq!($input, $expected);
            }
        )*
    };
}

// Usage:
test_cases! {
    test_add: 2 + 2 => 4,
    test_mul: 3 * 3 => 9,
    test_sub: 10 - 5 => 5,
}

/// Exercise 3: Builder pattern generator
macro_rules! builder {
    ($name:ident { $($field:ident: $type:ty),* $(,)? }) => {
        struct $name {
            $($field: $type),*
        }

        paste::paste! {
            struct [<$name Builder>] {
                $($field: Option<$type>),*
            }

            impl [<$name Builder>] {
                fn new() -> Self {
                    Self {
                        $($field: None),*
                    }
                }

                $(
                    fn $field(mut self, $field: $type) -> Self {
                        self.$field = Some($field);
                        self
                    }
                )*

                fn build(self) -> Result<$name, &'static str> {
                    Ok($name {
                        $($field: self.$field.ok_or("Missing field")?),*
                    })
                }
            }
        }
    };
}

/// Exercise 4: Conditional logger with levels
macro_rules! log {
    (error: $($arg:tt)*) => {
        eprintln!("[ERROR] {}", format!($($arg)*));
    };

    (warn: $($arg:tt)*) => {
        #[cfg(not(test))]
        println!("[WARN] {}", format!($($arg)*));
    };

    (info: $($arg:tt)*) => {
        #[cfg(debug_assertions)]
        println!("[INFO] {}", format!($($arg)*));
    };

    (debug: $($arg:tt)*) => {
        #[cfg(debug_assertions)]
        println!("[DEBUG] {}", format!($($arg)*));
    };
}

/// Exercise 5: Enum variant counter
macro_rules! count_variants {
    ($name:ident { $($variant:ident),* $(,)? }) => {
        impl $name {
            pub const COUNT: usize = {
                let mut count = 0;
                $(
                    let _ = stringify!($variant);
                    count += 1;
                )*
                count
            };
        }
    };
}
*/

// ============================================================================
// PROCEDURAL MACRO EXAMPLES (Conceptual)
// ============================================================================

/*
Note: Procedural macros require a separate crate with proc-macro = true
in Cargo.toml. Here's what they would look like:

// In a proc-macro crate:

use proc_macro::TokenStream;
use quote::quote;
use syn;

// Derive macro
#[proc_macro_derive(MyTrait)]
pub fn derive_my_trait(input: TokenStream) -> TokenStream {
    let ast = syn::parse(input).unwrap();
    impl_my_trait(&ast)
}

fn impl_my_trait(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let gen = quote! {
        impl MyTrait for #name {
            fn my_method(&self) {
                println!("MyTrait implemented for {}", stringify!(#name));
            }
        }
    };
    gen.into()
}

// Attribute macro
#[proc_macro_attribute]
pub fn my_attribute(attr: TokenStream, item: TokenStream) -> TokenStream {
    // Transform the item based on attribute
    item
}

// Function-like macro
#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    // Parse input and generate code
    TokenStream::new()
}

// Usage:
#[derive(MyTrait)]
struct Foo;

#[my_attribute]
fn bar() {}

my_macro! { ... }
*/
