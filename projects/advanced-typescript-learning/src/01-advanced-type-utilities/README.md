# 01 - Advanced Type Utilities 🔧

**Complexity:** Medium
**Focus:** Custom utility types, mapped types, conditional types

## 📚 Concepts Covered

1. **Mapped Types** - Transform properties of existing types
2. **Conditional Types** - Type-level if/else statements
3. **Template Literal Types** - String manipulation at type level
4. **Utility Type Composition** - Building complex types from simpler ones
5. **Type Inference with `infer`** - Extract types from other types

## 🎯 Learning Objectives

- Master TypeScript's built-in utility types
- Create custom utility types for common patterns
- Understand how to compose types for maximum reusability
- Learn type inference patterns with `infer` keyword

## 💡 Key Concepts

### Mapped Types

Mapped types allow you to transform properties of an existing type:

```typescript
type Readonly<T> = {
  readonly [K in keyof T]: T[K]
}
```

### Conditional Types

Conditional types enable type-level branching:

```typescript
type IsString<T> = T extends string ? true : false
```

### The `infer` Keyword

Extract types from function signatures, arrays, promises, etc:

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never
```

## 🔬 Practical Examples

### 1. Deep Partial

Make all nested properties optional:

```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K]
}
```

### 2. Deep Readonly

Make all nested properties readonly:

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K]
}
```

### 3. Nullable vs Optional

```typescript
type Nullable<T> = T | null
type Optional<T> = T | undefined
type Maybe<T> = T | null | undefined
```

## 🎓 Nuanced Scenarios

### Scenario 1: Form State Management

```typescript
// Transform all fields to include validation state
type FieldState<T> = {
  value: T
  error?: string
  touched: boolean
}

type FormState<T> = {
  [K in keyof T]: FieldState<T[K]>
}

// Usage
interface LoginForm {
  email: string
  password: string
}

type LoginFormState = FormState<LoginForm>
// Result:
// {
//   email: { value: string, error?: string, touched: boolean }
//   password: { value: string, error?: string, touched: boolean }
// }
```

### Scenario 2: API Response Wrapper

```typescript
type ApiResponse<T> =
  | { status: 'success'; data: T }
  | { status: 'error'; error: string }
  | { status: 'loading' }

// Extract successful data type
type ExtractData<T> = T extends { status: 'success'; data: infer D } ? D : never
```

### Scenario 3: Function Property Picker

```typescript
// Extract only function properties
type FunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? K : never
}[keyof T]

type FunctionProperties<T> = Pick<T, FunctionPropertyNames<T>>
```

## 🏃 Practice Exercises

1. Create a `DeepRequired<T>` type that makes all nested properties required
2. Build a `PickByType<T, U>` that selects properties of type U
3. Implement `OmitByType<T, U>` that removes properties of type U
4. Create `Promisify<T>` that wraps all function return types in Promise

## 📖 Further Reading

- TypeScript Handbook: Mapped Types
- TypeScript Handbook: Conditional Types
- Advanced TypeScript patterns by Matt Pocock
