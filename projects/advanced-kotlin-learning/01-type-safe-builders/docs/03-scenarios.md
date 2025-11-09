# Scenarios: Type-Safe Builders

## Introduction

This document explores real-world scenarios, edge cases, common mistakes, and advanced patterns when working with type-safe builders. Each scenario includes both the problem and solution with detailed explanations.

## Table of Contents

1. [Real-World Scenarios](#real-world-scenarios)
2. [Edge Cases](#edge-cases)
3. [Common Mistakes & Debugging](#common-mistakes--debugging)
4. [Integration with Existing Codebases](#integration-with-existing-codebases)
5. [Testing Strategies](#testing-strategies)
6. [Nuanced Scenarios](#nuanced-scenarios)
7. [Advanced Scenarios](#advanced-scenarios)

---

## Real-World Scenarios

### Scenario 1: REST API Client DSL

**Use Case:** Building a fluent HTTP client for API testing

```kotlin
@DslMarker
annotation class HttpDslMarker

@HttpDslMarker
class HttpRequestBuilder {
    var method: String = "GET"
    var url: String = ""
    private val headers = mutableMapOf<String, String>()
    private val queryParams = mutableMapOf<String, String>()
    var body: Any? = null

    fun headers(init: HeadersBuilder.() -> Unit) {
        val builder = HeadersBuilder()
        builder.init()
        headers.putAll(builder.build())
    }

    fun queryParams(init: QueryParamsBuilder.() -> Unit) {
        val builder = QueryParamsBuilder()
        builder.init()
        queryParams.putAll(builder.build())
    }

    fun build(): HttpRequest = HttpRequest(method, url, headers, queryParams, body)
}

@HttpDslMarker
class HeadersBuilder {
    private val headers = mutableMapOf<String, String>()

    infix fun String.to(value: String) {
        headers[this] = value
    }

    fun build() = headers
}

@HttpDslMarker
class QueryParamsBuilder {
    private val params = mutableMapOf<String, String>()

    infix fun String.to(value: String) {
        params[this] = value
    }

    fun build() = params
}

// Top-level function
fun httpRequest(init: HttpRequestBuilder.() -> Unit): HttpRequest {
    val builder = HttpRequestBuilder()
    builder.init()
    return builder.build()
}

// Usage
val request = httpRequest {
    method = "POST"
    url = "https://api.example.com/users"

    headers {
        "Content-Type" to "application/json"
        "Authorization" to "Bearer token123"
    }

    queryParams {
        "page" to "1"
        "limit" to "10"
    }

    body = mapOf("name" to "John", "age" to 30)
}
```

**Why This Works:**
- Type-safe method selection
- Clear separation of concerns (headers, params, body)
- Intuitive API that reads like natural language
- @DslMarker prevents scope confusion

### Scenario 2: Database Migration DSL

**Use Case:** Creating database schema migrations with type safety

```kotlin
@DslMarker
annotation class MigrationDslMarker

@MigrationDslMarker
class MigrationBuilder(val version: Int) {
    private val operations = mutableListOf<Operation>()

    fun createTable(name: String, init: TableBuilder.() -> Unit) {
        val builder = TableBuilder(name)
        builder.init()
        operations.add(CreateTableOperation(builder.build()))
    }

    fun alterTable(name: String, init: AlterTableBuilder.() -> Unit) {
        val builder = AlterTableBuilder(name)
        builder.init()
        operations.add(AlterTableOperation(builder.build()))
    }

    fun dropTable(name: String) {
        operations.add(DropTableOperation(name))
    }

    fun build(): Migration = Migration(version, operations)
}

@MigrationDslMarker
class TableBuilder(private val name: String) {
    private val columns = mutableListOf<Column>()
    private val constraints = mutableListOf<Constraint>()

    fun column(name: String, type: ColumnType, init: ColumnBuilder.() -> Unit = {}) {
        val builder = ColumnBuilder(name, type)
        builder.init()
        columns.add(builder.build())
    }

    fun primaryKey(vararg columnNames: String) {
        constraints.add(PrimaryKeyConstraint(columnNames.toList()))
    }

    fun foreignKey(column: String, references: String, init: ForeignKeyBuilder.() -> Unit = {}) {
        val builder = ForeignKeyBuilder(column, references)
        builder.init()
        constraints.add(builder.build())
    }

    fun build(): Table = Table(name, columns, constraints)
}

@MigrationDslMarker
class ColumnBuilder(private val name: String, private val type: ColumnType) {
    var nullable: Boolean = true
    var defaultValue: Any? = null
    var unique: Boolean = false
    var autoIncrement: Boolean = false

    fun build(): Column = Column(name, type, nullable, defaultValue, unique, autoIncrement)
}

@MigrationDslMarker
class ForeignKeyBuilder(private val column: String, private val references: String) {
    var onDelete: ReferentialAction = ReferentialAction.NO_ACTION
    var onUpdate: ReferentialAction = ReferentialAction.NO_ACTION

    fun build(): ForeignKeyConstraint = ForeignKeyConstraint(column, references, onDelete, onUpdate)
}

enum class ColumnType {
    INT, VARCHAR, TEXT, BOOLEAN, TIMESTAMP, DECIMAL
}

enum class ReferentialAction {
    CASCADE, SET_NULL, NO_ACTION, RESTRICT
}

// Top-level function
fun migration(version: Int, init: MigrationBuilder.() -> Unit): Migration {
    val builder = MigrationBuilder(version)
    builder.init()
    return builder.build()
}

// Usage
val userTableMigration = migration(1) {
    createTable("users") {
        column("id", ColumnType.INT) {
            nullable = false
            autoIncrement = true
        }
        column("username", ColumnType.VARCHAR) {
            nullable = false
            unique = true
        }
        column("email", ColumnType.VARCHAR) {
            nullable = false
        }
        column("created_at", ColumnType.TIMESTAMP) {
            nullable = false
            defaultValue = "CURRENT_TIMESTAMP"
        }

        primaryKey("id")
    }

    createTable("posts") {
        column("id", ColumnType.INT) {
            nullable = false
            autoIncrement = true
        }
        column("user_id", ColumnType.INT) {
            nullable = false
        }
        column("title", ColumnType.VARCHAR)
        column("content", ColumnType.TEXT)

        primaryKey("id")
        foreignKey("user_id", "users.id") {
            onDelete = ReferentialAction.CASCADE
        }
    }
}
```

**Benefits:**
- Type-safe schema definition
- Prevents common migration errors
- Self-documenting code
- Easy to version control

### Scenario 3: Configuration Management DSL

**Use Case:** Application configuration with validation

```kotlin
@DslMarker
annotation class ConfigDslMarker

@ConfigDslMarker
class AppConfigBuilder {
    private var serverConfig: ServerConfig? = null
    private var databaseConfig: DatabaseConfig? = null
    private val features = mutableMapOf<String, Boolean>()

    fun server(init: ServerConfigBuilder.() -> Unit) {
        val builder = ServerConfigBuilder()
        builder.init()
        serverConfig = builder.build()
    }

    fun database(init: DatabaseConfigBuilder.() -> Unit) {
        val builder = DatabaseConfigBuilder()
        builder.init()
        databaseConfig = builder.build()
    }

    fun features(init: FeatureConfigBuilder.() -> Unit) {
        val builder = FeatureConfigBuilder()
        builder.init()
        features.putAll(builder.build())
    }

    fun build(): AppConfig {
        require(serverConfig != null) { "Server configuration is required" }
        require(databaseConfig != null) { "Database configuration is required" }
        return AppConfig(serverConfig!!, databaseConfig!!, features)
    }
}

@ConfigDslMarker
class ServerConfigBuilder {
    var host: String = "localhost"
    var port: Int = 8080
    var ssl: Boolean = false
    private var sslConfig: SslConfig? = null

    fun ssl(init: SslConfigBuilder.() -> Unit) {
        ssl = true
        val builder = SslConfigBuilder()
        builder.init()
        sslConfig = builder.build()
    }

    fun build(): ServerConfig {
        if (ssl) {
            require(sslConfig != null) { "SSL config required when SSL is enabled" }
        }
        return ServerConfig(host, port, ssl, sslConfig)
    }
}

@ConfigDslMarker
class DatabaseConfigBuilder {
    var driver: String = "postgresql"
    var host: String = "localhost"
    var port: Int = 5432
    var database: String = ""
    var username: String = ""
    var password: String = ""
    var maxPoolSize: Int = 10
    var minIdleConnections: Int = 2

    fun build(): DatabaseConfig {
        require(database.isNotBlank()) { "Database name is required" }
        require(username.isNotBlank()) { "Username is required" }
        return DatabaseConfig(driver, host, port, database, username, password, maxPoolSize, minIdleConnections)
    }
}

@ConfigDslMarker
class SslConfigBuilder {
    var keyStore: String = ""
    var keyStorePassword: String = ""
    var trustStore: String = ""

    fun build(): SslConfig {
        require(keyStore.isNotBlank()) { "KeyStore path is required" }
        return SslConfig(keyStore, keyStorePassword, trustStore)
    }
}

@ConfigDslMarker
class FeatureConfigBuilder {
    private val features = mutableMapOf<String, Boolean>()

    fun enable(vararg featureNames: String) {
        featureNames.forEach { features[it] = true }
    }

    fun disable(vararg featureNames: String) {
        featureNames.forEach { features[it] = false }
    }

    infix fun String.enabled(value: Boolean) {
        features[this] = value
    }

    fun build() = features
}

// Top-level function
fun appConfig(init: AppConfigBuilder.() -> Unit): AppConfig {
    val builder = AppConfigBuilder()
    builder.init()
    return builder.build()
}

// Usage
val config = appConfig {
    server {
        host = "api.example.com"
        port = 443
        ssl {
            keyStore = "/etc/ssl/keystore.jks"
            keyStorePassword = System.getenv("SSL_PASSWORD")
        }
    }

    database {
        driver = "postgresql"
        host = "db.example.com"
        port = 5432
        database = "myapp"
        username = "admin"
        password = System.getenv("DB_PASSWORD")
        maxPoolSize = 20
    }

    features {
        enable("analytics", "notifications")
        disable("beta_features")
        "experimental_ui" enabled false
    }
}
```

**Key Features:**
- Validation at build time
- Environment variable integration
- Hierarchical configuration
- Clear feature flags management

---

## Edge Cases

### Edge Case 1: Circular Dependencies in Builders

**Problem:** Builders reference each other in a circular manner

```kotlin
// ❌ PROBLEMATIC CODE
@DslMarker
annotation class GraphDslMarker

@GraphDslMarker
class NodeBuilder(val id: String) {
    private val edges = mutableListOf<Edge>()

    fun connectTo(targetId: String, init: NodeBuilder.() -> Unit) {
        // This creates circular dependency!
        val targetBuilder = NodeBuilder(targetId)
        targetBuilder.init()
        edges.add(Edge(id, targetId))
    }
}
```

**Solution:** Use deferred resolution pattern

```kotlin
@DslMarker
annotation class GraphDslMarker

@GraphDslMarker
class GraphBuilder {
    private val nodes = mutableMapOf<String, NodeData>()
    private val edges = mutableListOf<EdgeSpec>()

    fun node(id: String, init: NodeBuilder.() -> Unit = {}) {
        val builder = NodeBuilder(id, this)
        builder.init()
        nodes[id] = builder.buildData()
    }

    internal fun addEdge(from: String, to: String, weight: Double) {
        edges.add(EdgeSpec(from, to, weight))
    }

    fun build(): Graph {
        // Validate all edges reference existing nodes
        edges.forEach { edge ->
            require(edge.from in nodes) { "Node ${edge.from} not found" }
            require(edge.to in nodes) { "Node ${edge.to} not found" }
        }
        return Graph(nodes, edges.map { Edge(it.from, it.to, it.weight) })
    }
}

@GraphDslMarker
class NodeBuilder(
    private val id: String,
    private val graphBuilder: GraphBuilder
) {
    var label: String = id
    var data: Map<String, Any> = emptyMap()

    fun connectTo(targetId: String, weight: Double = 1.0) {
        // Defer edge creation to graph builder
        graphBuilder.addEdge(id, targetId, weight)
    }

    fun buildData(): NodeData = NodeData(id, label, data)
}

data class NodeData(val id: String, val label: String, val data: Map<String, Any>)
data class EdgeSpec(val from: String, val to: String, val weight: Double)
data class Edge(val from: String, val to: String, val weight: Double)
data class Graph(val nodes: Map<String, NodeData>, val edges: List<Edge>)

fun graph(init: GraphBuilder.() -> Unit): Graph {
    val builder = GraphBuilder()
    builder.init()
    return builder.build()
}

// Usage
val socialGraph = graph {
    node("alice") {
        label = "Alice Smith"
        connectTo("bob")
        connectTo("charlie")
    }

    node("bob") {
        label = "Bob Jones"
        connectTo("alice")  // Bidirectional edge
    }

    node("charlie") {
        label = "Charlie Brown"
    }
}
```

**Key Points:**
- Use deferred resolution for cross-references
- Validate references at build time
- Keep builder reference to parent context when needed

### Edge Case 2: Dynamic Property Names

**Problem:** Need to support dynamic keys in builder

```kotlin
// ❌ Limited approach
@ConfigDslMarker
class ConfigBuilder {
    var host: String = ""
    var port: Int = 0
    // What if we need arbitrary properties?
}
```

**Solution:** Combine typed properties with dynamic map

```kotlin
@DslMarker
annotation class ConfigDslMarker

@ConfigDslMarker
class ConfigBuilder {
    // Typed properties for common use cases
    var host: String = "localhost"
    var port: Int = 8080

    // Dynamic properties
    private val customProperties = mutableMapOf<String, Any>()

    // Extension function for dynamic properties
    infix fun String.set(value: Any) {
        customProperties[this] = value
    }

    operator fun set(key: String, value: Any) {
        customProperties[key] = value
    }

    fun getCustomProperty(key: String): Any? = customProperties[key]

    fun build(): Config = Config(host, port, customProperties.toMap())
}

data class Config(
    val host: String,
    val port: Int,
    val customProperties: Map<String, Any>
)

fun config(init: ConfigBuilder.() -> Unit): Config {
    val builder = ConfigBuilder()
    builder.init()
    return builder.build()
}

// Usage
val serverConfig = config {
    host = "api.example.com"
    port = 443

    // Dynamic properties
    "ssl.enabled" set true
    "ssl.protocol" set "TLS"
    "custom.feature.xyz" set mapOf("enabled" to true, "value" to 42)

    // Alternative syntax
    this["cache.ttl"] = 3600
}
```

### Edge Case 3: Optional vs Required Properties

**Problem:** How to enforce required properties at compile time?

**Solution 1: Using sealed classes and state machine**

```kotlin
@DslMarker
annotation class UserDslMarker

// State tracking with sealed classes
sealed class UserBuilderState

class RequiresUsername : UserBuilderState()
class RequiresEmail(val username: String) : UserBuilderState()
class Complete(val username: String, val email: String) : UserBuilderState()

// Type-safe builder with state transitions
@UserDslMarker
class UserBuilder<S : UserBuilderState> private constructor(
    private val state: S
) {
    companion object {
        fun create(): UserBuilder<RequiresUsername> = UserBuilder(RequiresUsername())
    }

    fun username(value: String): UserBuilder<RequiresEmail> {
        require(state is RequiresUsername) { "Username already set" }
        return UserBuilder(RequiresEmail(value))
    }

    fun email(value: String): UserBuilder<Complete> {
        require(state is RequiresEmail) { "Email can only be set after username" }
        return UserBuilder(Complete(state.username, value))
    }

    // Only available when all required fields are set
    fun build(): User {
        require(state is Complete) { "Cannot build: missing required fields" }
        return User(state.username, state.email)
    }
}

data class User(val username: String, val email: String)

// Usage
val user = UserBuilder.create()
    .username("john_doe")
    .email("john@example.com")
    .build()

// This won't compile:
// val incomplete = UserBuilder.create().build()  // ❌ Missing required fields
```

**Solution 2: Using builder validation**

```kotlin
@DslMarker
annotation class FormDslMarker

@FormDslMarker
class FormBuilder {
    private var title: String? = null
    private var description: String? = null
    private val fields = mutableListOf<FormField>()

    // Required field
    fun title(value: String) {
        title = value
    }

    // Optional field
    fun description(value: String) {
        description = value
    }

    fun field(name: String, init: FormFieldBuilder.() -> Unit) {
        val builder = FormFieldBuilder(name)
        builder.init()
        fields.add(builder.build())
    }

    fun build(): Form {
        // Validate required fields
        val titleValue = requireNotNull(title) { "Title is required" }
        require(fields.isNotEmpty()) { "At least one field is required" }

        return Form(titleValue, description, fields)
    }
}

@FormDslMarker
class FormFieldBuilder(private val name: String) {
    private var type: FieldType? = null
    var label: String = name.capitalize()
    var required: Boolean = false
    var defaultValue: String? = null
    private val validators = mutableListOf<Validator>()

    fun type(value: FieldType) {
        type = value
    }

    fun validate(validator: Validator) {
        validators.add(validator)
    }

    fun build(): FormField {
        val typeValue = requireNotNull(type) { "Field type is required for field: $name" }
        return FormField(name, typeValue, label, required, defaultValue, validators)
    }
}

enum class FieldType {
    TEXT, EMAIL, NUMBER, DATE, CHECKBOX
}

interface Validator {
    fun validate(value: String): Boolean
}

data class FormField(
    val name: String,
    val type: FieldType,
    val label: String,
    val required: Boolean,
    val defaultValue: String?,
    val validators: List<Validator>
)

data class Form(
    val title: String,
    val description: String?,
    val fields: List<FormField>
)

fun form(init: FormBuilder.() -> Unit): Form {
    val builder = FormBuilder()
    builder.init()
    return builder.build()
}

// Usage
val contactForm = form {
    title("Contact Us")
    description("Get in touch with our team")

    field("name") {
        type(FieldType.TEXT)
        required = true
    }

    field("email") {
        type(FieldType.EMAIL)
        label = "Email Address"
        required = true
    }

    field("message") {
        type(FieldType.TEXT)
        required = true
    }
}

// This will throw at runtime:
// val invalid = form { }  // ❌ Missing required title
```

---

## Common Mistakes & Debugging

### Mistake 1: Forgetting @DslMarker

**Problem:**

```kotlin
// ❌ WITHOUT @DslMarker
class HTML {
    fun body(init: Body.() -> Unit) {
        Body().init()
    }
}

class Body {
    fun div(init: Div.() -> Unit) {
        Div().init()
    }
}

class Div {
    fun p(text: String) {}
}

// This compiles but is confusing:
HTML().body {
    div {
        body {  // ❌ Shouldn't be able to nest body in div!
            div {
                // Infinite nesting possible
            }
        }
    }
}
```

**Solution:**

```kotlin
// ✅ WITH @DslMarker
@DslMarker
annotation class HtmlTagMarker

@HtmlTagMarker
class HTML {
    fun body(init: Body.() -> Unit) {
        Body().init()
    }
}

@HtmlTagMarker
class Body {
    fun div(init: Div.() -> Unit) {
        Div().init()
    }
}

@HtmlTagMarker
class Div {
    fun p(text: String) {}
}

// Now this won't compile:
HTML().body {
    div {
        // body { }  // ❌ Compilation error: can't access outer scope
    }
}
```

**Debug Tip:** If you can access outer scopes unexpectedly, check if all builder classes have the same @DslMarker annotation.

### Mistake 2: Mutable State Exposure

**Problem:**

```kotlin
// ❌ EXPOSING MUTABLE STATE
class ListBuilder {
    val items = mutableListOf<String>()  // Public mutable list!

    fun item(value: String) {
        items.add(value)
    }

    fun build(): List<String> = items
}

// Usage can modify internal state:
val builder = ListBuilder()
builder.item("A")
builder.items.add("B")  // ❌ Direct modification!
builder.items.clear()   // ❌ Breaks encapsulation!
```

**Solution:**

```kotlin
// ✅ PROPER ENCAPSULATION
class ListBuilder {
    private val items = mutableListOf<String>()  // Private

    fun item(value: String) {
        items.add(value)
    }

    // Return immutable copy
    fun build(): List<String> = items.toList()
}

// Can only modify through DSL:
val builder = ListBuilder()
builder.item("A")
// builder.items  // ❌ Not accessible
```

**Debug Tip:** Always make builder internal state `private` and return immutable copies.

### Mistake 3: Not Validating Builder State

**Problem:**

```kotlin
// ❌ NO VALIDATION
class EmailBuilder {
    var to: String = ""
    var subject: String = ""
    var body: String = ""

    fun build(): Email = Email(to, subject, body)
}

// Can create invalid emails:
val invalid = email {
    // Oops, forgot to set 'to'
    subject = "Hello"
}  // Creates email with empty 'to'!
```

**Solution:**

```kotlin
// ✅ WITH VALIDATION
class EmailBuilder {
    var to: String = ""
    var subject: String = ""
    var body: String = ""

    fun build(): Email {
        require(to.isNotBlank()) { "Email 'to' field is required" }
        require(to.matches(Regex(".+@.+\\..+"))) { "Invalid email format: $to" }
        require(subject.isNotBlank()) { "Email subject is required" }

        return Email(to, subject, body)
    }
}

data class Email(val to: String, val subject: String, val body: String)

fun email(init: EmailBuilder.() -> Unit): Email {
    val builder = EmailBuilder()
    builder.init()
    return builder.build()
}

// Now this throws clear error:
try {
    email {
        subject = "Hello"
        // Missing 'to'
    }
} catch (e: IllegalArgumentException) {
    println(e.message)  // "Email 'to' field is required"
}
```

**Debug Tip:** Add validation in `build()` method, use `require()` for clear error messages.

### Mistake 4: Incorrect Receiver Types

**Problem:**

```kotlin
// ❌ WRONG RECEIVER TYPE
class TableBuilder {
    fun row(init: RowBuilder.() -> Unit) {
        RowBuilder().init()
    }
}

class RowBuilder {
    // Wrong: String receiver instead of CellBuilder
    fun cell(init: String.() -> Unit) {
        "".init()  // What does this even do?
    }
}
```

**Solution:**

```kotlin
// ✅ CORRECT RECEIVER TYPE
class TableBuilder {
    private val rows = mutableListOf<Row>()

    fun row(init: RowBuilder.() -> Unit) {
        val builder = RowBuilder()
        builder.init()
        rows.add(builder.build())
    }

    fun build(): Table = Table(rows)
}

class RowBuilder {
    private val cells = mutableListOf<Cell>()

    fun cell(init: CellBuilder.() -> Unit) {
        val builder = CellBuilder()
        builder.init()
        cells.add(builder.build())
    }

    fun build(): Row = Row(cells)
}

class CellBuilder {
    var content: String = ""
    var colspan: Int = 1
    var rowspan: Int = 1

    fun build(): Cell = Cell(content, colspan, rowspan)
}
```

**Debug Tip:** Each builder should have its own dedicated builder class as receiver type.

### Mistake 5: Thread Safety Issues

**Problem:**

```kotlin
// ❌ NOT THREAD-SAFE
class SharedBuilder {
    private val items = mutableListOf<String>()

    fun item(value: String) {
        items.add(value)  // Not thread-safe!
    }

    fun build(): List<String> = items.toList()
}

// Can cause issues with concurrent access:
val builder = SharedBuilder()
(1..1000).toList().parallelStream().forEach {
    builder.item("Item $it")  // Race condition!
}
```

**Solution:**

```kotlin
// ✅ THREAD-SAFE OPTIONS

// Option 1: Synchronization
class SynchronizedBuilder {
    private val items = mutableListOf<String>()
    private val lock = Any()

    fun item(value: String) {
        synchronized(lock) {
            items.add(value)
        }
    }

    fun build(): List<String> = synchronized(lock) {
        items.toList()
    }
}

// Option 2: Thread-safe collections
import java.util.concurrent.CopyOnWriteArrayList

class ThreadSafeBuilder {
    private val items = CopyOnWriteArrayList<String>()

    fun item(value: String) {
        items.add(value)
    }

    fun build(): List<String> = items.toList()
}

// Option 3: Immutable builder (best for DSL)
class ImmutableBuilder private constructor(
    private val items: List<String>
) {
    constructor() : this(emptyList())

    fun item(value: String): ImmutableBuilder {
        return ImmutableBuilder(items + value)
    }

    fun build(): List<String> = items
}
```

**Debug Tip:** If builder will be used concurrently, document thread-safety guarantees clearly.

---

## Integration with Existing Codebases

### Integration Pattern 1: Wrapping Existing APIs

**Scenario:** You have an existing complex API and want to add a DSL layer

```kotlin
// Existing API (can't modify)
class LegacyHttpClient {
    fun execute(request: HttpRequest): HttpResponse {
        // Complex logic
        return HttpResponse()
    }
}

data class HttpRequest(
    val method: String,
    val url: String,
    val headers: Map<String, String>,
    val body: String?
)

data class HttpResponse(val status: Int = 200, val body: String = "")

// Create DSL wrapper
@DslMarker
annotation class HttpClientDslMarker

@HttpClientDslMarker
class HttpClientDsl(private val client: LegacyHttpClient) {

    fun get(url: String, init: RequestBuilder.() -> Unit = {}): HttpResponse {
        return request("GET", url, init)
    }

    fun post(url: String, init: RequestBuilder.() -> Unit = {}): HttpResponse {
        return request("POST", url, init)
    }

    private fun request(method: String, url: String, init: RequestBuilder.() -> Unit): HttpResponse {
        val builder = RequestBuilder(method, url)
        builder.init()
        val request = builder.build()
        return client.execute(request)
    }
}

@HttpClientDslMarker
class RequestBuilder(
    private val method: String,
    private val url: String
) {
    private val headers = mutableMapOf<String, String>()
    var body: String? = null

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun headers(init: HeadersBuilder.() -> Unit) {
        val builder = HeadersBuilder()
        builder.init()
        headers.putAll(builder.build())
    }

    fun build(): HttpRequest = HttpRequest(method, url, headers, body)
}

@HttpClientDslMarker
class HeadersBuilder {
    private val headers = mutableMapOf<String, String>()

    infix fun String.to(value: String) {
        headers[this] = value
    }

    fun build() = headers
}

// Extension function for easy access
fun LegacyHttpClient.dsl(init: HttpClientDsl.() -> Unit) {
    val dsl = HttpClientDsl(this)
    dsl.init()
}

// Usage - wraps legacy API with DSL
val client = LegacyHttpClient()

val response = client.dsl {
    post("https://api.example.com/users") {
        headers {
            "Content-Type" to "application/json"
            "Authorization" to "Bearer token"
        }
        body = """{"name": "John"}"""
    }
}
```

### Integration Pattern 2: Builder Adapter Pattern

**Scenario:** Convert between DSL and existing builder patterns

```kotlin
// Existing Java-style builder
class DatabaseConfig private constructor(
    val host: String,
    val port: Int,
    val database: String
) {
    class Builder {
        private var host: String = "localhost"
        private var port: Int = 5432
        private var database: String = ""

        fun host(value: String) = apply { host = value }
        fun port(value: Int) = apply { port = value }
        fun database(value: String) = apply { database = value }
        fun build() = DatabaseConfig(host, port, database)
    }
}

// Create DSL adapter
@DslMarker
annotation class DatabaseDslMarker

@DatabaseDslMarker
class DatabaseConfigDsl {
    var host: String = "localhost"
    var port: Int = 5432
    var database: String = ""

    fun build(): DatabaseConfig {
        return DatabaseConfig.Builder()
            .host(host)
            .port(port)
            .database(database)
            .build()
    }
}

fun databaseConfig(init: DatabaseConfigDsl.() -> Unit): DatabaseConfig {
    val dsl = DatabaseConfigDsl()
    dsl.init()
    return dsl.build()
}

// Usage - both styles work
val config1 = DatabaseConfig.Builder()  // Old style
    .host("db.example.com")
    .port(5432)
    .database("myapp")
    .build()

val config2 = databaseConfig {  // New DSL style
    host = "db.example.com"
    port = 5432
    database = "myapp"
}
```

### Integration Pattern 3: Gradual Migration

**Scenario:** Migrate existing code to DSL gradually

```kotlin
// Phase 1: Support both old and new API
class ReportGenerator {
    // Old API (deprecated but still works)
    @Deprecated("Use DSL builder instead", ReplaceWith("report { ... }"))
    fun generateReport(
        title: String,
        filters: Map<String, Any>,
        columns: List<String>
    ): Report {
        return Report(title, filters, columns)
    }

    // New DSL API
    fun report(init: ReportBuilder.() -> Unit): Report {
        val builder = ReportBuilder()
        builder.init()
        return builder.build()
    }
}

@DslMarker
annotation class ReportDslMarker

@ReportDslMarker
class ReportBuilder {
    var title: String = ""
    private val filters = mutableMapOf<String, Any>()
    private val columns = mutableListOf<String>()

    fun filter(name: String, value: Any) {
        filters[name] = value
    }

    fun column(name: String) {
        columns.add(name)
    }

    fun build(): Report = Report(title, filters, columns)
}

data class Report(
    val title: String,
    val filters: Map<String, Any>,
    val columns: List<String>
)

// Migration helper: convert old calls to new
fun ReportGenerator.reportFromLegacy(
    title: String,
    filters: Map<String, Any>,
    columns: List<String>
): Report = report {
    this.title = title
    filters.forEach { (name, value) -> filter(name, value) }
    columns.forEach { column(it) }
}
```

---

## Testing Strategies

### Strategy 1: Testing DSL Construction

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class HtmlDslTest {

    @Test
    fun `should build simple HTML structure`() {
        val result = html {
            body {
                div {
                    p("Hello World")
                }
            }
        }

        val html = result.render()
        assertTrue(html.contains("<body>"))
        assertTrue(html.contains("<div>"))
        assertTrue(html.contains("<p>Hello World</p>"))
    }

    @Test
    fun `should handle nested elements correctly`() {
        val result = html {
            body {
                div {
                    p("First")
                }
                div {
                    p("Second")
                }
            }
        }

        val html = result.render()
        val firstIndex = html.indexOf("First")
        val secondIndex = html.indexOf("Second")
        assertTrue(firstIndex < secondIndex)
    }

    @Test
    fun `should validate required fields`() {
        val exception = assertThrows<IllegalArgumentException> {
            form {
                // Missing required title
                field("name") {
                    type(FieldType.TEXT)
                }
            }
        }
        assertEquals("Title is required", exception.message)
    }

    @Test
    fun `should support attributes`() {
        val result = html {
            body {
                div {
                    id = "main"
                    className = "container"
                    p("Content")
                }
            }
        }

        val html = result.render()
        assertTrue(html.contains("""id="main""""))
        assertTrue(html.contains("""class="container""""))
    }
}
```

### Strategy 2: Testing Builder State

```kotlin
class BuilderStateTest {

    @Test
    fun `should accumulate items correctly`() {
        val builder = ListBuilder()

        builder.item("A")
        builder.item("B")
        builder.item("C")

        val result = builder.build()
        assertEquals(listOf("A", "B", "C"), result)
    }

    @Test
    fun `should not allow modification after build`() {
        val builder = ListBuilder()
        builder.item("A")

        val result1 = builder.build()
        builder.item("B")
        val result2 = builder.build()

        // First build should be immutable
        assertEquals(listOf("A"), result1)
        assertEquals(listOf("A", "B"), result2)
    }

    @Test
    fun `should handle empty builder`() {
        val builder = ListBuilder()
        val result = builder.build()

        assertTrue(result.isEmpty())
    }
}
```

### Strategy 3: Testing DSL Scope Control

```kotlin
class DslMarkerTest {

    @Test
    fun `should prevent accessing outer scope with DslMarker`() {
        // This test verifies compile-time behavior
        // If it compiles, the test passes

        html {
            body {
                div {
                    // Can only access Div members
                    p("text")

                    // These should not compile (verified manually):
                    // body { }   // ❌
                    // html { }   // ❌
                }
            }
        }
    }
}
```

### Strategy 4: Property-Based Testing

```kotlin
import io.kotest.property.Arb
import io.kotest.property.arbitrary.int
import io.kotest.property.arbitrary.string
import io.kotest.property.checkAll
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test

class PropertyBasedDslTest {

    @Test
    fun `should handle arbitrary string content`() = runBlocking {
        checkAll<String> { content ->
            val result = html {
                body {
                    p(content)
                }
            }

            val rendered = result.render()
            assertTrue(rendered.contains(content))
        }
    }

    @Test
    fun `should handle arbitrary number of elements`() = runBlocking {
        checkAll(Arb.int(0..100)) { count ->
            val result = html {
                body {
                    repeat(count) {
                        div {
                            p("Item $it")
                        }
                    }
                }
            }

            val rendered = result.render()
            val divCount = rendered.split("<div>").size - 1
            assertEquals(count, divCount)
        }
    }
}
```

### Strategy 5: Integration Testing

```kotlin
class HttpDslIntegrationTest {

    private lateinit var mockServer: MockWebServer

    @BeforeEach
    fun setup() {
        mockServer = MockWebServer()
        mockServer.start()
    }

    @AfterEach
    fun teardown() {
        mockServer.shutdown()
    }

    @Test
    fun `should execute HTTP request with DSL`() {
        // Setup mock response
        mockServer.enqueue(MockResponse().setBody("""{"status":"ok"}"""))

        val client = HttpClient()

        val response = client.request {
            method = "POST"
            url = mockServer.url("/api/test").toString()

            headers {
                "Content-Type" to "application/json"
                "Accept" to "application/json"
            }

            body = """{"test": true}"""
        }

        // Verify request
        val request = mockServer.takeRequest()
        assertEquals("POST", request.method)
        assertEquals("/api/test", request.path)
        assertEquals("application/json", request.getHeader("Content-Type"))
        assertTrue(request.body.readUtf8().contains(""""test": true"""))

        // Verify response
        assertTrue(response.body.contains("ok"))
    }
}
```

---

## Nuanced Scenarios

### Scenario 1: Handling Validation in Builders

**Challenge:** When and how to validate builder state

```kotlin
@DslMarker
annotation class ValidationDslMarker

// Approach 1: Validation at Build Time
@ValidationDslMarker
class BuildTimeValidationBuilder {
    private var email: String? = null
    private var age: Int? = null

    fun email(value: String) {
        email = value
    }

    fun age(value: Int) {
        age = value
    }

    fun build(): User {
        // Validation happens here
        val emailValue = requireNotNull(email) { "Email is required" }
        require(emailValue.matches(Regex(".+@.+\\..+"))) { "Invalid email format" }

        val ageValue = requireNotNull(age) { "Age is required" }
        require(ageValue >= 0) { "Age must be non-negative" }
        require(ageValue < 150) { "Age must be realistic" }

        return User(emailValue, ageValue)
    }
}

// Approach 2: Validation at Set Time (fail-fast)
@ValidationDslMarker
class SetTimeValidationBuilder {
    private var email: String? = null
    private var age: Int? = null

    fun email(value: String) {
        // Validate immediately
        require(value.matches(Regex(".+@.+\\..+"))) { "Invalid email format: $value" }
        email = value
    }

    fun age(value: Int) {
        // Validate immediately
        require(value >= 0) { "Age must be non-negative: $value" }
        require(value < 150) { "Age must be realistic: $value" }
        age = value
    }

    fun build(): User {
        val emailValue = requireNotNull(email) { "Email is required" }
        val ageValue = requireNotNull(age) { "Age is required" }
        return User(emailValue, ageValue)
    }
}

// Approach 3: Accumulate Validation Errors
@ValidationDslMarker
class AccumulatingValidationBuilder {
    private var email: String? = null
    private var age: Int? = null
    private val errors = mutableListOf<String>()

    fun email(value: String) {
        email = value
        if (!value.matches(Regex(".+@.+\\..+"))) {
            errors.add("Invalid email format: $value")
        }
    }

    fun age(value: Int) {
        age = value
        if (value < 0) {
            errors.add("Age must be non-negative: $value")
        }
        if (value >= 150) {
            errors.add("Age must be realistic: $value")
        }
    }

    fun build(): User {
        if (email == null) errors.add("Email is required")
        if (age == null) errors.add("Age is required")

        if (errors.isNotEmpty()) {
            throw ValidationException(errors)
        }

        return User(email!!, age!!)
    }
}

class ValidationException(val errors: List<String>) :
    Exception("Validation failed:\n${errors.joinToString("\n")}")

data class User(val email: String, val age: Int)

// Usage comparison
fun demonstrateValidation() {
    // Build-time validation
    try {
        user1 {
            email = "invalid"
            age = -5
        }  // Fails at build()
    } catch (e: IllegalArgumentException) {
        println("Build-time: ${e.message}")  // Shows first error only
    }

    // Set-time validation
    try {
        user2 {
            email = "invalid"  // Fails immediately
            age = -5
        }
    } catch (e: IllegalArgumentException) {
        println("Set-time: ${e.message}")  // Fails at first invalid set
    }

    // Accumulating validation
    try {
        user3 {
            email = "invalid"
            age = -5
        }  // Accumulates all errors
    } catch (e: ValidationException) {
        println("Accumulated errors:")
        e.errors.forEach { println("  - $it") }  // Shows all errors
    }
}
```

**Best Practices:**
- Use build-time validation for required fields
- Use set-time validation for format/range validation
- Use accumulating validation for forms with multiple fields

### Scenario 2: Error Reporting in DSLs

**Challenge:** Provide clear error messages in nested DSL contexts

```kotlin
@DslMarker
annotation class ErrorReportingDslMarker

@ErrorReportingDslMarker
class ConfigurationBuilder(private val path: String = "root") {
    private val sections = mutableListOf<Section>()

    fun section(name: String, init: SectionBuilder.() -> Unit) {
        try {
            val builder = SectionBuilder("$path.$name")
            builder.init()
            sections.add(builder.build())
        } catch (e: Exception) {
            throw ConfigurationException("Error in section '$path.$name'", e)
        }
    }

    fun build(): Configuration {
        if (sections.isEmpty()) {
            throw ConfigurationException("Configuration at '$path' has no sections")
        }
        return Configuration(sections)
    }
}

@ErrorReportingDslMarker
class SectionBuilder(private val path: String) {
    private val properties = mutableMapOf<String, Any>()

    fun property(name: String, value: Any) {
        try {
            validateProperty(name, value)
            properties[name] = value
        } catch (e: Exception) {
            throw ConfigurationException("Error setting property '$path.$name'", e)
        }
    }

    private fun validateProperty(name: String, value: Any) {
        when {
            name.isBlank() -> throw IllegalArgumentException("Property name cannot be blank")
            value is String && value.isBlank() ->
                throw IllegalArgumentException("String value cannot be blank")
        }
    }

    fun build(): Section = Section(path, properties)
}

class ConfigurationException(message: String, cause: Exception? = null) :
    Exception(message, cause)

data class Section(val path: String, val properties: Map<String, Any>)
data class Configuration(val sections: List<Section>)

fun configuration(init: ConfigurationBuilder.() -> Unit): Configuration {
    val builder = ConfigurationBuilder()
    builder.init()
    return builder.build()
}

// Usage with clear error reporting
fun demonstrateErrorReporting() {
    try {
        configuration {
            section("database") {
                property("host", "localhost")
                property("", "value")  // Error: blank property name
            }
        }
    } catch (e: ConfigurationException) {
        // Clear error path:
        // "Error setting property 'root.database.': Property name cannot be blank"
        println(e.message)

        // Can trace back through nested contexts
        var cause: Throwable? = e
        while (cause != null) {
            println("  Caused by: ${cause.message}")
            cause = cause.cause
        }
    }
}
```

### Scenario 3: DSL Versioning and Compatibility

**Challenge:** Support multiple versions of DSL API

```kotlin
@DslMarker
annotation class VersionedDslMarker

// V1 API
@VersionedDslMarker
class ApiV1Builder {
    var endpoint: String = ""
    var method: String = "GET"

    fun build(): ApiCall = ApiCall(endpoint, method, emptyMap())
}

// V2 API - adds headers support
@VersionedDslMarker
class ApiV2Builder {
    var endpoint: String = ""
    var method: String = "GET"
    private val headers = mutableMapOf<String, String>()

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun build(): ApiCall = ApiCall(endpoint, method, headers)
}

// V3 API - adds headers and query parameters
@VersionedDslMarker
class ApiV3Builder {
    var endpoint: String = ""
    var method: String = "GET"
    private val headers = mutableMapOf<String, String>()
    private val queryParams = mutableMapOf<String, String>()

    fun header(name: String, value: String) {
        headers[name] = value
    }

    fun param(name: String, value: String) {
        queryParams[name] = value
    }

    fun build(): ApiCall {
        val fullEndpoint = if (queryParams.isEmpty()) {
            endpoint
        } else {
            val params = queryParams.entries.joinToString("&") { "${it.key}=${it.value}" }
            "$endpoint?$params"
        }
        return ApiCall(fullEndpoint, method, headers)
    }
}

data class ApiCall(
    val endpoint: String,
    val method: String,
    val headers: Map<String, String>
)

// Versioned entry points
@Deprecated("Use apiCallV2 or apiCallV3", ReplaceWith("apiCallV3"))
fun apiCallV1(init: ApiV1Builder.() -> Unit): ApiCall {
    val builder = ApiV1Builder()
    builder.init()
    return builder.build()
}

fun apiCallV2(init: ApiV2Builder.() -> Unit): ApiCall {
    val builder = ApiV2Builder()
    builder.init()
    return builder.build()
}

fun apiCallV3(init: ApiV3Builder.() -> Unit): ApiCall {
    val builder = ApiV3Builder()
    builder.init()
    return builder.build()
}

// Migration helpers
fun ApiV1Builder.toV2(): ApiV2Builder {
    return ApiV2Builder().apply {
        endpoint = this@toV2.endpoint
        method = this@toV2.method
    }
}

// Usage - support all versions
fun demonstrateVersioning() {
    // V1 - deprecated but still works
    @Suppress("DEPRECATION")
    val callV1 = apiCallV1 {
        endpoint = "/users"
        method = "GET"
    }

    // V2 - current stable
    val callV2 = apiCallV2 {
        endpoint = "/users"
        method = "GET"
        header("Authorization", "Bearer token")
    }

    // V3 - latest
    val callV3 = apiCallV3 {
        endpoint = "/users"
        method = "GET"
        header("Authorization", "Bearer token")
        param("page", "1")
        param("limit", "10")
    }
}
```

---

## Advanced Scenarios

### Advanced Scenario 1: Context-Aware Builders

**Challenge:** Builder behavior changes based on context

```kotlin
@DslMarker
annotation class ContextDslMarker

enum class Environment {
    DEVELOPMENT, STAGING, PRODUCTION
}

@ContextDslMarker
class ApplicationBuilder {
    private var environment: Environment = Environment.DEVELOPMENT
    private lateinit var serverConfig: ServerConfig

    fun environment(env: Environment) {
        environment = env
    }

    fun server(init: ServerConfigBuilder.() -> Unit) {
        val builder = ServerConfigBuilder(environment)
        builder.init()
        serverConfig = builder.build()
    }

    fun build(): Application = Application(environment, serverConfig)
}

@ContextDslMarker
class ServerConfigBuilder(private val environment: Environment) {
    var host: String = when (environment) {
        Environment.DEVELOPMENT -> "localhost"
        Environment.STAGING -> "staging.example.com"
        Environment.PRODUCTION -> "api.example.com"
    }

    var port: Int = when (environment) {
        Environment.DEVELOPMENT -> 8080
        Environment.STAGING -> 8443
        Environment.PRODUCTION -> 443
    }

    var ssl: Boolean = environment != Environment.DEVELOPMENT

    var logLevel: String = when (environment) {
        Environment.DEVELOPMENT -> "DEBUG"
        Environment.STAGING -> "INFO"
        Environment.PRODUCTION -> "WARN"
    }

    fun build(): ServerConfig {
        // Environment-specific validation
        when (environment) {
            Environment.PRODUCTION -> {
                require(ssl) { "SSL must be enabled in production" }
                require(host != "localhost") { "Cannot use localhost in production" }
            }
            Environment.STAGING -> {
                require(ssl) { "SSL must be enabled in staging" }
            }
            Environment.DEVELOPMENT -> {
                // No restrictions in development
            }
        }

        return ServerConfig(host, port, ssl, logLevel)
    }
}

data class ServerConfig(
    val host: String,
    val port: Int,
    val ssl: Boolean,
    val logLevel: String
)

data class Application(
    val environment: Environment,
    val serverConfig: ServerConfig
)

fun application(init: ApplicationBuilder.() -> Unit): Application {
    val builder = ApplicationBuilder()
    builder.init()
    return builder.build()
}

// Usage - context affects defaults and validation
fun demonstrateContextAware() {
    // Development - permissive
    val devApp = application {
        environment(Environment.DEVELOPMENT)
        server {
            // Uses development defaults
            // host = "localhost", port = 8080, ssl = false
        }
    }

    // Production - strict validation
    val prodApp = application {
        environment(Environment.PRODUCTION)
        server {
            host = "api.example.com"
            port = 443
            ssl = true  // Required in production
        }
    }

    // This will fail validation:
    try {
        application {
            environment(Environment.PRODUCTION)
            server {
                host = "localhost"  // ❌ Invalid for production
            }
        }
    } catch (e: IllegalArgumentException) {
        println(e.message)  // "Cannot use localhost in production"
    }
}
```

### Advanced Scenario 2: Lazy Evaluation in DSLs

**Challenge:** Defer computation until needed

```kotlin
@DslMarker
annotation class LazyDslMarker

@LazyDslMarker
class LazyQueryBuilder {
    private val operations = mutableListOf<() -> QueryOperation>()

    fun where(condition: () -> Boolean): LazyQueryBuilder {
        operations.add { WhereOperation(condition) }
        return this
    }

    fun select(selector: () -> List<String>): LazyQueryBuilder {
        operations.add { SelectOperation(selector) }
        return this
    }

    fun orderBy(ordering: () -> String): LazyQueryBuilder {
        operations.add { OrderByOperation(ordering) }
        return this
    }

    fun build(): LazyQuery = LazyQuery(operations)
}

sealed class QueryOperation
data class WhereOperation(val condition: () -> Boolean) : QueryOperation()
data class SelectOperation(val selector: () -> List<String>) : QueryOperation()
data class OrderByOperation(val ordering: () -> String) : QueryOperation()

class LazyQuery(private val operations: List<() -> QueryOperation>) {
    // Operations are not executed until execute() is called
    fun execute(): QueryResult {
        val executedOps = operations.map { it() }

        println("Executing query with ${executedOps.size} operations")
        executedOps.forEach { op ->
            when (op) {
                is WhereOperation -> println("  WHERE: ${op.condition()}")
                is SelectOperation -> println("  SELECT: ${op.selector()}")
                is OrderByOperation -> println("  ORDER BY: ${op.ordering()}")
            }
        }

        return QueryResult()
    }
}

data class QueryResult(val rows: List<Map<String, Any>> = emptyList())

fun lazyQuery(init: LazyQueryBuilder.() -> Unit): LazyQuery {
    val builder = LazyQueryBuilder()
    builder.init()
    return builder.build()
}

// Usage - operations are defined but not executed
fun demonstrateLazyEvaluation() {
    var expensiveCalculationCount = 0

    val query = lazyQuery {
        where {
            expensiveCalculationCount++
            println("    [Expensive WHERE calculation]")
            true
        }
        select {
            expensiveCalculationCount++
            println("    [Expensive SELECT calculation]")
            listOf("id", "name")
        }
    }

    println("Query built, calculations: $expensiveCalculationCount")  // 0

    println("\nExecuting query...")
    query.execute()
    println("After execution, calculations: $expensiveCalculationCount")  // 2

    println("\nExecuting again...")
    query.execute()
    println("After second execution, calculations: $expensiveCalculationCount")  // 4
}
```

### Advanced Scenario 3: Type-Safe Builder with Phantom Types

**Challenge:** Enforce state transitions at compile time

```kotlin
// Phantom types for state tracking
sealed class BuilderState
class Initial : BuilderState()
class HasTitle : BuilderState()
class HasContent : BuilderState()
class Complete : BuilderState()

@DslMarker
annotation class StateMachineDslMarker

@StateMachineDslMarker
class ArticleBuilder<S : BuilderState> private constructor(
    private val title: String? = null,
    private val content: String? = null,
    private val tags: List<String> = emptyList()
) {
    companion object {
        fun create(): ArticleBuilder<Initial> = ArticleBuilder()
    }

    fun title(value: String): ArticleBuilder<HasTitle> {
        return ArticleBuilder(title = value, content = content, tags = tags)
    }

    fun content(value: String): ArticleBuilder<Complete> where S : HasTitle {
        return ArticleBuilder(title = title!!, content = value, tags = tags)
    }

    fun tag(value: String): ArticleBuilder<S> {
        return ArticleBuilder(title = title, content = content, tags = tags + value)
    }

    fun build(): Article where S : Complete {
        return Article(title!!, content!!, tags)
    }
}

data class Article(
    val title: String,
    val content: String,
    val tags: List<String>
)

// Usage - compile-time state enforcement
fun demonstratePhantomTypes() {
    // ✅ Correct order
    val article1 = ArticleBuilder.create()
        .title("My Article")
        .content("Content here")
        .tag("kotlin")
        .build()

    // ✅ Can add tags at any point
    val article2 = ArticleBuilder.create()
        .title("Another Article")
        .tag("dsl")
        .content("More content")
        .tag("builders")
        .build()

    // ❌ These won't compile:

    // Can't build without title and content
    // ArticleBuilder.create().build()  // ❌

    // Can't set content before title
    // ArticleBuilder.create().content("Content")  // ❌

    // Can't build with only title
    // ArticleBuilder.create().title("Title").build()  // ❌
}
```

### Advanced Scenario 4: Composable DSLs

**Challenge:** Combine multiple DSLs together

```kotlin
@DslMarker
annotation class ComposableDslMarker

// DSL 1: Styling
@ComposableDslMarker
class StyleBuilder {
    var color: String = "black"
    var fontSize: Int = 12
    var fontWeight: String = "normal"

    fun build(): Style = Style(color, fontSize, fontWeight)
}

// DSL 2: Layout
@ComposableDslMarker
class LayoutBuilder {
    var width: String = "auto"
    var height: String = "auto"
    var padding: Int = 0
    var margin: Int = 0

    fun build(): Layout = Layout(width, height, padding, margin)
}

// DSL 3: Component (composes Style + Layout)
@ComposableDslMarker
class ComponentBuilder {
    var text: String = ""
    private var style: Style? = null
    private var layout: Layout? = null
    private val children = mutableListOf<Component>()

    fun style(init: StyleBuilder.() -> Unit) {
        val builder = StyleBuilder()
        builder.init()
        style = builder.build()
    }

    fun layout(init: LayoutBuilder.() -> Unit) {
        val builder = LayoutBuilder()
        builder.init()
        layout = builder.build()
    }

    fun child(init: ComponentBuilder.() -> Unit) {
        val builder = ComponentBuilder()
        builder.init()
        children.add(builder.build())
    }

    fun build(): Component = Component(
        text,
        style ?: Style(),
        layout ?: Layout(),
        children
    )
}

data class Style(
    val color: String = "black",
    val fontSize: Int = 12,
    val fontWeight: String = "normal"
)

data class Layout(
    val width: String = "auto",
    val height: String = "auto",
    val padding: Int = 0,
    val margin: Int = 0
)

data class Component(
    val text: String,
    val style: Style,
    val layout: Layout,
    val children: List<Component>
)

fun component(init: ComponentBuilder.() -> Unit): Component {
    val builder = ComponentBuilder()
    builder.init()
    return builder.build()
}

// Usage - compose multiple DSLs
fun demonstrateComposableDsls() {
    val page = component {
        text = "Root"

        style {
            color = "blue"
            fontSize = 16
        }

        layout {
            width = "100%"
            padding = 20
        }

        child {
            text = "Header"
            style {
                fontSize = 24
                fontWeight = "bold"
            }
        }

        child {
            text = "Content"
            layout {
                padding = 10
                margin = 5
            }

            child {
                text = "Nested content"
            }
        }
    }
}
```

### Advanced Scenario 5: DSL with Dependency Injection

**Challenge:** Inject dependencies into DSL builders

```kotlin
@DslMarker
annotation class DiDslMarker

// Services to be injected
interface Logger {
    fun log(message: String)
}

interface Database {
    fun query(sql: String): List<Map<String, Any>>
}

// Context holds dependencies
class DslContext(
    val logger: Logger,
    val database: Database
)

@DiDslMarker
class ServiceBuilder(private val context: DslContext) {
    private val operations = mutableListOf<Operation>()

    fun logOperation(message: String) {
        operations.add(LogOperation(message, context.logger))
    }

    fun queryOperation(sql: String, handler: QueryHandler) {
        operations.add(QueryOperation(sql, context.database, handler))
    }

    fun build(): Service = Service(operations)
}

sealed class Operation {
    abstract fun execute()
}

data class LogOperation(
    private val message: String,
    private val logger: Logger
) : Operation() {
    override fun execute() {
        logger.log(message)
    }
}

data class QueryOperation(
    private val sql: String,
    private val database: Database,
    private val handler: QueryHandler
) : Operation() {
    override fun execute() {
        val results = database.query(sql)
        handler.handle(results)
    }
}

interface QueryHandler {
    fun handle(results: List<Map<String, Any>>)
}

data class Service(private val operations: List<Operation>) {
    fun execute() {
        operations.forEach { it.execute() }
    }
}

fun service(context: DslContext, init: ServiceBuilder.() -> Unit): Service {
    val builder = ServiceBuilder(context)
    builder.init()
    return builder.build()
}

// Usage - dependencies injected automatically
fun demonstrateDependencyInjection() {
    // Setup dependencies
    val logger = object : Logger {
        override fun log(message: String) {
            println("[LOG] $message")
        }
    }

    val database = object : Database {
        override fun query(sql: String): List<Map<String, Any>> {
            println("[DB] Executing: $sql")
            return emptyList()
        }
    }

    val context = DslContext(logger, database)

    // Build service with injected dependencies
    val myService = service(context) {
        logOperation("Service starting")

        queryOperation("SELECT * FROM users") {
            object : QueryHandler {
                override fun handle(results: List<Map<String, Any>>) {
                    println("Got ${results.size} results")
                }
            }
        }

        logOperation("Service completed")
    }

    // Execute
    myService.execute()
}
```

---

## Summary

This document covered:

1. **Real-world scenarios** - HTTP client, database migrations, configuration management
2. **Edge cases** - Circular dependencies, dynamic properties, optional vs required fields
3. **Common mistakes** - Missing @DslMarker, mutable state exposure, lack of validation
4. **Integration patterns** - Wrapping existing APIs, adapter pattern, gradual migration
5. **Testing strategies** - Construction testing, state testing, scope control, property-based testing
6. **Nuanced scenarios** - Validation strategies, error reporting, versioning
7. **Advanced scenarios** - Context-aware builders, lazy evaluation, phantom types, composable DSLs, dependency injection

## Key Takeaways

- Always use `@DslMarker` to prevent scope leakage
- Validate at the right time (set-time vs build-time)
- Provide clear error messages with context path
- Keep builder state private and immutable
- Test both successful and error cases
- Document thread-safety guarantees
- Consider lazy evaluation for expensive operations
- Use phantom types for compile-time state enforcement
- Make DSLs composable when appropriate
- Support dependency injection when builders need services

---

**Next:** [Exercises →](04-exercises.md)
