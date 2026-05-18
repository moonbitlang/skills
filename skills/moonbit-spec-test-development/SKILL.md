---
name: moonbit-spec-test-development
description: Create formal spec-driven MoonBit APIs and test suites. Use when asked to set up a spec.mbt, spec-driven tests, or a formal contract-first workflow (e.g., "set up a formal spec & test suite for Yaml in MoonBit"), including moon.mod.json/moon.pkg.json scaffolding and guidance to implement in separate files.
---

# MoonBit Spec & Test Development

## Overview
Define a formal API contract in `<pkg>_spec.mbt`, write type-checked tests against it, and scaffold a minimal MoonBit module so `moon check` passes before implementation work begins.

## Workflow

###  Confirm API surface (if needed)
- Infer the package name from context; only ask if ambiguous.
- Confirm the API surface: core types, entry points, error types, and any versioning needs.

###  Scaffold the module using `moon new` (preferred for new projects)
- If you didn't use `moon new`, fall back to the `moon.mod.json` and `moon.pkg.json` templates.

###  Write the formal spec (`<pkg>_spec.mbt`)
- Use `#declaration_only` for all types/functions that will be implemented later.
- Functions with `#declaration_only` must still have a body: `{ ... }`.
- Keep the spec as the contract: treat it as read-only after creation; implementation goes in new files under the same package.
- Use `pub(all)` for types you need to construct in tests; keep `pub` for opaque types.


###  Write spec-driven tests
- Create `<pkg>_easy_test.mbt`, `<pkg>_mid_test.mbt`, and `<pkg>_difficult_test.mbt` (or similar) in the same package.
- Prefer black-box tests using public APIs; use `@json.inspect(...)` for complex values.
- Try to make the tests rich enough to validate the spec surface.

###  Validate
- Run `moon check` to confirm the spec + tests type-check.
- Run `moon test` only after some implementations exist

## Templates
- See `references/templates.md` for scaffolding and file templates.
