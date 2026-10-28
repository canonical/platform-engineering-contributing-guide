# Development Environment: opencode

Engineers use the opencode coding agent with the team's skills and
validators. Different versions, missing language server feedback and
different default models lead to inconsistent results and make problems hard
to reproduce.

The development environment must meet all of the following:

- opencode is installed as a snap, at version 1.19.4 or newer
  (`sudo snap install opencode --classic`).
- LSP is enabled in the opencode configuration: `lsp` is `true` or an object.
- The default `model` is Claude Sonnet 5.5, from any provider, for example
  `github-copilot/claude-sonnet-5.5` or `anthropic/claude-sonnet-5-5`.

For example, in `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": true,
  "model": "github-copilot/claude-sonnet-5.5"
}
```

Verify the environment with the `check-devenv` validator, run from the
project directory:

```shell
uvx --from 'git+https://github.com/canonical/platform-engineering-contributing-guide@main#subdirectory=validators/check-devenv' \
  check-devenv --format text .
```

The snap keeps opencode up to date and gives everyone the same build. LSP
diagnostics give the agent immediate feedback on the code it writes. A shared
default model makes the agent's behaviour consistent across the team.
