/*
 * Example C code that can call Rust functions
 *
 * This demonstrates how to call Rust functions from C.
 * To use this, you would:
 * 1. Compile the Rust code as a library (staticlib or cdylib)
 * 2. Include the generated header (or declare functions manually)
 * 3. Link against the Rust library
 *
 * Build instructions:
 *
 * 1. First, modify Cargo.toml to include:
 *    [lib]
 *    crate-type = ["cdylib"]
 *
 * 2. Build the Rust library:
 *    cargo build --release
 *
 * 3. Compile this C file:
 *    gcc example.c -L./target/release -l<project_name> -o example
 *
 * 4. Run (on Linux, you may need to set LD_LIBRARY_PATH):
 *    ./example
 */

#include <stdio.h>
#include <stdint.h>

// Declare Rust functions
// These correspond to the #[no_mangle] pub extern "C" functions in Rust

extern int32_t rust_add(int32_t a, int32_t b);
extern void rust_greet(const char* name);

// C-compatible struct (must match Rust's #[repr(C)] Point)
typedef struct {
    double x;
    double y;
} Point;

extern double point_distance(Point p);

int main() {
    printf("=== Calling Rust from C ===\n\n");

    // Call Rust's add function
    int32_t sum = rust_add(15, 27);
    printf("rust_add(15, 27) = %d\n", sum);

    // Call Rust's greet function
    printf("\nCalling rust_greet:\n");
    rust_greet("C Programmer");

    // Call Rust function with struct
    Point p = { .x = 6.0, .y = 8.0 };
    double distance = point_distance(p);
    printf("\nDistance of point (6, 8): %.2f\n", distance);

    printf("\n✅ Successfully called Rust from C!\n");

    return 0;
}

/*
 * Expected output:
 *
 * === Calling Rust from C ===
 *
 * rust_add(15, 27) = 42
 *
 * Calling rust_greet:
 * Hello from Rust, C Programmer!
 *
 * Distance of point (6, 8): 10.00
 *
 * ✅ Successfully called Rust from C!
 */
