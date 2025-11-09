//! Project 10: Async Web Server with Tokio
//!
//! This project demonstrates asynchronous programming in Rust using Tokio,
//! including building a simple HTTP web server from scratch.

use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, RwLock, Semaphore};
use tokio::time::sleep;

use serde::{Deserialize, Serialize};

// =============================================================================
// SECTION 1: Basic Async/Await Concepts
// =============================================================================

/// A simple async function that sleeps and returns a value
async fn fetch_data(id: u32) -> String {
    println!("  [Task {}] Starting fetch...", id);

    // Simulate network I/O with async sleep
    sleep(Duration::from_millis(100)).await;

    println!("  [Task {}] Fetch complete!", id);
    format!("Data from task {}", id)
}

/// Demonstrates basic async/await
async fn basic_async_example() {
    println!("\n=== BASIC ASYNC/AWAIT ===");

    // Sequential execution
    println!("\nSequential execution:");
    let start = std::time::Instant::now();

    let data1 = fetch_data(1).await;
    let data2 = fetch_data(2).await;

    println!("Results: {}, {}", data1, data2);
    println!("Time taken: {:?}", start.elapsed());

    // Concurrent execution with join!
    println!("\nConcurrent execution with join!:");
    let start = std::time::Instant::now();

    let (data1, data2) = tokio::join!(fetch_data(3), fetch_data(4));

    println!("Results: {}, {}", data1, data2);
    println!("Time taken: {:?} (should be ~100ms, not ~200ms)", start.elapsed());
}

// =============================================================================
// SECTION 2: Task Spawning and Concurrency
// =============================================================================

/// Demonstrates spawning tasks
async fn task_spawning_example() {
    println!("\n=== TASK SPAWNING ===");

    let mut handles = vec![];

    // Spawn multiple tasks
    for i in 1..=5 {
        let handle = tokio::spawn(async move {
            sleep(Duration::from_millis(100)).await;
            println!("  Task {} complete", i);
            i * 2
        });
        handles.push(handle);
    }

    // Wait for all tasks to complete
    let results: Vec<i32> = futures::future::join_all(handles)
        .await
        .into_iter()
        .map(|r| r.unwrap())
        .collect();

    println!("Results: {:?}", results);
}

// =============================================================================
// SECTION 3: Select and Racing
// =============================================================================

async fn slow_operation() -> &'static str {
    sleep(Duration::from_secs(2)).await;
    "Slow result"
}

async fn fast_operation() -> &'static str {
    sleep(Duration::from_millis(100)).await;
    "Fast result"
}

/// Demonstrates using select! to race operations
async fn select_example() {
    println!("\n=== SELECT AND RACING ===");

    tokio::select! {
        result = slow_operation() => {
            println!("Slow operation won: {}", result);
        }
        result = fast_operation() => {
            println!("Fast operation won: {}", result);
        }
    }
}

// =============================================================================
// SECTION 4: Timeouts
// =============================================================================

async fn might_timeout() -> Result<String, tokio::time::error::Elapsed> {
    println!("\n=== TIMEOUTS ===");

    // This will timeout
    let result1 = tokio::time::timeout(Duration::from_millis(50), async {
        sleep(Duration::from_millis(200)).await;
        "Success"
    })
    .await;

    match result1 {
        Ok(val) => println!("Operation 1 completed: {}", val),
        Err(_) => println!("Operation 1 timed out!"),
    }

    // This won't timeout
    let result2 = tokio::time::timeout(Duration::from_millis(200), async {
        sleep(Duration::from_millis(50)).await;
        "Success"
    })
    .await;

    match result2 {
        Ok(val) => println!("Operation 2 completed: {}", val),
        Err(_) => println!("Operation 2 timed out!"),
    }

    result2
}

// =============================================================================
// SECTION 5: Channels for Communication
// =============================================================================

async fn channel_example() {
    println!("\n=== CHANNELS ===");

    let (tx, mut rx) = mpsc::channel(32);

    // Spawn producer tasks
    for i in 1..=5 {
        let tx_clone = tx.clone();
        tokio::spawn(async move {
            sleep(Duration::from_millis(50 * i)).await;
            tx_clone.send(format!("Message {}", i)).await.unwrap();
        });
    }

    // Drop original sender so receiver knows when to stop
    drop(tx);

    // Receive messages
    println!("Receiving messages:");
    while let Some(msg) = rx.recv().await {
        println!("  Received: {}", msg);
    }
}

// =============================================================================
// SECTION 6: Shared State
// =============================================================================

#[derive(Debug, Clone)]
struct AppState {
    request_count: Arc<RwLock<u64>>,
    visitors: Arc<RwLock<HashMap<String, u32>>>,
}

impl AppState {
    fn new() -> Self {
        Self {
            request_count: Arc::new(RwLock::new(0)),
            visitors: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    async fn increment_requests(&self) {
        let mut count = self.request_count.write().await;
        *count += 1;
    }

    async fn get_request_count(&self) -> u64 {
        *self.request_count.read().await
    }

    async fn increment_visitor(&self, ip: String) {
        let mut visitors = self.visitors.write().await;
        *visitors.entry(ip).or_insert(0) += 1;
    }

    async fn get_visitor_count(&self, ip: &str) -> u32 {
        let visitors = self.visitors.read().await;
        visitors.get(ip).copied().unwrap_or(0)
    }
}

async fn shared_state_example() {
    println!("\n=== SHARED STATE ===");

    let state = AppState::new();
    let mut handles = vec![];

    // Simulate concurrent requests
    for i in 0..10 {
        let state_clone = state.clone();
        let handle = tokio::spawn(async move {
            let ip = format!("192.168.1.{}", i % 3); // Simulate 3 different IPs
            state_clone.increment_requests().await;
            state_clone.increment_visitor(ip).await;
        });
        handles.push(handle);
    }

    // Wait for all tasks
    futures::future::join_all(handles).await;

    println!("Total requests: {}", state.get_request_count().await);
    println!(
        "Visitor 192.168.1.0: {} requests",
        state.get_visitor_count("192.168.1.0").await
    );
}

// =============================================================================
// SECTION 7: HTTP Server Implementation
// =============================================================================

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse {
    success: bool,
    message: String,
    data: Option<serde_json::Value>,
}

/// HTTP Request representation
#[derive(Debug)]
struct HttpRequest {
    method: String,
    path: String,
    _headers: HashMap<String, String>,
    body: String,
}

impl HttpRequest {
    async fn parse(stream: &mut TcpStream) -> std::io::Result<Self> {
        let mut buffer = vec![0u8; 4096];
        let n = stream.read(&mut buffer).await?;

        let request_str = String::from_utf8_lossy(&buffer[..n]);
        let lines: Vec<&str> = request_str.lines().collect();

        if lines.is_empty() {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "Empty request",
            ));
        }

        // Parse request line
        let parts: Vec<&str> = lines[0].split_whitespace().collect();
        let method = parts.get(0).unwrap_or(&"GET").to_string();
        let path = parts.get(1).unwrap_or(&"/").to_string();

        // Parse headers (simplified)
        let mut headers = HashMap::new();
        let mut i = 1;
        while i < lines.len() && !lines[i].is_empty() {
            if let Some(pos) = lines[i].find(':') {
                let key = lines[i][..pos].trim().to_string();
                let value = lines[i][pos + 1..].trim().to_string();
                headers.insert(key, value);
            }
            i += 1;
        }

        // Get body (everything after empty line)
        let body = if i + 1 < lines.len() {
            lines[i + 1..].join("\n")
        } else {
            String::new()
        };

        Ok(HttpRequest {
            method,
            path,
            _headers: headers,
            body,
        })
    }
}

/// HTTP Response builder
struct HttpResponse {
    status_code: u16,
    status_text: String,
    headers: Vec<(String, String)>,
    body: String,
}

impl HttpResponse {
    fn new(status_code: u16, body: String) -> Self {
        let status_text = match status_code {
            200 => "OK",
            404 => "Not Found",
            500 => "Internal Server Error",
            _ => "Unknown",
        }
        .to_string();

        Self {
            status_code,
            status_text,
            headers: vec![("Content-Type".to_string(), "text/plain".to_string())],
            body,
        }
    }

    fn json(status_code: u16, response: &ApiResponse) -> Self {
        let body = serde_json::to_string_pretty(response).unwrap();
        let mut resp = Self::new(status_code, body);
        resp.headers = vec![("Content-Type".to_string(), "application/json".to_string())];
        resp
    }

    fn to_bytes(&self) -> Vec<u8> {
        let mut response = format!(
            "HTTP/1.1 {} {}\r\n",
            self.status_code, self.status_text
        );

        for (key, value) in &self.headers {
            response.push_str(&format!("{}: {}\r\n", key, value));
        }

        response.push_str(&format!("Content-Length: {}\r\n", self.body.len()));
        response.push_str("\r\n");
        response.push_str(&self.body);

        response.into_bytes()
    }
}

/// Route handler
async fn handle_request(req: HttpRequest, state: AppState) -> HttpResponse {
    // Increment request counter
    state.increment_requests().await;

    match (req.method.as_str(), req.path.as_str()) {
        ("GET", "/") => {
            let count = state.get_request_count().await;
            HttpResponse::new(
                200,
                format!(
                    "Welcome to Async Web Server!\n\nTotal requests: {}\n",
                    count
                ),
            )
        }

        ("GET", "/api/stats") => {
            let count = state.get_request_count().await;
            let response = ApiResponse {
                success: true,
                message: "Statistics retrieved".to_string(),
                data: Some(serde_json::json!({
                    "total_requests": count,
                })),
            };
            HttpResponse::json(200, &response)
        }

        ("POST", "/api/echo") => {
            let response = ApiResponse {
                success: true,
                message: "Echo successful".to_string(),
                data: Some(serde_json::json!({
                    "received": req.body,
                })),
            };
            HttpResponse::json(200, &response)
        }

        ("GET", "/slow") => {
            // Simulate slow endpoint
            sleep(Duration::from_secs(2)).await;
            HttpResponse::new(200, "This was a slow response".to_string())
        }

        _ => HttpResponse::new(404, "Not Found\n".to_string()),
    }
}

/// Handle a single connection
async fn handle_connection(
    mut stream: TcpStream,
    state: AppState,
    _connection_id: u64,
) -> std::io::Result<()> {
    // Parse request
    let request = HttpRequest::parse(&mut stream).await?;

    println!(
        "Request: {} {} (body: {} bytes)",
        request.method,
        request.path,
        request.body.len()
    );

    // Handle request
    let response = handle_request(request, state).await;

    // Send response
    stream.write_all(&response.to_bytes()).await?;
    stream.flush().await?;

    Ok(())
}

/// Run the HTTP server
async fn run_server(
    addr: &str,
    state: AppState,
    shutdown: tokio::sync::watch::Receiver<bool>,
) -> std::io::Result<()> {
    println!("\n=== ASYNC HTTP SERVER ===");
    println!("Starting server on {}", addr);
    println!("\nAvailable endpoints:");
    println!("  GET  /              - Welcome page");
    println!("  GET  /api/stats     - Statistics (JSON)");
    println!("  POST /api/echo      - Echo request body (JSON)");
    println!("  GET  /slow          - Slow endpoint (2s delay)");
    println!("\nPress CTRL+C to stop\n");

    let listener = TcpListener::bind(addr).await?;

    // Limit concurrent connections
    let semaphore = Arc::new(Semaphore::new(100));
    let mut connection_id = 0u64;

    let mut shutdown = shutdown;

    loop {
        tokio::select! {
            accept_result = listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        connection_id += 1;
                        let current_id = connection_id;
                        let state_clone = state.clone();
                        let permit = semaphore.clone().acquire_owned().await.unwrap();

                        tokio::spawn(async move {
                            let _permit = permit; // Hold permit for duration of connection

                            if let Err(e) = handle_connection(stream, state_clone, current_id).await {
                                eprintln!("Error handling connection {}: {}", current_id, e);
                            }
                        });

                        println!("Connection {} from {}", current_id, addr);
                    }
                    Err(e) => {
                        eprintln!("Error accepting connection: {}", e);
                    }
                }
            }

            _ = shutdown.changed() => {
                if *shutdown.borrow() {
                    println!("\n🛑 Shutdown signal received, stopping server...");
                    break;
                }
            }
        }
    }

    println!("Server stopped gracefully");
    Ok(())
}

// =============================================================================
// SECTION 8: Graceful Shutdown
// =============================================================================

async fn graceful_shutdown_example() {
    let state = AppState::new();
    let (shutdown_tx, shutdown_rx) = tokio::sync::watch::channel(false);

    // Spawn server task
    let server_handle = tokio::spawn(async move {
        if let Err(e) = run_server("127.0.0.1:3000", state, shutdown_rx).await {
            eprintln!("Server error: {}", e);
        }
    });

    // Wait for CTRL+C
    tokio::signal::ctrl_c()
        .await
        .expect("Failed to listen for CTRL+C");

    // Signal shutdown
    shutdown_tx.send(true).unwrap();

    // Wait for server to finish
    let _ = server_handle.await;

    println!("Cleanup complete, goodbye!");
}

// =============================================================================
// SECTION 9: Bounded Concurrency
// =============================================================================

async fn process_item(id: usize) -> String {
    sleep(Duration::from_millis(100)).await;
    format!("Processed item {}", id)
}

async fn bounded_concurrency_example() {
    println!("\n=== BOUNDED CONCURRENCY ===");

    let items: Vec<usize> = (1..=20).collect();

    println!("Processing {} items with max 5 concurrent tasks", items.len());

    let start = std::time::Instant::now();

    // Process with bounded concurrency
    use futures::stream::{self, StreamExt};

    let results: Vec<String> = stream::iter(items)
        .map(|id| async move { process_item(id).await })
        .buffer_unordered(5) // At most 5 concurrent tasks
        .collect()
        .await;

    println!("Completed in {:?}", start.elapsed());
    println!("Results: {} items processed", results.len());
}

// =============================================================================
// SECTION 10: CPU-Bound Work in Async
// =============================================================================

fn cpu_intensive_work(n: u64) -> u64 {
    // Simulate CPU-bound work
    (1..=n).sum()
}

async fn cpu_bound_example() {
    println!("\n=== CPU-BOUND WORK ===");

    println!("Running CPU-intensive work in thread pool:");

    let handles: Vec<_> = (1..=5)
        .map(|i| {
            tokio::task::spawn_blocking(move || {
                println!("  Task {} starting CPU work", i);
                let result = cpu_intensive_work(10_000_000);
                println!("  Task {} complete: result = {}", i, result);
                result
            })
        })
        .collect();

    let results = futures::future::join_all(handles).await;
    println!("All CPU work complete");
    println!("Results: {:?}", results.iter().map(|r| r.as_ref().ok()).collect::<Vec<_>>());
}

// =============================================================================
// MAIN FUNCTION
// =============================================================================

#[tokio::main]
async fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║       Project 10: Async Web Server with Tokio             ║");
    println!("║                                                            ║");
    println!("║  Learn async/await, Futures, and build an HTTP server     ║");
    println!("╚════════════════════════════════════════════════════════════╝");

    // Check if we should run the server or examples
    let args: Vec<String> = std::env::args().collect();

    if args.len() > 1 && args[1] == "server" {
        // Run the web server
        graceful_shutdown_example().await;
    } else {
        // Run all examples
        basic_async_example().await;
        task_spawning_example().await;
        select_example().await;
        let _ = might_timeout().await;
        channel_example().await;
        shared_state_example().await;
        bounded_concurrency_example().await;
        cpu_bound_example().await;

        println!("\n╔════════════════════════════════════════════════════════════╗");
        println!("║                    Examples Complete!                      ║");
        println!("║                                                            ║");
        println!("║  To run the web server, use:                              ║");
        println!("║    cargo run server                                       ║");
        println!("║                                                            ║");
        println!("║  Then test with:                                          ║");
        println!("║    curl http://localhost:3000/                            ║");
        println!("║    curl http://localhost:3000/api/stats                   ║");
        println!("║    curl -X POST http://localhost:3000/api/echo -d 'test'  ║");
        println!("╚════════════════════════════════════════════════════════════╝");
    }
}

// =============================================================================
// TESTS
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_fetch_data() {
        let result = fetch_data(1).await;
        assert_eq!(result, "Data from task 1");
    }

    #[tokio::test]
    async fn test_shared_state() {
        let state = AppState::new();

        state.increment_requests().await;
        state.increment_requests().await;

        assert_eq!(state.get_request_count().await, 2);
    }

    #[tokio::test]
    async fn test_visitor_tracking() {
        let state = AppState::new();

        state.increment_visitor("127.0.0.1".to_string()).await;
        state.increment_visitor("127.0.0.1".to_string()).await;
        state.increment_visitor("192.168.1.1".to_string()).await;

        assert_eq!(state.get_visitor_count("127.0.0.1").await, 2);
        assert_eq!(state.get_visitor_count("192.168.1.1").await, 1);
    }

    #[tokio::test]
    async fn test_timeout() {
        let result = tokio::time::timeout(Duration::from_millis(10), async {
            sleep(Duration::from_millis(100)).await;
        })
        .await;

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_concurrent_execution() {
        let start = std::time::Instant::now();

        let (_r1, _r2) = tokio::join!(
            async {
                sleep(Duration::from_millis(100)).await;
            },
            async {
                sleep(Duration::from_millis(100)).await;
            }
        );

        let elapsed = start.elapsed();

        // Should take ~100ms, not ~200ms
        assert!(elapsed < Duration::from_millis(150));
    }
}
