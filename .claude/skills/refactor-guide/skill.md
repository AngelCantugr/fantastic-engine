# Refactor Guide Skill

You are an expert at identifying refactoring opportunities and guiding clean code transformations.

## When to Use

Activate when the user:
- Asks to refactor code
- Mentions "clean up", "improve", "optimize code structure"
- Says code is "messy", "hard to read", "duplicated"
- Wants to improve maintainability

## Refactoring Principles

### The Rule of Three
Don't refactor until you have:
1. Written it once
2. Duplicated it twice
3. Now refactor on the third occurrence

### Red-Green-Refactor
1. **Red**: Tests fail (or write failing test)
2. **Green**: Make tests pass (quick & dirty)
3. **Refactor**: Clean up while keeping tests green

## Code Smells to Detect

```markdown
## 🔍 Code Smell Checklist

### Bloaters
- [ ] Long methods (>20 lines)
- [ ] Large classes (>200 lines)
- [ ] Too many parameters (>3)
- [ ] Data clumps (same groups of variables)

### Object-Orientation Abusers
- [ ] Switch statements (consider polymorphism)
- [ ] Temporary fields
- [ ] Refused bequest
- [ ] Alternative classes with different interfaces

### Change Preventers
- [ ] Divergent change (one class changed for many reasons)
- [ ] Shotgun surgery (one change requires many class edits)
- [ ] Parallel inheritance hierarchies

### Dispensables
- [ ] Comments explaining what code does (code should be self-documenting)
- [ ] Duplicate code
- [ ] Dead code
- [ ] Speculative generality

### Couplers
- [ ] Feature envy (method uses another class more than its own)
- [ ] Inappropriate intimacy (classes too dependent)
- [ ] Message chains (a.b().c().d())
- [ ] Middle man (class just delegates)
```

## Output Format

```markdown
## 🔧 Refactoring Plan: [Component Name]

### 📊 Current Issues

**Code Smells Detected:**
1. [Smell type]: [Where and why]
2. [Smell type]: [Where and why]

**Technical Debt Score:** 🔴 High | 🟡 Medium | 🟢 Low

### 🎯 Refactoring Strategy

**Goal:** [What we want to achieve]

**Steps:**
1. [First refactoring]
2. [Second refactoring]
3. [Third refactoring]

**Risk Level:** 🔴 High | 🟡 Medium | 🟢 Low

---

## 📝 Step-by-Step Refactoring

### Step 1: [Refactoring Name]

**Before:**
```[language]
[Original code]
```

**After:**
```[language]
[Refactored code]
```

**Improvements:**
- [What's better]
- [Metrics: lines reduced, complexity, etc.]

---

### Step 2: [Next Refactoring]

[Repeat pattern]

---

## ✅ Validation

**Tests to run:**
```bash
[Test commands]
```

**Checklist:**
- [ ] All tests still pass
- [ ] No new warnings
- [ ] Behavior unchanged
- [ ] Code more readable
- [ ] Complexity reduced

## 📈 Impact

- **Lines of code:** X → Y (Z% reduction)
- **Cyclomatic complexity:** X → Y
- **Duplication:** X → Y
- **Maintainability:** [Improved/Same]
```

## Common Refactorings

### 1. Extract Method

**When:** Method too long or does multiple things

```javascript
// ❌ Before
function processOrder(order) {
  // Validate
  if (!order.items || order.items.length === 0) {
    throw new Error('No items');
  }
  if (!order.customer) {
    throw new Error('No customer');
  }

  // Calculate
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }
  if (order.customer.isPremium) {
    total *= 0.9;
  }

  // Save
  db.save(order);
}

// ✅ After
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  saveOrder(order, total);
}

function validateOrder(order) {
  if (!order.items?.length) throw new Error('No items');
  if (!order.customer) throw new Error('No customer');
}

function calculateTotal(order) {
  const subtotal = order.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  return order.customer.isPremium ? subtotal * 0.9 : subtotal;
}

function saveOrder(order, total) {
  db.save({ ...order, total });
}
```

### 2. Replace Conditional with Polymorphism

**When:** Switch/if-else based on type

```javascript
// ❌ Before
function calculateShipping(order) {
  switch (order.type) {
    case 'standard':
      return order.weight * 0.5;
    case 'express':
      return order.weight * 1.5 + 10;
    case 'overnight':
      return order.weight * 3.0 + 25;
  }
}

// ✅ After
class ShippingMethod {
  calculate(order) {
    throw new Error('Must implement');
  }
}

class StandardShipping extends ShippingMethod {
  calculate(order) {
    return order.weight * 0.5;
  }
}

class ExpressShipping extends ShippingMethod {
  calculate(order) {
    return order.weight * 1.5 + 10;
  }
}

class OvernightShipping extends ShippingMethod {
  calculate(order) {
    return order.weight * 3.0 + 25;
  }
}

// Usage
const shipping = shippingMethods[order.type];
const cost = shipping.calculate(order);
```

### 3. Introduce Parameter Object

**When:** Functions take many related parameters

```javascript
// ❌ Before
function createUser(firstName, lastName, email, phone, address, city, state, zip) {
  // ...
}

// ✅ After
function createUser(userInfo) {
  const { firstName, lastName, email, phone, address, city, state, zip } = userInfo;
  // ...
}

// Or better with a class/type
class UserInfo {
  constructor(data) {
    this.firstName = data.firstName;
    this.lastName = data.lastName;
    this.contactInfo = {
      email: data.email,
      phone: data.phone
    };
    this.address = {
      street: data.address,
      city: data.city,
      state: data.state,
      zip: data.zip
    };
  }
}
```

### 4. Replace Magic Numbers with Constants

```javascript
// ❌ Before
if (user.age >= 18) {
  if (order.total > 100) {
    discount = order.total * 0.1;
  }
}

// ✅ After
const ADULT_AGE = 18;
const DISCOUNT_THRESHOLD = 100;
const DISCOUNT_RATE = 0.1;

if (user.age >= ADULT_AGE) {
  if (order.total > DISCOUNT_THRESHOLD) {
    discount = order.total * DISCOUNT_RATE;
  }
}
```

### 5. Decompose Conditional

```javascript
// ❌ Before
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
  charge = quantity * winterRate + winterServiceCharge;
} else {
  charge = quantity * summerRate;
}

// ✅ After
const isSummer = date.after(SUMMER_START) && date.before(SUMMER_END);

if (isSummer) {
  charge = summerCharge(quantity);
} else {
  charge = winterCharge(quantity);
}

function summerCharge(quantity) {
  return quantity * summerRate;
}

function winterCharge(quantity) {
  return quantity * winterRate + winterServiceCharge;
}
```

### 6. Replace Nested Conditionals with Guard Clauses

```javascript
// ❌ Before
function getPayment(user) {
  let result;
  if (user.isDead) {
    result = deadAmount();
  } else {
    if (user.isSeparated) {
      result = separatedAmount();
    } else {
      if (user.isRetired) {
        result = retiredAmount();
      } else {
        result = normalAmount();
      }
    }
  }
  return result;
}

// ✅ After
function getPayment(user) {
  if (user.isDead) return deadAmount();
  if (user.isSeparated) return separatedAmount();
  if (user.isRetired) return retiredAmount();
  return normalAmount();
}
```

## Refactoring Safety Checklist

Before refactoring:
- [ ] **Have tests**: Write tests if they don't exist
- [ ] **Commit current state**: Create a restore point
- [ ] **One refactoring at a time**: Don't mix multiple changes
- [ ] **Run tests after each step**: Ensure nothing breaks

During refactoring:
- [ ] **Keep semantics identical**: Behavior shouldn't change
- [ ] **Small steps**: Refactor incrementally
- [ ] **Run tests frequently**: After each mini-change

After refactoring:
- [ ] **All tests pass**: Green across the board
- [ ] **Code review**: Get feedback
- [ ] **Update documentation**: If public API changed

## Metrics to Track

### Before & After Comparison

```markdown
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of Code | 150 | 95 | -37% |
| Cyclomatic Complexity | 12 | 6 | -50% |
| Code Duplication | 45% | 5% | -89% |
| Test Coverage | 60% | 75% | +25% |
| Methods | 3 | 8 | +167% |
| Max Method Length | 85 | 12 | -86% |
```

## When NOT to Refactor

- **Right before a deadline**: Risk vs reward
- **Legacy code without tests**: Write tests first
- **Code that rarely changes**: ROI too low
- **Performance-critical sections**: Profile first

## ADHD-Friendly Refactoring

### Time-Box It
- Set a timer for 25 minutes (Pomodoro)
- Focus on one refactoring pattern
- Take a break between refactorings

### Make It Visible
```markdown
## Refactoring Progress

- [x] Extract validateOrder method
- [x] Extract calculateTotal method
- [ ] Extract saveOrder method
- [ ] Add type definitions
- [ ] Update tests
```

### Celebrate Small Wins
Each successful refactoring is progress! 🎉

### Use IDE Refactoring Tools
- Rename: F2 (most IDEs)
- Extract method: Ctrl+Shift+R
- Move: F6
- Safe delete: Alt+Delete

Don't do it manually if your IDE can do it automatically!
