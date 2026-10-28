# check-todos

Reports `TODO` and `FIXME` comments left in source code.

* **Practice:**
  [`PFE-IMPL-004` TODOs in source code](../../src/implementation/400-todos.md)
* **Scope:** common source and configuration file types (`.py`, `.go`,
  `.sh`, `.ts`, `.yaml`, `.toml`, ...). Markdown and other prose are ignored.
  Files ignored by git are skipped.

## Usage

### uvx

```shell
uvx --from 'git+https://github.com/canonical/platform-engineering-contributing-guide@v1#subdirectory=validators/check-todos' \
  check-todos [--format text|github|json] [PATH ...]
```

### GitHub Actions

```yaml
- uses: actions/checkout@v7
- uses: canonical/platform-engineering-contributing-guide/validators/check-todos@v1
  with:
    paths: src tests   # optional, default "."
```

| Input            | Default  | Description                          |
|------------------|----------|--------------------------------------|
| `paths`          | `.`      | Space-separated files or directories |
| `format`         | `github` | `github`, `text` or `json`           |
| `python-version` | `3.12`   | Python used to run the validator     |

## Exit codes

`0` no findings, `1` findings reported, `2` usage or runtime error.
