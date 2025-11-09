// Project 05: Type System & Pattern Matching
// Comprehensive examples of structs, enums, and pattern matching

fn main() {
    println!("🦀 Type System & Pattern Matching");
    println!("==================================\n");

    struct_basics();
    tuple_and_unit_structs();
    methods_and_associated_functions();
    enum_basics();
    enums_with_data();
    pattern_matching();
    destructuring_patterns();
    match_guards();
    if_let_while_let();
    newtype_pattern();
    real_world_modeling();
}

/// Demonstrates basic named structs
fn struct_basics() {
    println!("📦 Struct Basics");
    println!("----------------");

    // Define a struct
    struct Person {
        name: String,
        age: u32,
        email: String,
    }

    // Create an instance
    let person = Person {
        name: String::from("Alice"),
        age: 30,
        email: String::from("alice@example.com"),
    };

    println!("Person: {} ({}) - {}", person.name, person.age, person.email);

    // Field shorthand
    fn create_person(name: String, age: u32) -> Person {
        let email = format!("{}@example.com", name.to_lowercase());
        Person { name, age, email }  // Shorthand when var name matches field
    }

    let bob = create_person(String::from("Bob"), 25);
    println!("Created: {} ({}) - {}", bob.name, bob.age, bob.email);

    // Struct update syntax
    let charlie = Person {
        name: String::from("Charlie"),
        email: String::from("charlie@example.com"),
        ..bob  // Copy remaining fields (age) from bob
    };
    println!("With update: {} ({}) - {}", charlie.name, charlie.age, charlie.email);

    // Mutable struct
    let mut diana = Person {
        name: String::from("Diana"),
        age: 28,
        email: String::from("diana@example.com"),
    };

    diana.age = 29;
    println!("After birthday: {} is now {}", diana.name, diana.age);

    println!();
}

/// Demonstrates tuple structs and unit structs
fn tuple_and_unit_structs() {
    println!("📦 Tuple & Unit Structs");
    println!("-----------------------");

    // Tuple struct - unnamed fields
    struct Point(i32, i32);
    struct Color(u8, u8, u8);

    let origin = Point(0, 0);
    let black = Color(0, 0, 0);

    println!("Point: ({}, {})", origin.0, origin.1);
    println!("Color: RGB({}, {}, {})", black.0, black.1, black.2);

    // Unit struct - no fields
    struct AlwaysEqual;

    let _subject = AlwaysEqual;
    println!("Unit struct created (zero size)");

    // Common use: Newtype pattern
    struct Meters(i32);
    struct Feet(i32);

    let distance_m = Meters(100);
    let distance_f = Feet(328);

    println!("Distance: {}m or {}ft", distance_m.0, distance_f.0);

    println!();
}

/// Demonstrates methods and associated functions
fn methods_and_associated_functions() {
    println!("🔧 Methods & Associated Functions");
    println!("----------------------------------");

    #[derive(Debug)]
    struct Rectangle {
        width: u32,
        height: u32,
    }

    impl Rectangle {
        // Associated function (constructor)
        fn new(width: u32, height: u32) -> Self {
            Rectangle { width, height }
        }

        // Associated function (alternative constructor)
        fn square(size: u32) -> Self {
            Rectangle {
                width: size,
                height: size,
            }
        }

        // Method - borrows immutably
        fn area(&self) -> u32 {
            self.width * self.height
        }

        // Method - borrows immutably
        fn perimeter(&self) -> u32 {
            2 * (self.width + self.height)
        }

        // Method - borrows immutably with parameter
        fn can_hold(&self, other: &Rectangle) -> bool {
            self.width > other.width && self.height > other.height
        }

        // Method - borrows mutably
        fn scale(&mut self, factor: u32) {
            self.width *= factor;
            self.height *= factor;
        }

        // Method - consumes self
        fn into_square(self) -> Rectangle {
            let size = std::cmp::max(self.width, self.height);
            Rectangle::new(size, size)
        }

        // Method - returns bool
        fn is_square(&self) -> bool {
            self.width == self.height
        }
    }

    // Using associated functions
    let rect1 = Rectangle::new(30, 50);
    let square = Rectangle::square(25);

    println!("Rectangle: {:?}", rect1);
    println!("Square: {:?}", square);

    // Using methods
    println!("Area of rect1: {}", rect1.area());
    println!("Perimeter of rect1: {}", rect1.perimeter());
    println!("Is rect1 a square? {}", rect1.is_square());
    println!("Is square a square? {}", square.is_square());

    let rect2 = Rectangle::new(10, 20);
    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));

    // Mutable method
    let mut rect3 = Rectangle::new(5, 10);
    println!("Before scaling: {:?}", rect3);
    rect3.scale(2);
    println!("After scaling by 2: {:?}", rect3);

    // Consuming method
    let rect4 = Rectangle::new(10, 20);
    let new_square = rect4.into_square();
    println!("Converted to square: {:?}", new_square);
    // println!("{:?}", rect4);  // Error: rect4 was consumed

    println!();
}

/// Demonstrates basic enums
fn enum_basics() {
    println!("🎯 Enum Basics");
    println!("--------------");

    // Simple enum
    #[derive(Debug)]
    enum Direction {
        North,
        South,
        East,
        West,
    }

    let direction = Direction::North;
    println!("Direction: {:?}", direction);

    // Enum with associated values
    #[derive(Debug)]
    enum TrafficLight {
        Red,
        Yellow,
        Green,
    }

    impl TrafficLight {
        fn duration(&self) -> u32 {
            match self {
                TrafficLight::Red => 60,
                TrafficLight::Yellow => 5,
                TrafficLight::Green => 45,
            }
        }

        fn next(&self) -> TrafficLight {
            match self {
                TrafficLight::Red => TrafficLight::Green,
                TrafficLight::Yellow => TrafficLight::Red,
                TrafficLight::Green => TrafficLight::Yellow,
            }
        }
    }

    let light = TrafficLight::Red;
    println!("Light: {:?}, Duration: {}s", light, light.duration());

    let next_light = light.next();
    println!("Next light: {:?}", next_light);

    println!();
}

/// Demonstrates enums with data
fn enums_with_data() {
    println!("📊 Enums with Data");
    println!("------------------");

    // Enum with different data types
    #[derive(Debug)]
    enum Message {
        Quit,                                   // Unit variant
        Move { x: i32, y: i32 },               // Struct variant
        Write(String),                          // Tuple variant
        ChangeColor(u8, u8, u8),               // Tuple variant
    }

    let msg1 = Message::Quit;
    let msg2 = Message::Move { x: 10, y: 20 };
    let msg3 = Message::Write(String::from("Hello, Rust!"));
    let msg4 = Message::ChangeColor(255, 0, 0);

    println!("msg1: {:?}", msg1);
    println!("msg2: {:?}", msg2);
    println!("msg3: {:?}", msg3);
    println!("msg4: {:?}", msg4);

    // Methods on enums
    impl Message {
        fn call(&self) {
            match self {
                Message::Quit => println!("  Quitting..."),
                Message::Move { x, y } => println!("  Moving to ({}, {})", x, y),
                Message::Write(text) => println!("  Writing: {}", text),
                Message::ChangeColor(r, g, b) => {
                    println!("  Changing color to RGB({}, {}, {})", r, g, b)
                }
            }
        }
    }

    msg1.call();
    msg2.call();
    msg3.call();
    msg4.call();

    // Option<T> is an enum!
    let some_number = Some(5);
    let no_number: Option<i32> = None;

    println!("Some number: {:?}", some_number);
    println!("No number: {:?}", no_number);

    // Result<T, E> is an enum!
    let success: Result<i32, String> = Ok(42);
    let failure: Result<i32, String> = Err(String::from("error"));

    println!("Success: {:?}", success);
    println!("Failure: {:?}", failure);

    println!();
}

/// Demonstrates pattern matching with match
fn pattern_matching() {
    println!("🎲 Pattern Matching");
    println!("-------------------");

    // Basic match
    let number = 7;

    match number {
        1 => println!("One!"),
        2 | 3 | 5 | 7 | 11 => println!("Prime!"),
        13..=19 => println!("Teen"),
        _ => println!("Other"),
    }

    // Match with enum
    #[derive(Debug)]
    enum Coin {
        Penny,
        Nickel,
        Dime,
        Quarter,
    }

    fn value_in_cents(coin: Coin) -> u8 {
        match coin {
            Coin::Penny => {
                println!("  Lucky penny!");
                1
            }
            Coin::Nickel => 5,
            Coin::Dime => 10,
            Coin::Quarter => 25,
        }
    }

    let coin = Coin::Quarter;
    let value = value_in_cents(coin);
    println!("Quarter = {}¢", value);

    // Match Option
    fn plus_one(x: Option<i32>) -> Option<i32> {
        match x {
            Some(i) => Some(i + 1),
            None => None,
        }
    }

    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);

    println!("Five: {:?}", five);
    println!("Six: {:?}", six);
    println!("None: {:?}", none);

    // Match Result
    fn divide(a: i32, b: i32) -> Result<i32, String> {
        if b == 0 {
            Err(String::from("Division by zero"))
        } else {
            Ok(a / b)
        }
    }

    match divide(10, 2) {
        Ok(result) => println!("10 / 2 = {}", result),
        Err(e) => println!("Error: {}", e),
    }

    match divide(10, 0) {
        Ok(result) => println!("10 / 0 = {}", result),
        Err(e) => println!("Error: {}", e),
    }

    // Match as expression
    let is_even = match number {
        n if n % 2 == 0 => true,
        _ => false,
    };
    println!("{} is even: {}", number, is_even);

    println!();
}

/// Demonstrates destructuring patterns
fn destructuring_patterns() {
    println!("🔍 Destructuring Patterns");
    println!("-------------------------");

    // Tuple destructuring
    let point = (3, 5);
    let (x, y) = point;
    println!("Point: ({}, {})", x, y);

    // Struct destructuring
    struct Point {
        x: i32,
        y: i32,
    }

    let p = Point { x: 0, y: 7 };

    // Full destructuring
    let Point { x, y } = p;
    println!("Point fields: x={}, y={}", x, y);

    // Renaming fields
    let Point { x: a, y: b } = p;
    println!("Renamed: a={}, b={}", a, b);

    // Partial destructuring
    let Point { x, .. } = p;
    println!("Only x: {}", x);

    // Destructuring in match
    match p {
        Point { x: 0, y } => println!("On y-axis at y={}", y),
        Point { x, y: 0 } => println!("On x-axis at x={}", x),
        Point { x, y } => println!("Neither axis: ({}, {})", x, y),
    }

    // Enum destructuring
    #[derive(Debug)]
    enum Message {
        Move { x: i32, y: i32 },
        Write(String),
        ChangeColor(u8, u8, u8),
    }

    let msg = Message::Move { x: 10, y: 20 };

    match msg {
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
        Message::Write(text) => println!("Write: {}", text),
        Message::ChangeColor(r, g, b) => println!("RGB({}, {}, {})", r, g, b),
    }

    // Nested destructuring
    let msg = Message::ChangeColor(255, 128, 0);
    match msg {
        Message::ChangeColor(r, g, b) if r > 200 => {
            println!("Bright red color: RGB({}, {}, {})", r, g, b)
        }
        Message::ChangeColor(r, g, b) => {
            println!("Normal color: RGB({}, {}, {})", r, g, b)
        }
        _ => println!("Other message"),
    }

    // Array destructuring
    let arr = [1, 2, 3, 4, 5];
    let [first, second, ..] = arr;
    println!("First two: {}, {}", first, second);

    println!();
}

/// Demonstrates match guards
fn match_guards() {
    println!("🛡️  Match Guards");
    println!("----------------");

    let num = Some(4);

    match num {
        Some(x) if x < 5 => println!("{} is less than 5", x),
        Some(x) if x >= 5 && x < 10 => println!("{} is between 5 and 9", x),
        Some(x) => println!("{} is 10 or more", x),
        None => println!("No number"),
    }

    // Multiple patterns with guard
    let x = 4;
    let y = false;

    match x {
        4 | 5 | 6 if y => println!("yes"),
        _ => println!("no"),
    }

    // Complex guard
    let point = (3, 4);

    match point {
        (x, y) if x == y => println!("On the diagonal"),
        (x, y) if x > y => println!("Above diagonal"),
        (x, y) if x < y => println!("Below diagonal"),
        _ => unreachable!(),
    }

    // Guard with enum
    #[derive(Debug)]
    enum Temperature {
        Celsius(i32),
        Fahrenheit(i32),
    }

    let temp = Temperature::Celsius(25);

    match temp {
        Temperature::Celsius(t) if t > 30 => println!("Hot: {}°C", t),
        Temperature::Celsius(t) if t < 10 => println!("Cold: {}°C", t),
        Temperature::Celsius(t) => println!("Comfortable: {}°C", t),
        Temperature::Fahrenheit(t) if t > 86 => println!("Hot: {}°F", t),
        Temperature::Fahrenheit(t) if t < 50 => println!("Cold: {}°F", t),
        Temperature::Fahrenheit(t) => println!("Comfortable: {}°F", t),
    }

    println!();
}

/// Demonstrates if let and while let
fn if_let_while_let() {
    println!("🔀 if let & while let");
    println!("---------------------");

    // if let - concise single pattern matching
    let some_value = Some(3);

    // Without if let (verbose)
    match some_value {
        Some(3) => println!("Three!"),
        _ => (),
    }

    // With if let (concise)
    if let Some(3) = some_value {
        println!("Three!");
    }

    // if let with else
    let number = Some(7);

    if let Some(n) = number {
        println!("Got number: {}", n);
    } else {
        println!("No number");
    }

    // if let with pattern
    #[derive(Debug)]
    enum Message {
        Move { x: i32, y: i32 },
        Write(String),
    }

    let msg = Message::Move { x: 10, y: 20 };

    if let Message::Move { x, y } = msg {
        println!("Move message: ({}, {})", x, y);
    }

    // while let - loop while pattern matches
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);

    println!("Popping from stack:");
    while let Some(top) = stack.pop() {
        println!("  {}", top);
    }

    // while let with condition
    let mut optional = Some(0);

    while let Some(i) = optional {
        if i > 5 {
            println!("Greater than 5, quit!");
            optional = None;
        } else {
            println!("  i = {}", i);
            optional = Some(i + 1);
        }
    }

    println!();
}

/// Demonstrates the newtype pattern
fn newtype_pattern() {
    println!("🎁 Newtype Pattern");
    println!("------------------");

    // Type safety with newtypes
    struct Meters(i32);
    struct Feet(i32);

    let distance_m = Meters(100);
    let distance_f = Feet(328);

    // These are different types!
    // let total = distance_m.0 + distance_f.0;  // Bug: mixing units

    println!("Distance: {}m", distance_m.0);
    println!("Distance: {}ft", distance_f.0);

    // Proper conversion
    fn meters_to_feet(meters: Meters) -> Feet {
        Feet((meters.0 as f64 * 3.28084) as i32)
    }

    let converted = meters_to_feet(Meters(100));
    println!("100m = {}ft", converted.0);

    // Wrapper type to implement external traits
    struct Wrapper(Vec<String>);

    impl Wrapper {
        fn new() -> Self {
            Wrapper(Vec::new())
        }

        fn add(&mut self, s: String) {
            self.0.push(s);
        }

        fn len(&self) -> usize {
            self.0.len()
        }
    }

    let mut wrapper = Wrapper::new();
    wrapper.add(String::from("hello"));
    wrapper.add(String::from("world"));
    println!("Wrapper length: {}", wrapper.len());

    // Type aliases (not newtypes)
    type Kilometers = i32;  // Just an alias, not a new type

    let x: i32 = 5;
    let y: Kilometers = 5;

    // These are the same type
    let total = x + y;
    println!("Total: {}", total);

    println!();
}

/// Real-world modeling examples
fn real_world_modeling() {
    println!("🌍 Real-World Modeling");
    println!("----------------------");

    // Example 1: Shape calculator
    #[derive(Debug)]
    enum Shape {
        Circle { radius: f64 },
        Rectangle { width: f64, height: f64 },
        Triangle { base: f64, height: f64 },
    }

    impl Shape {
        fn area(&self) -> f64 {
            match self {
                Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
                Shape::Rectangle { width, height } => width * height,
                Shape::Triangle { base, height } => 0.5 * base * height,
            }
        }
    }

    let circle = Shape::Circle { radius: 5.0 };
    let rectangle = Shape::Rectangle {
        width: 10.0,
        height: 20.0,
    };
    let triangle = Shape::Triangle {
        base: 8.0,
        height: 12.0,
    };

    println!("Circle area: {:.2}", circle.area());
    println!("Rectangle area: {:.2}", rectangle.area());
    println!("Triangle area: {:.2}", triangle.area());

    // Example 2: User account system
    #[derive(Debug)]
    enum AccountType {
        Free,
        Premium { expiry: String },
        Enterprise { seats: u32 },
    }

    #[derive(Debug)]
    struct User {
        username: String,
        email: String,
        account: AccountType,
    }

    impl User {
        fn describe(&self) -> String {
            match &self.account {
                AccountType::Free => format!("{} has a free account", self.username),
                AccountType::Premium { expiry } => {
                    format!("{} has premium until {}", self.username, expiry)
                }
                AccountType::Enterprise { seats } => {
                    format!("{} has enterprise with {} seats", self.username, seats)
                }
            }
        }
    }

    let user1 = User {
        username: String::from("alice"),
        email: String::from("alice@example.com"),
        account: AccountType::Free,
    };

    let user2 = User {
        username: String::from("bob"),
        email: String::from("bob@example.com"),
        account: AccountType::Premium {
            expiry: String::from("2024-12-31"),
        },
    };

    println!("{}", user1.describe());
    println!("{}", user2.describe());

    println!();
}

// Exercise Solutions (uncomment to test)

/*
/// Exercise 1: Rectangle calculator
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn new(width: u32, height: u32) -> Self {
        Rectangle { width, height }
    }

    fn square(size: u32) -> Self {
        Rectangle {
            width: size,
            height: size,
        }
    }

    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn perimeter(&self) -> u32 {
        2 * (self.width + self.height)
    }

    fn is_square(&self) -> bool {
        self.width == self.height
    }
}

/// Exercise 2: Traffic light
enum TrafficLight {
    Red,
    Yellow,
    Green,
}

impl TrafficLight {
    fn duration(&self) -> u32 {
        match self {
            TrafficLight::Red => 60,
            TrafficLight::Yellow => 5,
            TrafficLight::Green => 45,
        }
    }

    fn next(&self) -> TrafficLight {
        match self {
            TrafficLight::Red => TrafficLight::Green,
            TrafficLight::Yellow => TrafficLight::Red,
            TrafficLight::Green => TrafficLight::Yellow,
        }
    }
}

/// Exercise 3: Shape calculator
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { base: f64, height: f64 },
}

fn calculate_area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
        Shape::Rectangle { width, height } => width * height,
        Shape::Triangle { base, height } => 0.5 * base * height,
    }
}

/// Exercise 4: Option transformer
fn transform_option(opt: Option<i32>) -> Option<i32> {
    match opt {
        Some(n) if n % 2 == 0 => Some(n * 2),
        Some(_) => None,
        None => Some(0),
    }
}

/// Exercise 5: Message parser
enum Message {
    Text(String),
    Image { url: String, width: u32, height: u32 },
    Video { url: String, duration: u32 },
}

fn describe_message(msg: &Message) -> String {
    match msg {
        Message::Text(text) => format!("Text message: {}", text),
        Message::Image { url, width, height } => {
            format!("Image at {} ({}x{})", url, width, height)
        }
        Message::Video { url, duration } => {
            format!("Video at {} ({}s)", url, duration)
        }
    }
}
*/
