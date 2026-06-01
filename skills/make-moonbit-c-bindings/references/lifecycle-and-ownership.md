# Lifecycle And Ownership

MoonBit C bindings are mostly lifecycle engineering. Do not start by translating
headers into extern declarations. First answer: who owns every pointer, how long
it stays valid, and who frees it.

## Call-Scoped Borrowing

Use `#borrow(param)` only when C reads or writes through a MoonBit object during
the call and does not store the pointer after returning.

Good cases:

- Input arrays that C scans during the call.
- Output `Ref[Int]` parameters.
- Temporary `Bytes` passed as `const char *`.

Bad cases:

- C stores a pointer for later.
- C calls back asynchronously.
- C keeps an input buffer in an internal handle.

If unsure, do not use `#borrow`. Either copy the data into C-owned memory or
make lifetime explicit with a handle.

## Owned Parameters

Use `#owned(param)` only when ownership transfers to C. C must eventually call
`moonbit_decref(param)`.

Rules:

- Every `#owned` parameter needs a clear release path.
- Pair `moonbit_incref` and `moonbit_decref` when C keeps a MoonBit object.
- Missing `decref` leaks; missing `incref` risks use-after-free.

## External Objects

Use `moonbit_make_external_object(finalizer, size)` when a C resource should be
freed by MoonBit GC.

```c
typedef struct {
  lib_handle_t *handle;
} MoonBitHandle;

static void handle_finalize(void *object) {
  MoonBitHandle *self = (MoonBitHandle *)object;
  if (self->handle != NULL) {
    lib_destroy(self->handle);
    self->handle = NULL;
  }
}
```

Important: the finalizer must release only the inner C resource. Do not call
`free(object)`: the MoonBit GC owns the external object container.

## `#external` C-Managed Handles

Use `#external` on an opaque MoonBit type when C owns the pointer and the user
must call an explicit destroy function.

```mbt
///|
#external
type RawHandle
```

This is appropriate when the C API already has clear `create` / `destroy`
functions and the wrapper should not involve MoonBit GC finalizers.

## Value-As-Bytes

For small C structs with no inner pointers and no cleanup, store the value in
MoonBit-managed bytes:

```c
MOONBIT_FFI_EXPORT
void *settings_new(void) {
  return moonbit_make_bytes(sizeof(settings_t), 0);
}
```

Do not use this for structs that contain heap pointers, file descriptors, or
resources requiring cleanup. Use external objects instead.

## C-Allocated Output

When C returns allocated arrays or strings:

1. Copy into MoonBit-owned arrays or `Bytes`.
2. Free the C allocation using the library's matching free function.
3. Return only MoonBit-owned data from the safe API.

For library-specific allocators, always use the matching deallocator. Do not mix
`free`, `lib_free`, `delete`, and custom arenas.

## Optional Pointers

Prefer one representation:

- MoonBit: `None` becomes an empty `FixedArray`.
- C wrapper: `Moonbit_array_length(arr) > 0 ? arr : NULL`.

Avoid extra `Bool use_x` parameters across FFI. They make ABI order bugs easy
and duplicate information already encoded by the array length.

## Mutating C APIs

Some C options mutate input arrays in place, renumber indices, or reuse output
buffers as scratch space. Do not expose these modes unless the MoonBit API makes
the mutation explicit and validates the preconditions.

If a C function mutates inputs but the MoonBit domain type should be immutable,
copy before calling C.

## Callback Lifetimes

For callbacks:

- Keep callback state alive for at least as long as C can call it.
- `moonbit_incref` stored MoonBit callback state before handing it to C.
- `moonbit_decref` it in the C-side finalizer or unregister function.
- Document whether callbacks may run synchronously, asynchronously, or from
  foreign threads.

If the C library can call from arbitrary native threads, verify MoonBit runtime
support before exposing that API.
