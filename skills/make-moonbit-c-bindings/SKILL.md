---
name: make-moonbit-c-bindings
description: Guides agents through complete, maintainable MoonBit bindings for C/C++ libraries, from upstream source survey through vendoring, safe API design, documentation tests, and ASan validation. Use when creating or hardening MoonBit native FFI bindings, wrapping C APIs, vendoring C sources into native-stub, or turning a C library into a MoonBit package.
---

# Make MoonBit C Bindings

Use this skill for end-to-end binding projects. Also read `moonbit-c-binding`
before implementation for low-level FFI syntax, ownership annotations, and
`moonbit.h` details.

## Quick Start
1. Clone or inspect the upstream C/C++ project in a temporary directory.
2. Identify the public header(s), generated config headers, source layout,
   allocator API, and build-time type widths.
3. Decide the safe MoonBit API surface; do not mechanically expose every C API.
4. Vendor sources with `templates/prepare.py` or link to a system library only
   when that is explicitly desired.
5. Write a thin C wrapper, private MoonBit externs, and safe public MoonBit
   wrappers.
6. Validate with `moon check`, native tests, ASan, `moon info`, and vendoring
   script idempotency.

## Binding Architecture

Prefer this layout, adapting names to the library. Start from bundled templates
instead of rewriting scaffolding from scratch:

```text
scripts/prepare.py          # optional: pinned upstream download + generated stubs
moon.mod.json               # preferred/supported native targets
src/moon.pkg                # native-stub list and file target gates
src/wrapper.c               # ABI normalization and ownership boundaries
src/ffi.mbt                 # private extern "c" declarations
src/<domain>.mbt            # safe public MoonBit API
src/<domain>_test.mbt       # regression tests
src/README.mbt.md           # tested documentation examples
README.md -> src/README.mbt.md
```

Template mapping:
- `templates/prepare.py` -> `scripts/prepare.py`
- `templates/moon.mod.json` -> `moon.mod.json`
- `templates/moon.pkg` -> `src/moon.pkg`
- `templates/wrapper.c` -> `src/wrapper.c`
- `templates/ffi.mbt` -> `src/ffi.mbt`
- `templates/api.mbt` -> `src/<domain>.mbt`
- `templates/README.mbt.md` -> `src/README.mbt.md`

For ASan validation, copy or invoke the companion runner from
`moonbit-c-binding/scripts/run-asan.py` as `scripts/run-asan.py`; do not invent
a new ASan patching script unless that runner cannot fit the project.

## Workflow

### 1. Survey Upstream

- Read public headers first; they define the binding contract.
- Record configured widths for project-specific typedefs: index types, scalar
  types, size/count types, handle types, enum backing types, and callbacks.
- Separate library APIs from CLI-only, internal, generated, or test code.
- Look for functions that allocate memory, mutate inputs, store callbacks, or
  require paired `destroy/free` calls.

### 2. Design The MoonBit API

- Expose domain-specific MoonBit types that match the current C library instead
  of raw pointers and arrays where possible.
- Validate shapes and option lengths before entering C.
- Omit unsafe or misleading C features when the safe wrapper cannot uphold
  their semantics.
- Map C status codes into MoonBit errors; return structured result records for
  output parameters.

### 3. Vendor Or Link

- For portable packages, vendor C sources into `native-stub` with a pinned
  revision and a repeatable script.
- Flatten sources if MoonBit requires stubs in one package directory, and
  rewrite includes deterministically.
- Generate configured headers instead of relying on ad hoc compiler flags.
- Ensure the vendoring script can be rerun with no tracked diff.

### 4. Build The FFI Boundary

- C wrapper owns ABI normalization: type-width assertions, optional pointer
  conversion, output copying, and freeing C-allocated memory.
- `ffi.mbt` should keep externs private and use `#borrow` / `#owned` explicitly.
- Public MoonBit files should call only safe wrapper functions, never raw C APIs.
- Avoid extra Boolean sentinel parameters for optional arrays; prefer empty
  MoonBit arrays and check `Moonbit_array_length` in C.

### 5. Validate

Run, at minimum:

```bash
moon fmt
moon check --target all --warn-list +73
moon test --target native
python3 scripts/run-asan.py
moon info --target native
python3 scripts/prepare.py
git status --short
```

For native-only packages, set `"preferred-target": "native"` and
the smallest true `"supported-targets"` value in `moon.mod.json`.

## Required References
[Lifecycle And Ownership](references/lifecycle-and-ownership.md);
[Vendoring And Package Setup](references/vendoring-and-package-setup.md);
[Testing And Documentation](references/testing-and-documentation.md).
