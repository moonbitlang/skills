#include <stdint.h>
#include <moonbit.h>

/* Include vendored upstream headers after scripts/prepare.py copies them. */
#include "upstream#include#library.h"

typedef char library_int_must_be_i32[
  (sizeof(library_int_t) == sizeof(int32_t)) ? 1 : -1
];

MOONBIT_FFI_EXPORT int32_t library_mbt_version(void) {
  return (int32_t)library_version();
}

MOONBIT_FFI_EXPORT void library_mbt_free(void *ptr) {
  if (ptr != NULL) {
    library_free(ptr);
  }
}
