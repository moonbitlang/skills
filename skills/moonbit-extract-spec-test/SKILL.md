---
name: moonbit-extract-spec-test
description: Extract formal spec and comprehensive test suites from existing MoonBit implementations. Use when asked to "extract spec from implementation", "generate tests from code", or "create spec-driven tests for existing package". Analyzes existing code to produce spec.mbt with `declare` keyword stubs and organized test files (valid/invalid).
---

# MoonBit Extract Spec & Test

> Validated 2026-10-27 against moon 0.1.20261023 / moonc v0.10.17+d971670cd by compiling and running a full spec + implementation + black-box/white-box test project. Key toolchain facts baked in below: `try?` removed, `derive(Show)` deprecated, `raise`-style signatures preferred over `Result[T, Error]`, and `@pkg.`-prefix requirements in black-box tests.

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
- Include error types with `derive(Debug, Eq, ToJson)` for testability — `derive(Show)` is deprecated (warning `deprecated_syntax`); use `Debug` + `debug_inspect()` for diagnostic output
- Prefer `T raise E` signatures for failable APIs; the toolchain warns `result_error_return` for `Result[T, E]` where `E` is an error type — keep `Result` only when success/failure must flow as ordinary data
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
} derive(Debug, Eq, ToJson)

///|
/// Main data type
declare pub(all) type Toml

///|
/// Convert to test JSON format
declare pub fn Toml::to_test_json(self : Toml) -> Json

///|
/// Parse TOML from string
declare pub fn parse(input : StringView) -> Toml raise ParseError
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

**For valid input tests** — call raising functions directly: a `test` block propagates errors by default, so an unexpected raise fails the test with the actual error (no `try?`-style wrapper needed):

```mbt
///|
test "valid/category/test-name" {
  let toml_text =
    #|key = "value"
    #|
  let toml = @pkg.parse(toml_text)
  json_inspect(toml.to_test_json(), content={
    "key": { "type": "string", "value": "value" }
  })
}
```

**For invalid input tests** — use `try ... catch ... noraise`, matching suberror variants exhaustively (a non-exhaustive `catch` is error `partial_match`):

```mbt
///|
test "invalid/category/test-name" {
  let toml_text =
    #|invalid syntax here
    #|
  try @pkg.parse(toml_text) catch {
    @pkg.ParseError::InvalidFormat(_) => ()  // expected
    @pkg.ParseError::UnexpectedEof => ()     // expected
  } noraise {
    toml => fail("Expected parse to fail, got \{toml.to_test_json().stringify(indent=2)}")
  }
}
```

Note: in black-box test files (`*_test.mbt`) every referenced symbol — including suberror constructors in patterns — needs the `@pkg.` prefix; unqualified use triggers the `test_unqualified_package` warning.

### 5. Validate

**Type-check the spec:**

```bash
moon check
```

Verified semantics of the spec-only state (moon 0.1.20261023 / moonc v0.10.17): unimplemented `declare`s emit the `declaration_unimplemented` **warning** (spec-only check still exits 0), but **using** an unimplemented declaration anywhere (including tests) is a hard error (exit 1). Implement the declarations in a separate file until the warnings disappear.

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

pub(all) suberror ConfigError {
  BadLine(String)
} derive(Debug, Eq)

pub fn Config::parse(text : String) -> Config raise ConfigError {
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
declare pub fn Config::parse(text : String) -> Config raise ConfigError

///|
declare pub fn Config::get_value(self : Config, key : String) -> String?
```

### To Tests

Black-box tests import the package under test and use the `@pkg.` alias for every symbol:

```mbt
///|
test "parse valid config" {
  let cfg = @config.Config::parse("key=value")
  inspect(cfg.get_value("key"), content="Some(value)")
}

///|
test "parse invalid config returns error" {
  try @config.Config::parse("invalid") catch {
    @config.ConfigError::BadLine(line) => inspect(line, content="invalid")
  } noraise {
    _ => fail("Should have failed to parse")
  }
}
```

(`inspect` renders `Option[String]` as `Some(value)` — String payloads are unquoted in current `inspect` output; prefer `debug_inspect` on types that `derive(Debug)` when exact quoting matters.)

## Tips

- **Start simple**: Begin with core functionality, add complexity incrementally
- **Use existing tests**: If tests exist, migrate and enhance them
- **Iterate**: Run `moon check` frequently to catch type errors early
- **Update snapshots**: Use `moon test -u` when output format changes
- **Document reasoning**: Add comments explaining non-obvious test cases

## Common Patterns

> **`try?` has been removed from the language** (parse error on moonc v0.10.17 with an explicit replacement hint). Use the patterns below instead.

### Testing expected success — call raising functions directly

```mbt
test "call directly" {
  let value = function_call(...)  // unexpected raise fails the test with the actual error
  inspect(value, content="...")
}
```

### Testing expected failures — `try`/`catch`/`noraise`

```mbt
try function_call(...) catch {
  @pkg.ErrorVariant(payload) => inspect(payload, content="...")  // expected error
} noraise {
  v => fail("Expected error, got \{Repr(v)}")
}
```

The `catch` must be exhaustive over the raised error type (else `partial_match`).

### Result-as-data — when the API genuinely returns `Result`

```mbt
let result = try Ok(function_call(...)) catch { e => Err(e) }
match result {
  Ok(value) => inspect(value, content="...")
  Err(e) => fail("Unexpected error: \{Repr(e)}")
}
```

### Using test JSON format

```mbt
json_inspect(value.to_test_json(), content={
  "field": { "type": "integer", "value": "42" }
})
```
