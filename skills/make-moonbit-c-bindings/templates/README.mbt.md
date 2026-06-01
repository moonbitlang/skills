# library_mbt

```mbt check
///|
test "version smoke" {
  let value = version()
  inspect(value >= 0, content="true")
}
```
