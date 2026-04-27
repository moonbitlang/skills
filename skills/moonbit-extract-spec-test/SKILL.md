---
name: moonbit-extract-spec-test
description: Extract formal spec and comprehensive test suites from existing MoonBit implementations. Use when asked to "extract spec from implementation", "generate tests from code", or "create spec-driven tests for existing package". Analyzes existing code to produce spec.mbt with `declare` keyword stubs and organized test files (valid/invalid).
---

# MoonBit Extract Spec & Test

## Overview

Reverse-engineer a formal API contract (`<pkg>_spec.mbt`) and comprehensive test suites from an existing MoonBit implementation. This enables spec-driven testing for already-written code.

## When to Use

- User asks to "extract spec from existing implementation"
- User wants to "generate spec-driven tests for a package"
- User requests "create formal API specification from code"
- Converting legacy code to spec-driven development workflow
- Need to document and test existing public API surface

## Workflow

### 1. Analyze the Existing Implementation

**Identify public API surface:**

- List all `pub` and `pub(all)` types, functions, traits
- Note error types (suberrors) and their variants
- Document method signatures and trait implementations
- Identify key entry points and core functionality

**Examine test patterns (if tests exist):**

- Look for existing test files (`*_test.mbt`, `*_wbtest.mbt`)
- Identify test coverage gaps
- Note common test scenarios

### 2. Generate the Spec File (`<pkg>_spec.mbt`)

**Create formal API contract:**

- Use the `declare` keyword for all public functions/types
- Preserve exact type signatures from implementation
- Include error types with `derive(Show, Eq, ToJson)` for testability
- Add documentation comments from original code
- Declarations with `declare` do not have a body
- Use `pub(all)` for types that need construction in tests
- Keep `pub` for opaque types

**Example spec structure:**

```mbt
///|
/// Error type for parsing operations
pub(all) suberror ParseError {
  InvalidFormat(String)
  UnexpectedEof
} derive(Show, Eq, ToJson)

///|
/// Main data type
declare pub(all) type Toml

///|
/// Convert to test JSON format
declare pub fn Toml::to_test_json(self : Toml) -> Json

///|
/// Parse TOML from string
declare pub fn parse(input : StringView) -> Result[Toml, ParseError]
```

### 3. Extract and Organize Test Cases

**Categorize tests by validity (happy path vs error path):**

**Valid tests** (`<pkg>_valid_test.mbt`):

- Happy path: valid inputs that exercise core features
- Edge cases: boundary sizes, empty inputs, maximum nesting
- Compatibility: behaviors that match real-world data or dominant implementations
- Regression: bugs fixed in prior work or known pitfalls

**Invalid tests** (`<pkg>_invalid_test.mbt`):

- Error path: invalid inputs and required error behavior
- Ambiguities: inputs where the spec allows multiple interpretations (tests pin down chosen interpretation)
- Malformed inputs: syntax errors, type mismatches, constraint violations

### 4. Write Spec-Driven Tests

**For valid input tests:**

```mbt
///|
test "valid/category/test-name" {
  let toml_text =
    #|key = "value"
    #|
  let toml = match @pkg.parse(toml_text) {
    Ok(toml) => toml
    Err(error) => fail("Failed to parse: " + error.to_string())
  }
  json_inspect(toml.to_test_json(), content={
    "key": { "type": "string", "value": "value" }
  })
}
```

**For invalid input tests:**

```mbt
///|
test "invalid/category/test-name" {
  let toml_text =
    #|invalid syntax here
    #|
  match @pkg.parse(toml_text) {
    Ok(toml) => {
      let json = toml.to_test_json()
      fail("Expected parse to fail, got \{json.stringify(indent=2)}")
    }
    Err(_) => ()
  }
}
```

### 5. Validate

**Type-check the spec:**

```bash
moon check
```

**Run the tests:**

```bash
moon test          # Run all tests
moon test -u       # Update snapshot tests
```

**Verify coverage:**

- Ensure all public API functions have tests
- Check for untested error paths
- Confirm edge cases are covered

## Key Principles

### Spec File Rules

1. **Declaration-only stubs**: All public API uses `declare` keyword (no body needed)
2. **Exact signatures**: Match the implementation's type signatures precisely
3. **Error handling**: Include all error types with proper derives
4. **Documentation**: Preserve or add doc comments for clarity
5. **Test helpers**: Include conversion functions like `to_test_json()` for inspection

### Test Organization

1. **Black-box testing**: Tests use only public API (call via `@pkg.function`)
2. **Snapshot testing**: Prefer `json_inspect()` for complex values
3. **Clear naming**: Use descriptive test names like "valid/arrays/nested" or "invalid/keys/empty"
4. **Categorization**: Organize by validity (`<pkg>_valid_test.mbt` for happy path, `<pkg>_invalid_test.mbt` for error path)
5. **Block separation**: Use `///|` to delimit test blocks

### Test Coverage Goals

- **Positive cases**: Valid inputs producing expected outputs
- **Negative cases**: Invalid inputs producing appropriate errors
- **Edge cases**: Boundaries, empty inputs, special values
- **Integration**: Features working together
- **Aim for 80-90% API coverage**

## Example Extraction

### From Implementation

```mbt
pub type Config

pub fn Config::parse(text : String) -> Result[Config, String] {
  // implementation
}

pub fn Config::get_value(self : Config, key : String) -> String? {
  // implementation
}
```

### To Spec

```mbt
///|
declare pub type Config

///|
declare pub fn Config::parse(text : String) -> Result[Config, String]

///|
declare pub fn Config::get_value(self : Config, key : String) -> String?
```

### To Tests

```mbt
///|
test "parse valid config" {
  let result = try? Config::parse("key=value")
  match result {
    Ok(cfg) => {
      inspect(cfg.get_value("key"), content="Some(\"value\")")
    }
    Err(e) => fail("Parse failed: \{e}")
  }
}

///|
test "parse invalid config returns error" {
  let result = try? Config::parse("invalid")
  match result {
    Ok(_) => fail("Should have failed to parse")
    Err(_) => ()
  }
}
```

## Tips

- **Start simple**: Begin with core functionality, add complexity incrementally
- **Use existing tests**: If tests exist, migrate and enhance them
- **Iterate**: Run `moon check` frequently to catch type errors early
- **Update snapshots**: Use `moon test -u` when output format changes
- **Document reasoning**: Add comments explaining non-obvious test cases

## Common Patterns

### Testing with Result types

```mbt
let result : Result[T, Error] = try? function_call(...)
match result {
  Ok(value) => inspect(value, content="...")
  Err(e) => fail("Unexpected error: \{e}")
}
```

### Testing expected failures

```mbt
match try? function_call(...) {
  Ok(v) => fail("Expected error, got \{v}")
  Err(_) => ()  // Success - error was expected
}
```

### Using test JSON format

```mbt
json_inspect(value.to_test_json(), content={
  "field": { "type": "integer", "value": "42" }
})
```
