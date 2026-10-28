---
name: pfe-practices
description: >-
  Use when writing, reviewing or fixing code in a Canonical Platform
  Engineering repository, to find the applicable engineering practices
  (PFE-* IDs), read their rationale, and run the matching compliance
  validators before proposing changes.
---

# Platform Engineering practices

The practices are the team's source of truth for how code is written, tested,
reviewed and published. They live in
[canonical/platform-engineering-contributing-guide][repo].

## Workflow

1. **Find the practices that apply.** Read `catalog.yaml` at the root of the
   repository above. Each entry has a stable ID (`PFE-<AREA>-<NNN>`), a title,
   the path to its documentation (`doc`), and optionally `skills` and
   `validators`. Pick entries by area and title that match the task. Do not
   load every doc.
2. **Read the documentation** of the selected practices (`doc` path). The doc
   is authoritative. If it conflicts with this skill, the doc wins.
3. **Run the validators** listed for those practices against the files you
   changed, and fix every finding before proposing the change:

   ```shell
   uvx --from 'git+https://github.com/canonical/platform-engineering-contributing-guide@main#subdirectory=validators/<validator>' \
     <validator> --format text <paths>
   ```

   Exit code `0` means compliant, `1` means findings to fix, `2` means the
   tool failed: report it, do not treat it as a pass.
4. **Cite practice IDs** in review comments and commit or PR descriptions
   when a change is motivated by a practice, for example
   "Removes TODO comments (PFE-IMPL-004)".

## Example

Before opening a pull request, check that no TODO comments remain
(PFE-IMPL-004):

```shell
uvx --from 'git+https://github.com/canonical/platform-engineering-contributing-guide@main#subdirectory=validators/check-todos' \
  check-todos --format text .
```

Move each reported TODO to the backlog (e.g. Jira) and remove the comment.

When setting up or troubleshooting a developer machine, run `check-devenv`
(PFE-DEV-001) the same way to verify the opencode snap version, LSP and
default model.

[repo]: https://github.com/canonical/platform-engineering-contributing-guide
