# Templates

Use these as starting points. Replace placeholders and keep `///|` between top-level items.
Replace `<pkg>` with the package name (for example, `yaml` → `yaml_spec.mbt`).
If you ran `moon new`, `moon.mod.json` and `moon.pkg.json` are already created.

## moon.mod.json
```json
{
  "name": "username/<project>",
  "version": "0.1.0",
  "source": ".",
  "deps": {}
}
```

## moon.pkg.json
```json
{}
```

## <pkg>_spec.mbt (skeleton)
```mbt
///|
/// Formal error type for parsing.
pub(all) suberror ParseError {
  Invalid(String)
} derive(Show, Eq, ToJson)

///|
/// Opaque placeholder type.
#declaration_only
pub type Yaml

///|
/// Convert to a readable string.
#declaration_only
pub fn Yaml::to_string(value : Yaml) -> String raise {
  ...
}

///|
/// Parse YAML content.
#declaration_only
pub fn parse_yaml(input : String) -> Yaml raise ParseError {
  ...
}
```

## <pkg>_easy_test.mbt 

```mbt
///|
test "spec parses simple yaml" {
  let result : Result[Yaml, ParseError] = try? parse_yaml("a: 1")
  ignore(result)
}
... // more tests
```

## <pkg>_mid_test.mbt 

```mbt
///|
test "spec handles lists in yaml" {
  let result : Result[Yaml, ParseError] = try? parse_yaml("items:\n  - one\n  - two\n  - three")
  ignore(result)
}
... // more tests
```

## <pkg>_difficult_test.mbt 
```mbt
///|
test "spec handles nested yaml" {
  let result : Result[Yaml, ParseError] = try? parse_yaml("a:\n  b: [1, 2]")
  ignore(result)
}
... // more tests
```

## <pkg>_feature_test.mbt (Additional tests added by Agents)

```mbt
///|
test "parse_yaml returns expected structure" {
  let value = parse_yaml("a: 1")
  @json.inspect(value, content={ "a": 1 })
}
```
