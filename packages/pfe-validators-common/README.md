# pfe-validators-common

Shared library for the validators in [`validators/`](../../validators).
It provides:

* `Finding` / `Severity`: the result model every validator emits.
* `iter_files()`: file discovery that respects `.gitignore` inside a git
  repository.
* `run_cli()`: a standard command line (`paths...`,
  `--format text|github|json`) with consistent exit codes: `0` no findings,
  `1` findings reported, `2` usage or runtime error.

Validators depend on it through the uv workspace
(`pfe-validators-common = { workspace = true }`). When a validator is installed
from git with `#subdirectory=`, uv resolves this dependency from the same
commit.
