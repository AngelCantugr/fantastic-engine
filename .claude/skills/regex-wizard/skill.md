# Regex Wizard Skill

You are a regular expression expert who creates, explains, and debugs regex patterns.

## When to Use

Activate when the user:
- Asks for regex help
- Mentions "regular expression", "regex", "pattern matching"
- Wants to validate or extract data from text
- Needs to search/replace with patterns

## Regex Fundamentals

### Character Classes
```
.       Any character (except newline)
\d      Digit (0-9)
\D      Not a digit
\w      Word character (a-z, A-Z, 0-9, _)
\W      Not a word character
\s      Whitespace
\S      Not whitespace
[abc]   Any of a, b, or c
[^abc]  Not a, b, or c
[a-z]   Range a through z
```

### Quantifiers
```
*       0 or more
+       1 or more
?       0 or 1
{3}     Exactly 3
{3,}    3 or more
{3,5}   Between 3 and 5
```

### Anchors
```
^       Start of string
$       End of string
\b      Word boundary
\B      Not a word boundary
```

### Groups
```
(abc)   Capturing group
(?:abc) Non-capturing group
(?<name>abc) Named capturing group
(a|b)   Alternation (a or b)
```

### Lookarounds
```
(?=abc)  Positive lookahead
(?!abc)  Negative lookahead
(?<=abc) Positive lookbehind
(?<!abc) Negative lookbehind
```

## Output Format

```markdown
## 🔍 Regex Pattern: [Purpose]

### Pattern

```regex
[regex pattern]
```

**Flags:** [g, i, m, s, u] - [explanation]

### Breakdown

```
[pattern with spacing]
^──────── [explanation of part 1]
  ^────── [explanation of part 2]
    ^──── [explanation of part 3]
```

### Explanation

[Detailed explanation in plain English]

### Test Cases

**Matches ✅**
- `[example 1]` → `[captured groups]`
- `[example 2]` → `[captured groups]`

**Doesn't Match ❌**
- `[example 1]` - [why not]
- `[example 2]` - [why not]

### Usage Examples

**JavaScript:**
```javascript
const pattern = /[regex]/[flags];
const result = text.match(pattern);
```

**Python:**
```python
import re
pattern = r'[regex]'
result = re.findall(pattern, text)
```

**Alternatives:**
[Simpler approaches if applicable]
```

## Common Regex Patterns

### Email Validation

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

**Breakdown:**
```
^[a-zA-Z0-9._%+-]+  Local part (before @)
@                   Literal @ symbol
[a-zA-Z0-9.-]+      Domain name
\.                  Literal dot
[a-zA-Z]{2,}        TLD (2+ letters)
$                   End of string
```

**Better validation:** Use a library or `input[type="email"]`

### URL Validation

```regex
^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$
```

**Note:** URLs are complex. Consider using `new URL()` in JavaScript.

### Phone Numbers (US)

```regex
^\(?(\d{3})\)?[- ]?(\d{3})[- ]?(\d{4})$
```

**Matches:**
- `(555) 123-4567`
- `555-123-4567`
- `5551234567`

### Credit Card (Basic)

```regex
^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$
```

**Patterns:**
- Visa: `^4[0-9]{12}(?:[0-9]{3})?$`
- Mastercard: `^5[1-5][0-9]{14}$`
- Amex: `^3[47][0-9]{13}$`

**Note:** Always use proper payment libraries!

### Date Formats

```regex
# YYYY-MM-DD
^(\d{4})-(\d{2})-(\d{2})$

# MM/DD/YYYY
^(\d{2})/(\d{2})/(\d{4})$

# DD-MM-YYYY
^(\d{2})-(\d{2})-(\d{4})$
```

### Password Strength

```regex
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

**Requirements:**
- At least 8 characters
- At least 1 lowercase letter
- At least 1 uppercase letter
- At least 1 digit
- At least 1 special character

### IP Address (IPv4)

```regex
^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
```

**Matches:**
- `192.168.1.1`
- `10.0.0.255`
- `255.255.255.0`

### Hex Color

```regex
^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$
```

**Matches:**
- `#FF5733`
- `#F57`
- `FF5733`

### UUID

```regex
^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$
```

**Matches:**
- `123e4567-e89b-12d3-a456-426614174000`

### Username (alphanumeric + underscore)

```regex
^[a-zA-Z0-9_]{3,16}$
```

**Rules:**
- 3-16 characters
- Letters, numbers, underscore only

### Slug (URL-friendly)

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

**Matches:**
- `my-blog-post`
- `hello-world-2024`

### Extract from Text

#### Extract emails

```regex
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
```

#### Extract URLs

```regex
https?://[^\s]+
```

#### Extract hashtags

```regex
#\w+
```

#### Extract mentions

```regex
@\w+
```

#### Extract numbers

```regex
\d+(?:\.\d+)?
```

## Advanced Examples

### Validate HTML Tags

```regex
^<([a-z]+)([^<]+)*(?:>(.*)<\/\1>|\s+\/>)$
```

**Matches:**
- `<div>content</div>`
- `<img src="test.jpg" />`

**Note:** Don't use regex for HTML parsing! Use a proper HTML parser.

### Extract JSON Keys

```regex
"([^"]+)"\s*:
```

**Matches:**
- `"name":` → captures `name`
- `"email":` → captures `email`

### Remove Comments

```javascript
// JavaScript comments
/\/\/.*$/gm          // Single-line
/\/\*[\s\S]*?\*\//g  // Multi-line
```

### Camel to Snake Case

```javascript
const toSnakeCase = (str) => {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
};

// myVariableName → my_variable_name
```

### Validate GitHub Repo Format

```regex
^[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+$
```

**Matches:**
- `username/repo-name`
- `org_name/project_name`

## Debugging Regex

### Test Incrementally

```javascript
// Build pattern step by step
const tests = [
  /^\d/,              // Starts with digit
  /^\d{3}/,           // 3 digits
  /^\d{3}-/,          // 3 digits + dash
  /^\d{3}-\d{3}/,     // Add 3 more digits
  /^\d{3}-\d{3}-\d{4}$/ // Complete pattern
];

tests.forEach((pattern, i) => {
  console.log(`Step ${i + 1}:`, pattern.test('555-123-4567'));
});
```

### Common Mistakes

```javascript
// ❌ Forgetting to escape special characters
/user@example.com/   // Wrong - @ and . have special meaning

// ✅ Escaped
/user@example\.com/

// ❌ Greedy matching
/<.*>/               // Matches <a> and <b> as one match in "<a><b>"

// ✅ Non-greedy
/<.*?>/              // Matches <a> and <b> separately

// ❌ Not anchoring when needed
/\d{3}-\d{4}/        // Matches 123-4567 in "abc123-4567xyz"

// ✅ Anchored
/^\d{3}-\d{4}$/      // Only matches exactly 123-4567
```

### Visualization Tools

- **regex101.com** - Best online regex tester
- **regexr.com** - Visual regex tool
- **debuggex.com** - Regex railroad diagrams

## Language-Specific Usage

### JavaScript

```javascript
// Literal notation
const pattern = /\d+/g;

// Constructor
const pattern = new RegExp('\\d+', 'g');

// Test
if (pattern.test(str)) { }

// Match
const matches = str.match(pattern);

// Replace
const result = str.replace(pattern, 'replacement');

// Split
const parts = str.split(pattern);

// Match with groups
const [full, group1, group2] = str.match(/(\d+)-(\d+)/);
```

### Python

```python
import re

# Compile
pattern = re.compile(r'\d+')

# Test
if pattern.search(text): pass

# Find all
matches = re.findall(r'\d+', text)

# Replace
result = re.sub(r'\d+', 'replacement', text)

# Split
parts = re.split(r'\s+', text)

# Match with groups
match = re.search(r'(\d+)-(\d+)', text)
if match:
    group1 = match.group(1)
    group2 = match.group(2)
```

### Go

```go
import "regexp"

// Compile
pattern := regexp.MustCompile(`\d+`)

// Test
matched := pattern.MatchString(text)

// Find
result := pattern.FindString(text)

// Find all
results := pattern.FindAllString(text, -1)

// Replace
result := pattern.ReplaceAllString(text, "replacement")
```

## Performance Tips

```javascript
// ❌ Slow - backtracking nightmare
/^(a+)+$/

// ✅ Fast - no backtracking
/^a+$/

// ❌ Slow - compiling in loop
for (const item of items) {
  if (/pattern/.test(item)) { }
}

// ✅ Fast - compile once
const pattern = /pattern/;
for (const item of items) {
  if (pattern.test(item)) { }
}
```

## When NOT to Use Regex

### Don't use regex for:
- HTML/XML parsing (use DOMParser, cheerio, BeautifulSoup)
- JSON parsing (use JSON.parse)
- CSV parsing (use csv library)
- Complex email validation (use validator library)
- URL parsing (use URL API)

### Use regex for:
- Simple pattern matching
- Text search and replace
- Input validation
- Extracting simple patterns
- Tokenizing text

## Quick Reference Card

```
Anchors:    ^$\b\B
Classes:    \d\w\s  [abc]  [^abc]  [a-z]
Quantifiers:*+?  {n}  {n,}  {n,m}
Groups:     ()  (?:)  (?<name>)
Lookaround: (?=)  (?!)  (?<=)  (?<!)
Special:    .  |  \
Flags:      g(global) i(ignore case) m(multiline) s(dotall)

Escapes:    \.  \*  \+  \?  \[  \]  \(  \)  \{  \}  \^  \$  \|  \\
```

## ADHD-Friendly Regex

### Build Incrementally
Start simple, add complexity step by step

```javascript
// Step 1
/\d/         // Match a digit

// Step 2
/\d{3}/      // Match 3 digits

// Step 3
/\d{3}-/     // Match 3 digits and dash

// Step 4
/\d{3}-\d{4}/ // Complete phone pattern
```

### Use Variables for Readability

```javascript
const digit = '\\d';
const phone = `${digit}{3}-${digit}{4}`;
const pattern = new RegExp(`^${phone}$`);
```

### Comment Complex Patterns

```javascript
const emailPattern = new RegExp([
  '^',
  '[a-zA-Z0-9._%+-]+',  // Local part
  '@',                   // At symbol
  '[a-zA-Z0-9.-]+',      // Domain
  '\\.',                 // Dot
  '[a-zA-Z]{2,}',        // TLD
  '$'
].join(''));
```

### Keep a Pattern Library

```javascript
// regex-patterns.js
export const patterns = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  phone: /^\d{3}-\d{3}-\d{4}$/,
  zipCode: /^\d{5}(-\d{4})?$/,
  url: /^https?:\/\/.+/,
  hex: /^#?[a-fA-F0-9]{6}$/
};
```
