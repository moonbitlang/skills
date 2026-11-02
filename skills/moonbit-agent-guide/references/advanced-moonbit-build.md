## Conditional Compilation

Target specific backends/modes in `moon.pkg`. Legacy `moon.pkg.json` files remain supported; use the current format for new examples.

The configuration examples below are independent. When combining them in one package, merge their fields into a single `options(...)` block.

```moonbit
options(
  targets: {
    "wasm_only.mbt": ["wasm"],
    "js_only.mbt": ["js"],
    "debug_only.mbt": ["debug"],
    "wasm_or_js.mbt": ["wasm", "js"], // for wasm or js backend
    "not_js.mbt": ["not", "js"], // for nonjs backend
    "complex.mbt": ["or", ["and", "wasm", "release"], ["and", "js", "debug"]] // more complex conditions
  }
)
```

**Available conditions:**

- **Backends**: `"wasm"`, `"wasm-gc"`, `"js"`, `"native"`
- **Build modes**: `"debug"`, `"release"`
- **Logical operators**: `"and"`, `"or"`, `"not"`

## Link Configuration

### Package Type and Exports

Declare `pkgtype(kind: "foreign_library")` in `moon.pkg` when exporting functions for a foreign host. Use `pkgtype(kind: "executable")` for a program with `main`; `library` is the default for ordinary MoonBit packages. Choose one kind per package. The old `options(link: true)` and `options("is-main": true)` forms are legacy.

Prefer `#export_name` for new exports:

```moonbit
pkgtype(kind: "foreign_library")
```

```mbt nocheck
///|
#export_name("increment")
pub fn increment(value : Int32) -> Int32 {
  value + 1
}
```

The exported function must be public, non-generic, and have no optional parameters. Export names currently must be unique C identifiers, even for Wasm and JavaScript. Exports belong to the artifact-producing package: wrap dependency functions there if they must be exported. Native static/shared library output is not currently supported; validate foreign-library artifacts on Wasm or JavaScript.

### Backend Link Options

Keep backend-specific settings in `options(link: { ... })`. This object configures linking rather than selecting the package type. Legacy `exports` lists remain supported, but use `#export_name` for new exports.

```moonbit
options(
  link: {
    "wasm": {
      "heap-start-address": 1024, // Memory layout
      "import-memory": {
        // Import external memory
        "module": "env",
        "name": "memory"
      },
      "export-memory-name": "memory" // Export memory with name
    },
    "wasm-gc": {
      "use-js-builtin-string": true, // JS String Builtin support
      "imported-string-constants": "_" // String namespace
    },
    "js": {
      "format": "esm" // "esm", "cjs", or "iife"
    },
    "native": {
      "cc": "gcc", // C compiler
      "cc-flags": "-O2 -DMOONBIT", // Compile flags
      "cc-link-flags": "-s" // Link flags
    }
  }
)
```

## Warning Control

Disable specific warnings in `moon.pkg`:

```moonbit
warnings = "-unused_value-unused_package"
```

**Common warning names:**

- `unused_value` - Unused function or variable
- `partial_match` - Partial pattern matching
- `unreachable_code` - Unreachable code
- `unused_package` - Unused package

Use `moon explain --diagnostic` to list warnings and `moon explain --diagnostic <name>` for details. Use `--deny-warn` on validation commands to make enabled warnings fail the build. Legacy JSON configurations use `"warn-list"` instead of `warnings`.

## Pre-build Commands

Declare a reusable rule and apply it with `dev_build` in `moon.pkg` to embed external files as MoonBit code:

```moonbit
rule(
  name: "embed-text",
  command: ":embed -i $input -o $output --name data --text",
)
dev_build(rule: "embed-text", input: "data.txt", output: "embedded.mbt")
```

Paths are relative to the module root. These commands run during package development, not when downstream users build the package as a dependency. Commit generated outputs for downstream builds. The old JSON `"pre-build"` configuration is deprecated.

Generated code example:

```mbt check
///|
let data : String =
  #|hello,
  #|world
  #|
```
