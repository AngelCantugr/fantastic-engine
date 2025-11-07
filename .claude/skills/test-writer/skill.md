# Test Writer Skill

You are an expert at writing comprehensive, maintainable tests for any codebase.

## When to Use

Activate when the user:
- Asks to write tests
- Mentions "unit test", "integration test", "e2e test"
- Wants to improve code coverage
- Asks "how do I test this?"

## Testing Philosophy

### The Testing Pyramid

```
       /\
      /  \     E2E Tests (Few)
     /----\
    /      \   Integration Tests (Some)
   /--------\
  /          \  Unit Tests (Many)
 /____________\
```

- **Unit Tests (70%)**: Test individual functions/methods
- **Integration Tests (20%)**: Test component interactions
- **E2E Tests (10%)**: Test full user workflows

## Test Structure (AAA Pattern)

```javascript
test('description of what it should do', () => {
  // Arrange: Setup test data and environment
  const input = createTestData();

  // Act: Execute the code being tested
  const result = functionUnderTest(input);

  // Assert: Verify the result
  expect(result).toBe(expectedValue);
});
```

## Test Naming Convention

Use descriptive names that explain the scenario:

```javascript
// ✅ Good
test('should return empty array when input is null')
test('should throw error when user is not authenticated')
test('should calculate total with 10% discount for premium users')

// ❌ Bad
test('test1')
test('it works')
test('edge case')
```

## Framework Detection

Automatically detect and use the appropriate testing framework:

- **JavaScript/TypeScript**: Jest, Vitest, Mocha, Jasmine
- **Python**: pytest, unittest
- **Rust**: Built-in `#[test]`
- **Go**: Built-in `testing` package
- **Ruby**: RSpec, Minitest
- **Java**: JUnit

## Output Format

```markdown
## 🧪 Test Suite: [Component Name]

### Test Coverage Plan

- [ ] Happy path scenarios
- [ ] Edge cases
- [ ] Error conditions
- [ ] Boundary values
- [ ] Integration points

### Tests to Create

1. **[test file path]**
   - [Test case 1]
   - [Test case 2]
   - [Test case 3]

---

## Test Implementation

### File: `[path/to/test.spec.js]`

```[language]
[Complete test code]
```

### File: `[path/to/another.test.js]`

```[language]
[Complete test code]
```

---

## Running the Tests

```bash
[Command to run tests]
```

## Expected Coverage

- **Lines**: XX%
- **Functions**: XX%
- **Branches**: XX%
```

## Test Templates

### Unit Test Template (JavaScript/Jest)

```javascript
import { functionToTest } from './module';

describe('functionToTest', () => {
  // Happy path
  test('should return expected result for valid input', () => {
    const result = functionToTest('valid input');
    expect(result).toBe('expected output');
  });

  // Edge cases
  test('should handle empty input', () => {
    const result = functionToTest('');
    expect(result).toBe(null);
  });

  test('should handle null input', () => {
    const result = functionToTest(null);
    expect(result).toBeNull();
  });

  // Error conditions
  test('should throw error for invalid input', () => {
    expect(() => functionToTest('invalid')).toThrow('Error message');
  });
});
```

### Unit Test Template (Python/pytest)

```python
import pytest
from module import function_to_test

class TestFunctionToTest:
    def test_returns_expected_result_for_valid_input(self):
        result = function_to_test('valid input')
        assert result == 'expected output'

    def test_handles_empty_input(self):
        result = function_to_test('')
        assert result is None

    def test_raises_error_for_invalid_input(self):
        with pytest.raises(ValueError, match='Error message'):
            function_to_test('invalid')
```

### Integration Test Template

```javascript
import request from 'supertest';
import app from './app';

describe('API Integration Tests', () => {
  beforeEach(async () => {
    // Setup: Clear database, seed data
    await db.clear();
    await db.seed();
  });

  afterEach(async () => {
    // Cleanup
    await db.clear();
  });

  test('POST /api/users should create new user', async () => {
    const userData = {
      email: 'test@example.com',
      name: 'Test User'
    };

    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);

    expect(response.body).toMatchObject({
      email: userData.email,
      name: userData.name
    });
    expect(response.body.id).toBeDefined();
  });
});
```

## Test Coverage Checklist

For each function/method, test:

### Input Variations
- [ ] Valid inputs (happy path)
- [ ] Empty/null/undefined
- [ ] Boundary values (min, max)
- [ ] Invalid types
- [ ] Malformed data

### Behavior Variations
- [ ] Different code paths
- [ ] All branches (if/else)
- [ ] Loop iterations (zero, one, many)
- [ ] Exception handling
- [ ] Async behavior

### State Variations
- [ ] Initial state
- [ ] Modified state
- [ ] Edge states
- [ ] Concurrent state changes

## Mocking & Stubbing

### When to Mock

Mock external dependencies:
- HTTP requests
- Database calls
- File system operations
- Third-party APIs
- Time-dependent functions

### Mock Example (Jest)

```javascript
import axios from 'axios';
jest.mock('axios');

test('should fetch user data', async () => {
  // Arrange
  const mockUser = { id: 1, name: 'Test' };
  axios.get.mockResolvedValue({ data: mockUser });

  // Act
  const user = await fetchUser(1);

  // Assert
  expect(user).toEqual(mockUser);
  expect(axios.get).toHaveBeenCalledWith('/api/users/1');
});
```

## Test Data Builders

Create reusable test data factories:

```javascript
// testHelpers.js
export const buildUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
  ...overrides
});

// In tests
const admin = buildUser({ role: 'admin' });
const unverified = buildUser({ email: null });
```

## Testing Async Code

```javascript
// Using async/await (preferred)
test('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});

// Using promises
test('should fetch data', () => {
  return fetchData().then(data => {
    expect(data).toBeDefined();
  });
});

// Testing rejections
test('should reject with error', async () => {
  await expect(fetchData()).rejects.toThrow('Error message');
});
```

## Common Testing Patterns

### Parameterized Tests

```javascript
test.each([
  ['input1', 'expected1'],
  ['input2', 'expected2'],
  ['input3', 'expected3'],
])('should handle %s and return %s', (input, expected) => {
  expect(functionToTest(input)).toBe(expected);
});
```

### Snapshot Testing

```javascript
test('should render component correctly', () => {
  const tree = renderer.create(<Component />).toJSON();
  expect(tree).toMatchSnapshot();
});
```

## Tips

- **Test behavior, not implementation**: Don't test private methods
- **Keep tests independent**: Each test should run in isolation
- **Make tests readable**: Tests are documentation
- **Fast tests**: Unit tests should run in milliseconds
- **Deterministic**: Same input always produces same result
- **One assertion concept per test**: Test one thing at a time

## ADHD-Friendly Testing

- **Start with the happy path**: Get one test passing first
- **Test one function at a time**: Don't try to test everything at once
- **Use test.only**: Focus on one test while writing it
- **Run tests frequently**: Quick feedback loop
- **Celebrate green tests**: Each passing test is a win!

```javascript
test.only('should work for basic case', () => {
  // Focus on this one test
});
```
