# check-devenv

Checks that the local opencode development environment follows the team
standard.

* **Practice:** `PFE-DEV-001`,
  [Development environment: opencode](../../src/devenv/100-opencode.md)
* **Checks:**
  * the `opencode` snap is installed at version 1.19.4 or newer;
  * LSP is enabled in the effective opencode configuration;
  * the default model is Claude Sonnet 5.5, from any provider.
* The configuration is read from `opencode debug config`, so global, project
  and managed configuration are all taken into account.

This validator inspects a developer machine, not repository files, so it is
only meant to be run with `uvx` and has no GitHub Action.

## Usage

```shell
uvx --from 'git+https://github.com/canonical/platform-engineering-contributing-guide@v1#subdirectory=validators/check-devenv' \
  check-devenv [--format text|github|json] [PROJECT_DIR]
```

`PROJECT_DIR` (default: current directory) is where `opencode debug config`
runs, so that the project's `opencode.json` is included.

## Exit codes

`0` compliant, `1` findings reported, `2` a command failed or returned
unexpected output.
