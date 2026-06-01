# Testing And Documentation

C bindings need tests for both API behavior and memory/lifecycle mistakes.

## Test Layers

Use these layers:

1. Unit tests for safe MoonBit validation.
2. Smoke tests for every public C-backed function.
3. Regression tests for every FFI bug fixed.
4. ASan tests for C memory safety.
5. `README.mbt.md` doctests for public examples.
6. Idempotency tests for vendoring scripts.

## What To Test

Test at least:

- Invalid input rejected before FFI.
- Empty inputs when the C library cannot handle them.
- Optional arrays passed as absent and present.
- Weighted and unweighted modes.
- Output array lengths and basic value ranges.
- Result structs containing output parameters.
- C-allocated return memory copied and freed.
- Public options that should affect behavior.
- Public options intentionally not exposed because they are unsafe or no-op.

When a binding bug is found, add a focused regression test before or with the
fix. Common examples: swapped C arguments, wrong output length, wrong optional
pointer, and missing deallocator.

## AddressSanitizer

Run native tests under ASan. A practical script usually:

- Temporarily forces clang as the C compiler.
- Disables `tcc -run` when needed.
- Sets `MOON_CC` / `MOON_AR`.
- Adds ASan compiler and linker flags.
- Restores `moon.pkg` after running.
- On macOS, sets `DYLD_INSERT_LIBRARIES` when the ASan runtime requires it.

Recommended command, using the repository's ASan runner:

```bash
python3 scripts/run-asan.py
```

Copy `moonbit-c-binding/scripts/run-asan.py` into the target repository as
`scripts/run-asan.py` unless the project already has an equivalent runner.

If ASan finds an issue, fix the root cause. Do not hide it with flags unless the
flag documents a platform limitation such as unsupported leak detection.

## README.mbt.md

Create tested documentation:

```text
src/README.mbt.md
README.md -> src/README.mbt.md
```

Use `mbt check` blocks:

````markdown
```mbt check
///|
test "example" {
  let value = replace_with_real_package_api()
  inspect(value, content="...")
}
```
````

For packages with `"source": "src"`, put `README.mbt.md` under `src/` so it is
part of the package. If the package is native-only, ensure module-level
`"supported-targets"` prevents wasm/js doctest checks.

## Standard Validation Gate

Before finishing, run:

```bash
moon fmt
moon check --target all --warn-list +73
moon test --target native
python3 scripts/run-asan.py
moon info --target native
python3 scripts/prepare.py
git status --short
```

The final `git status --short` should be clean after committing, or should show
only expected uncommitted work when the user did not ask for a commit.

## Review Checklist

- Public API is safe and honest; unsafe C modes are omitted or explicit.
- Extern declarations are private.
- Non-primitive FFI parameters have ownership annotations.
- Every C allocation has the matching free path.
- Every stored MoonBit object has a matching incref/decref strategy.
- `pkg.generated.mbti` reflects intended public API.
- `README.mbt.md` examples run.
- Vendoring script is repeatable.
- ASan passes.
