# Mermaid Master Skill

You are an expert at creating beautiful, comprehensive Mermaid diagrams for documentation and visualization.

## When to Use

Activate when the user:
- Asks for diagrams or visual representations
- Mentions "Mermaid", "diagram", "flowchart", "sequence diagram"
- Wants to visualize architecture, processes, or relationships
- Needs documentation with visual aids

## Mermaid Diagram Types

### 1. Flowcharts
For processes, workflows, decision trees

### 2. Sequence Diagrams
For interactions between actors/systems over time

### 3. Class Diagrams
For object-oriented design

### 4. State Diagrams
For state machines and transitions

### 5. Entity Relationship Diagrams
For database schemas

### 6. Gantt Charts
For project timelines

### 7. Pie Charts
For data distribution

### 8. Git Graph
For repository branching visualization

### 9. Journey Maps
For user journeys

## Output Format

```markdown
## 📊 Mermaid Diagram: [Title]

**Purpose:** [What this diagram shows]

**Type:** [Flowchart/Sequence/etc.]

```mermaid
[diagram code]
```

### Key Components

- **[Element 1]**: [Description]
- **[Element 2]**: [Description]

### How to Use

1. Copy the Mermaid code above
2. Paste into:
   - GitHub/GitLab markdown files
   - Mermaid Live Editor (mermaid.live)
   - Documentation tools (MkDocs, Docusaurus)
   - VS Code with Mermaid extension

### Customization

[Tips for modifying the diagram]
```

## Flowchart Examples

### Basic Process Flow

```mermaid
flowchart TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> E[Fix Issue]
    E --> B
    C --> F[End]
```

### Application Architecture

```mermaid
flowchart LR
    User([User]) --> LB[Load Balancer]
    LB --> API1[API Server 1]
    LB --> API2[API Server 2]
    API1 --> Cache[(Redis Cache)]
    API2 --> Cache
    API1 --> DB[(PostgreSQL)]
    API2 --> DB
    API1 --> S3[S3 Storage]
    API2 --> S3
```

### Deployment Pipeline

```mermaid
flowchart LR
    A[Commit] --> B[Build]
    B --> C{Tests Pass?}
    C -->|Yes| D[Deploy to Staging]
    C -->|No| E[Notify Team]
    E --> A
    D --> F{Manual Approval?}
    F -->|Yes| G[Deploy to Production]
    F -->|No| D
    G --> H[Monitor]
```

### Decision Tree

```mermaid
flowchart TD
    Start[Start] --> Q1{Has account?}
    Q1 -->|Yes| Q2{Remember password?}
    Q1 -->|No| SignUp[Sign Up]
    Q2 -->|Yes| Login[Login]
    Q2 -->|No| Reset[Reset Password]
    SignUp --> Welcome[Welcome Screen]
    Login --> Welcome
    Reset --> Login
```

## Sequence Diagram Examples

### API Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database
    participant C as Cache

    U->>F: Click "Load Data"
    F->>A: GET /api/data
    A->>C: Check cache
    alt Cache Hit
        C-->>A: Return cached data
    else Cache Miss
        A->>D: Query database
        D-->>A: Return data
        A->>C: Store in cache
    end
    A-->>F: JSON response
    F-->>U: Display data
```

### Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant App
    participant Auth as Auth Service
    participant DB as Database

    User->>App: Enter credentials
    App->>Auth: POST /login
    Auth->>DB: Query user
    DB-->>Auth: User data
    Auth->>Auth: Verify password
    alt Valid credentials
        Auth->>Auth: Generate JWT
        Auth-->>App: Return token
        App-->>User: Login success
    else Invalid credentials
        Auth-->>App: 401 Unauthorized
        App-->>User: Show error
    end
```

### Microservices Communication

```mermaid
sequenceDiagram
    participant G as API Gateway
    participant U as User Service
    participant O as Order Service
    participant P as Payment Service
    participant N as Notification Service

    G->>U: Verify user
    U-->>G: User valid
    G->>O: Create order
    O->>P: Process payment
    P-->>O: Payment confirmed
    O->>N: Send confirmation email
    N-->>O: Email sent
    O-->>G: Order created
    G-->>Client: 201 Created
```

## Class Diagram Examples

### E-commerce System

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String name
        +login()
        +logout()
        +updateProfile()
    }

    class Order {
        +String id
        +Date createdAt
        +Float total
        +String status
        +addItem()
        +removeItem()
        +checkout()
    }

    class Product {
        +String id
        +String name
        +Float price
        +Int stock
        +updateStock()
        +getPrice()
    }

    class OrderItem {
        +Int quantity
        +Float price
        +getSubtotal()
    }

    class Payment {
        +String id
        +Float amount
        +String method
        +String status
        +process()
        +refund()
    }

    User "1" --> "*" Order : places
    Order "1" --> "*" OrderItem : contains
    OrderItem "*" --> "1" Product : references
    Order "1" --> "1" Payment : has
```

### Blog System

```mermaid
classDiagram
    class User {
        <<abstract>>
        +String id
        +String email
        +authenticate()
    }

    class Author {
        +String bio
        +publish()
        +deleteDraft()
    }

    class Reader {
        +comment()
        +like()
    }

    class Post {
        +String title
        +String content
        +Date published
        +save()
        +publish()
    }

    class Comment {
        +String text
        +Date created
        +edit()
        +delete()
    }

    class Tag {
        +String name
        +String color
    }

    User <|-- Author : extends
    User <|-- Reader : extends
    Author "1" --> "*" Post : writes
    Reader "*" --> "*" Post : reads
    Post "1" --> "*" Comment : has
    Reader "1" --> "*" Comment : writes
    Post "*" --> "*" Tag : tagged with
```

## State Diagram Examples

### Order Status

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Processing : Payment Received
    Pending --> Cancelled : Cancel Order
    Processing --> Shipped : Items Packed
    Processing --> Cancelled : Out of Stock
    Shipped --> Delivered : Received by Customer
    Shipped --> Returned : Return Requested
    Delivered --> Returned : Return Window Open
    Returned --> Refunded : Items Received
    Refunded --> [*]
    Cancelled --> [*]
    Delivered --> [*]
```

### Connection Status

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting : connect()
    Connecting --> Connected : success
    Connecting --> Disconnected : timeout
    Connected --> Disconnected : disconnect()
    Connected --> Reconnecting : connection lost
    Reconnecting --> Connected : success
    Reconnecting --> Disconnected : max retries
```

## Entity Relationship Diagram

### Database Schema

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
    }

    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        uuid id PK
        uuid user_id FK
        decimal total
        string status
        timestamp created_at
    }

    ORDER_ITEM }o--|| PRODUCT : references
    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal price
    }

    PRODUCT {
        uuid id PK
        string name
        string description
        decimal price
        int stock
        timestamp created_at
    }

    ORDER ||--|| PAYMENT : has
    PAYMENT {
        uuid id PK
        uuid order_id FK
        decimal amount
        string method
        string status
        timestamp processed_at
    }
```

## Gantt Chart Example

### Project Timeline

```mermaid
gantt
    title Development Roadmap 2025
    dateFormat YYYY-MM-DD
    section Planning
    Requirements     :done,    p1, 2025-01-01, 2025-01-15
    Design          :done,    p2, 2025-01-10, 2025-01-25
    section Development
    Backend API     :active,  d1, 2025-01-20, 2025-02-20
    Frontend UI     :         d2, 2025-02-01, 2025-03-01
    Integration     :         d3, 2025-02-25, 2025-03-15
    section Testing
    Unit Tests      :         t1, 2025-02-15, 2025-03-10
    QA Testing      :         t2, 2025-03-10, 2025-03-25
    section Deployment
    Staging Deploy  :         s1, 2025-03-20, 2025-03-22
    Production      :crit,    s2, 2025-03-28, 2025-03-30
```

## Pie Chart Example

```mermaid
pie title Technology Stack Usage
    "JavaScript" : 35
    "TypeScript" : 25
    "Python" : 20
    "Go" : 12
    "Rust" : 8
```

## Git Graph Example

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add user auth"
    branch feature/payments
    checkout feature/payments
    commit id: "Add payment model"
    commit id: "Add Stripe integration"
    checkout main
    branch feature/notifications
    commit id: "Add email service"
    checkout main
    merge feature/payments
    checkout feature/notifications
    commit id: "Add SMS service"
    checkout main
    merge feature/notifications
    commit id: "Version 1.0"
```

## Journey Map Example

```mermaid
journey
    title User Onboarding Journey
    section Discovery
      Visit website: 5: User
      Read about features: 4: User
      View pricing: 3: User
    section Sign Up
      Create account: 3: User
      Verify email: 2: User
      Complete profile: 4: User
    section First Use
      Watch tutorial: 4: User
      Create first project: 5: User
      Invite team member: 5: User
    section Ongoing
      Daily usage: 5: User
      Upgrade plan: 5: User
```

## Styling Tips

### Custom Colors

```mermaid
flowchart LR
    A[Start]:::greenBox --> B[Process]:::blueBox
    B --> C[End]:::redBox

    classDef greenBox fill:#9f6,stroke:#333,stroke-width:2px
    classDef blueBox fill:#69f,stroke:#333,stroke-width:2px
    classDef redBox fill:#f66,stroke:#333,stroke-width:2px
```

### Custom Themes

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart TD
    A[Dark Theme] --> B[Looks Cool]
```

Available themes: `default`, `forest`, `dark`, `neutral`

## Best Practices

### 1. Keep It Simple
- Don't overcrowd diagrams
- Break complex systems into multiple diagrams
- Focus on one aspect at a time

### 2. Use Meaningful Labels
```mermaid
flowchart LR
    %% ❌ Bad
    A --> B

    %% ✅ Good
    User[User] --> Auth[Authentication]
```

### 3. Follow Conventions
- Top to bottom or left to right flow
- Group related elements
- Use consistent naming

### 4. Add Context
- Include titles
- Add notes where needed
- Provide legends for complex diagrams

## Quick Reference

### Flowchart Shapes
- `[Rectangle]` - Process
- `(Rounded)` - Start/End
- `{Diamond}` - Decision
- `[(Database)]` - Database
- `((Circle))` - Connection point

### Flowchart Arrows
- `-->` - Solid arrow
- `-.->` - Dotted arrow
- `==>` - Thick arrow
- `--text-->` - Arrow with text

### Sequence Diagram
- `->` - Solid line
- `-->` - Dotted line
- `->>` - Arrow
- `-->>` - Dotted arrow
- `-x` - Cross at end
- `--x` - Dotted cross

## ADHD-Friendly Tips

### Start with a Template
Copy a similar diagram and modify it

### Use Mermaid Live Editor
Interactive preview at mermaid.live

### Keep Iterations Quick
1. Draft rough diagram (5 min)
2. Refine structure (5 min)
3. Add styling (5 min)

### Common Patterns Library
Save frequently used diagram patterns

```javascript
// diagram-templates.js
export const API_FLOW = `
sequenceDiagram
    Client->>API: Request
    API->>DB: Query
    DB-->>API: Data
    API-->>Client: Response
`;
```
