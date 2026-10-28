# Agent guidelines

Conventions for humans and agents contributing to this repository. See
[README.md](README.md) for the layout and how each part is consumed.

## Practices and catalog

* Every practice has a stable ID `PFE-<AREA>-<NNN>` in
  [`catalog.yaml`](catalog.yaml). IDs are never renumbered or reused; retire
  a practice with `status: retired`.
* Every page under `src/` must be listed in the catalog, and every skill and
  validator must be referenced by at least one practice and mention its
  practice ID(s). `uv run tools/check_catalog.py` enforces this.

## Validators

* One validator per directory under `validators/`, named `check-<topic>`. The
  directory name, the package name and the console script are identical, so
  `uvx git+...#subdirectory=validators/<name>` works without `--from`.
* Start from [`validators/_template`](validators/_template/README.md).
* Python only, standard library first. Shared code goes to
  `packages/pfe-validators-common` instead of being copied.
* Use `run_cli()` so every validator has the same interface and exit codes,
  and tag every `Finding` with its practice ID.
* Each validator ships `pyproject.toml`, `action.yml` (composite action
  running `uvx --from "${{ github.action_path }}"`), `README.md`, and
  `tests/` with good and bad fixtures.
* Add a self-test job in `.github/workflows/actions-selftest.yaml`.
* Validators that inspect a developer machine rather than repository files
  (for example `check-devenv`) set `[tool.pfe] local-only = true` in their
  `pyproject.toml`, ship no `action.yml` and are used with `uvx` only.

## Skills

* One skill per directory under `skills/`, with a `SKILL.md` whose
  frontmatter has `name` (matching the directory) and `description`.
* Skills point to the documentation and validators rather than duplicating
  the practice text.

## Checks before proposing a change

```shell
uv sync --locked
uv run ruff check && uv run ruff format --check
uv run mypy
uv run pytest
uv run tools/check_catalog.py
```

New Markdown must pass `mdl` with the repository `.mdlrc` (80-column lines,
code blocks excepted).
