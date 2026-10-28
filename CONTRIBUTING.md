# Standards

- [Definitions](#definitions)
- [Principles](#principles)
- [Workflows](#workflows)
- [Implementation](#implementation)
- [Tests](#tests)
- [Continuous integration](#continuous-integration)
- [Publication](#publication)
- [Development environment](#development-environment)

The
[Charm development best practices](https://documentation.ubuntu.com/juju/3.6/reference/charm/index.html)
are incorporated by reference.

## Definitions

### Breaking change

A breaking change is any change that results in a deliverable that can not be
swaped by its previous version seamlessly. In the context of charms, the
following are considered breaking changes:

* Dropping or renaming  a configuration or integration
* Adding a new required configuration or integration
* Removing or changing an existing action (e.g., introducing a new required parameter)
* Introducing or modifying the structure of a secret
* Changing to an incompatible workload version
* Introducing a requirement on a juju version which was not previously required

### Tool

A tool is a project the team works on which isn't a charm, such as a GitHub
action.

### Unit Tests

These are tests that cover charm/ service functions to ensure that given a
specific context and mocked interfaces, the function returns the expected
output. Tests could cover more than one function if some of them don't include
business logic. These tests shouldn't be functional, they just ensure that the
code is doing what it's supposed to do.

### Integration Tests

Integration tests ensure that the charm integrated with its dependencies will
behave properly. It doesn't test the code in a production like environment,
meaning that we don't connect to environments with equivalent resources and
production like datasets. The integration tests will spawn specific dependencies
that could differ from the production one (e.g using localstack instead of
openstack, sqlite instead of a production grade database, ...). These tests can
be functional (they ensure that the features provided by the charm are working
as intended) or focus on checking an abstracted interface. They don't
necessarily need to ensure that the API/Service/CLI they're interacting with are
working as intended.

### End To End Tests

These are simulated user scenarios running on an environment as close as
possible to production. They ususally run on a staging environment with
preexisting data, and interact with the charm as a user would (ideally using the
juju cli). These are functional tests and ensure that the charm is working as
intended in the conditions close to production in order to detect issues related
to this environment (ressources, pre-existing conditions, migrations, ...).

### Smoke Tests

These are functional tests for business critical use cases used to ensure that
the most critical features are still working after a deployment. The
aim is to ensure that a deployment didn't impact business continuity and detect
potential defects immediately after the deployment.


## Principles

## Programming Languages and Frameworks

If we develop in many different programming languages and frameworks, the
maintenance cost increases, only those with knowledge of a given programming
language or framework can work on code bases in that programming language and
best practices and standards are difficult to set across the team.

We are a team primarily focused on developing charms, and we should follow the
recommended tools and best practices of the ecosystem we work within (and help
to improve them where appropriate). As a result, the primary programming
language we work in is Python, and the primary framework we use to develop
charms with is the [Operator
Framework](https://github.com/canonical/operator).

We will also be working on older charms which may be written in older
frameworks such as the [Reactive
Framework](https://charmsreactive.readthedocs.io/en/latest/). In some cases
we'll work on converting those to the Operator Framework but for small bug
fixes or changes this may not be the case.

As a team we'll also be exposed to a much lesser extent to other programming
languages as a result of working with specific applications that we deploy on
Juju, or via small changes to Juju itself, which is written in Go. We also
encourage exploration and experimentation in a range of programming languages
depending on the interest of the individual as part of using Canonical's
annual training budget.


## Charm Ubuntu and Python Version

Using inconsistent minor Python version for development, CI and production means
that, even if tests pass during development and CI, the charm may not work in
production.

When charms are running in production, the version of Python available to them
is dictated by the version of Ubuntu that it is running on. This is configured
in the `charmcraft.yaml` file under the `bases.build-on` and `bases.run-on`
keys. The CI should be configured to use the same version of Ubuntu as
configured under the `charmcraft.yaml` `bases.run-on` key. It is recommended
that local development be done on the version of Python that is shipped with
the Ubuntu version defined in `charmcraft.yaml` `bases.run-on`. The unit and
integration tests should be run on the same minor Python version as is shipped
with the the OS as configured under the `charmcraft.yaml` `bases.run-on` key.
With tox, for Ubuntu 22.04, this can be done using:

```
[testenv]
basepython = python3.10
```

This ensures that the tests are run on the same Python version as the charm
will be running in production, catching any issues related to mismatched Python
versions.


## Downloading Binaries

Downloading binaries is only permitted from what are classed as trusted sources.
These are:

* The Ubuntu Archives (for debian packages).
* Snaps.
  [owned by the "canonical" account](https://snapcraft.io/publisher/canonical)
* Snaps where the binary is built from a trusted and approved source.
* [PyPi](https://pypi.org/) where the binary is built from a trusted and
  approved source.

These sources are considered trusted because we are confident that we understand
the way in which they're built, and the security commitments for packages/snaps
produced by them. At any point we can rerun our builds and know that we will
pull in the latest versions of these artefacts, and that in the case of the
first two they will include security updates that Canonical stands behind.

Downloading binaries from any other sources and including them in our charms or
ROCKs exposes our end users to potential security issues either now or in the
future. We don't know the manner in which the binaries were built and don't have
confidence that they will be updated in the future in case of security
vulnerabilities that affect them.

As such, we should ensure that we’re only downloading from either the trusted
sources above, or we're downloading the source instead, verifying that download
where possible, and then building that code from source on infrastructure we
trust (e.g. Launchpad builders or GitHub self-hosted runners).

Any exception to this should be specifically noted/documented and approved by IS
Charms managers.


## Workflows

### Repository Setup

The repositories that store the source code for our charms are critical to the
ongoing development of our charms. They also enforce quality gates
and ensure business continuity. If the repository is setup poorly, it
exposes our team and Canonical to operational risks.

- GitHub should be used for charm source code and issue tracking.
- The repository should be publicly accessible.
- The `platform-engineering` team is added as maintainers.
- `is-devops-leadership` team is added as admins
  on the repository.
- Branches are auto-deleted after merging.
- The only option for merging PRs is using a squash commit.
- The default branch is called `main`.
- The default branch is protected and can only be changed using PRs.
- The number of approvers for PRs is 2.
- Approvals are not dismissed on new commits.
- PRs can only be merged if all checks pass.
- Bypassing of the rules is disabled.
- Commits must be signed.
- [Automated secret scanning](https://docs.github.com/en/code-security/secret-scanning/configuring-secret-scanning-for-your-repositories#enabling-secret-scanning-alerts-for-users)
  must be enabled.

The above configuration ensures our team processes around changes are enforced
and provides access to the repository even if some team members are unavailable.

The repository will contain a `CODEOWNERS` file in its root to automatically add
the `platform-engineering` team as reviewer

```text
*       @canonical/platform-engineering
```


### PR comments and requests for changes

The team uses Github for reviewing changes in the codebase and integrating them
within our projects. A reviewer can comment and give feedback that potentially
leads to new changes in the submitted code. Github allows you to `request
changes` on a PR, meaning it cannot be merged until the changes are accepted. As
the team is distributed, requesting changes as a default slows down merges and
requires the reviewer to approve again. Even with sufficient approvals, a PR
cannot be merged unless the requestor accepts the changes.

It is adviseable to comment and let the
engineer take action rather than request changes and block the PR. The preferred
way is to comment instead. Please note we expect the engineer
that raised the PR to deal with the comments in good faith, i.e., not just mark
them as resolved when they are not really resolved for the purpose of being able
to merge the PR. The engineer that raised the PR is responsible for closing the
comments once they are tackled.

With commenting rather than requesting changes, an engineer gives feedback and
still allows the team (based on approvals) to decide the way forward - a change
might make it in a different PR or the change might not be desireable in the
end.


## Implementation

### Random Values

While creating tests, sometimes you need to assign values to variables
or parameters in order to simulate a user behavior, for example. In this case,
instead of using constants or fixed values, consider using random ones generated
by [`secrets.token_hex()`](https://docs.python.org/3/library/secrets.html#secrets.token_hex).

Reasons:

- If you use the same fixed values in your tests every time, your tests may pass
even if there are underlying issues with your code. This can lead to false
positives and make it difficult to identify and fix real issues in your code.
- Using random values generated by secrets.token_hex() can help to prevent
collisions or conflicts between test data.
- In the case of sensitive data, if you use fixed values in your tests, there is
a risk that may be exposed or leaked, especially if your tests are run in a
shared environment.

Example:

```python
from secrets import token_hex

email = token_hex(16)
```


### File Encoding

If file encoding is not specified when interacting with a file, the default
value for the operating sytem is used. The default varies across operating
systems reducing the portability of code that does not specify a encoding
explicitly. See: <https://peps.python.org/pep-0597/>

For any file operations, specify the `utf-8` encoding where possible. For
example:

```python
with open(..., encoding="utf-8") as file:
    ...

from pathlib import Path

Path(...).read_text(encoding="utf-8")
Path(...).write_text(..., encoding="utf-8")
```

This ensures that the code we write is portable across operating systems.


### Type Hints

Python is a dynamic programming language that does not require type
declarations. Without type information, arguments might be passed to functions
that are not of the expected type (e.g., passing `None` where it is not
expected), which leads to more bugs. It also makes it more difficult to know
what functions accept as input and return as output.

Except when impractical, declare type hints on function parameters, return
values and class and instance variables. Examples of when type hints might
be impractical (not an exhaustive list):

- dictionaries with many nested dictionaries,
- decorator functions,
- when making small changes or
- contributions to projects not owned by the team.

To leverage the power of type hints, the following configuration snippet should
be added to `pyproject.toml`. This helps the user during the linting process by
ensuring that all functions, including tests, have type definitions and checks
for any typing issues even if a function does not have explicit type hints on
it.

```toml
[tool.mypy]
check_untyped_defs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

The type hints should be checked with `mypy`. More information on
type hints can be found here: [PEP 484](https://peps.python.org/pep-0484/).

This will help users know what functions expect as parameters and return and
catches more bugs earlier.

### Handling Typing Issues with python-libjuju

In tests and elsewhere when interacting with `python-libjuju`, it is a frequent
requirement to check whether certain attributes are `None`. Doing this in many
tests reduces the readability of the code.

Instead of putting `assert ops_test.model` in individual tests, write a fixture:

```Python
@pytest_asyncio.fixture(scope="module", name="model")
async def model_fixture(ops_test: pytest_operator.plugin.OpsTest) -> ops.model.Model:
    """The current test model."""
    assert ops_test.model
    return ops_test.model
```

Instead of putting `assert hasattr(app, "units")`, write a fixture:

```Python
@pytest_asyncio.fixture(scope="function", name="units")
async def units_fixture(app: ops.model.Application) -> list[ops.model.Unit]:
    """The current test unit."""
    assert hasattr(app, "units")
    return app.units
```

This reduces code duplication which increases the readability of the tests.


### TODO's in source code

Engineers tend to add TODO comments in the source code for different purposes,
e.g.:

- To remind themselves to do something before merging a PR.
- To acknowledge that the current state of the code needs improvement, but it
depends on  something external (e.g., a feature not being ready yet).
- To indicate that refactoring is necessary, but the cost is too high
- (e.g., development efforts or the PR becoming too large).

In general, comments tend to be inaccurate because code changes faster than
comments are updated. The same applies to TODOs.
They tend to stick around forever and confuse future engineers,
who don't know what the TODO is about or if they should take action.
Therefore, TODOs should preferably be added to the product backlog
(e.g., Jira).
It is acceptable to add TODOs while developing a feature on a feature branch,
but they should be removed before merging the PR.


### Function and Method Ordering

Without a logical order, it can be difficult to follow modules and classes as
the number of functions or methods on them grow increasing the maintenance
burden of the code.

Functions should be ordered according to the
["step-down"](https://dzone.com/articles/the-stepdown-rule) rule.
This means that a module should be readable from top to bottom,
with functions ordered by level of abstraction, from general to specific.
A calling function should always be above the called function.
Functions should also be grouped together logically. If functions have a
similar purpose, they should be grouped together.

On classes, the `__init__` method should come first followed by any other
factory methods, such as `from_charm`. The rest of the methods on a class should
be ordered similar to the guidance for function ordering on modules.

This will make it easier for readers to understand the code reducing the
maintenance cost.


### Non Compliant Code

Standards and best practices evolve over time which means that code already
written may not comply with a new standard. If this is wide spread, it can lead
to a culture of ignoring the standard and can degreade the value of team
standards.

At a minimum, any code changed in a pull request complies with team standards.
The team values initiative updating code to comply with new standards and
recognises that this needs to be balanced with other priorities, such as
delivering new features of fixing bugs. If possible, standards should be
enforced automatically by the CI system.

This ensures that:

1. code under active development is likely to be compliant with team standards,
2. less time is spent updating code that doesn't need to be updated frequently
   to new standards,
3. it encourages the team to go out of their way to implement any new standards
   as individuals see value in doing so and
4. compliance is enforced using CI where possible.


## Tests

### Test Structure

Tests that are difficult to understand are of lower value because if they fail
it is difficult to understand why they fail.

The docstring of a test has 3 sections, *arrange*, *act* and *assert*. Arrange
explains the pre-conditions required for the test, act explains what steps the
test performs and assert explains what the state must be after all actions are
complete. If the description for a section is longer than one line, any
additional lines are indented by the default indentation of the file. The test
code is separated into blocks for each section. For example:

```Python
def test_something():
    """
    arrange: given 2 numbers
    act: when they are added
    assert: the result must be the sum of the 2 numbers. If a description spans
        multiple lines, lines after the first should be indented by the default
        spacing of the file to indicate that the description continues.
    """
    num_a = 1
    num_b = 2

    result = num_a + num_b

    assert result == 3
```

Whilst this standard is usually valuable, there are cases where it imposes
unreasonable constraints. An example is complex functional tests that check
multiple interactions that require individual arrange, act, assert blocks
because they, for example, build on each other. In those cases, apply judgement
keeping in mind the option of breaking up the test into multiple tests.

This structure makes it easy to understand what is required before test
execution, how the test works and what it checks for in the end.


### Test Exception Raised

Testing an exception being raised might not be enough as a type of exception
can be raised due to multiple reasons. E.g., a function could raise `ValueError`
for different arguments.

The property of the exception being raised should be asserted against as well.
A common test would be the string representation of the exception. Using the
following `pytest` example:

```Python
def something(a: int, b: bool):
  """Do something."""
  if a >= 5:
    raise ValueError("Argument a must be less than 5")
  if b:
    raise ValueError("Some other error message")
  # Rest of the function...


def test_something():
  """Test the something function."""
  with pytest.raises(ValueError) as err:
      something(a=10, b=False)
  assert "Argument a" in str(err.value)
  assert "less than 5" in str(err.value)
```

In the above example, the `something` function could have thrown a different
`ValueError` related to the argument `b`. Testing the string representation of
the `ValueError` ensures the proper type of error is being tested against.


### Test Fixture

When declaring fixture functions and requesting them in the same Python module,
there is a risk of accidentally using the fixture function declared in the
global scope instead of requesting it in the test case function parameters.

To prevent this problem, it is recommended to add a "fixture" prefix or suffix
to the fixture function name and use the `name` argument in the `pytest.fixture`
decorator to name the fixture.

Here's an example of using the `name` argument in `pytest.fixture`:

```python
import pytest

@pytest.fixture(name="app")
def app_fixture():
    return "app"

def test_my_fixture(app):
    assert app == "app"
```


### Test Coverage

Unit tests check whether the intended functionality has been implemented. This
is valuable to reduce bugs and checking whether any changes to the code break
any features. The benefits of testing are roughly proportional to the test
coverage percentage, the lower the coverage the higher the chances of bugs and
the higher the risk of code changes.

The team has a coverage percentage which is the maximum of 85% and the current
percentage on the default branch, usually `main`. Any code that is already
covered on the default branch should not cease to be covered by new commits to
main, such as through a pull request. Any coverage exclusion should have an
explanatory comment, such as:

```Python
# Exclude from coverage since unit tests should not run as __main__
if __name__ == "__main__":  # pragma: no cover
   ...
```

To enforce this, the `pyproject.toml` file should include the following
configuration:

```toml
[tool.coverage.report]
fail_under = <maximum of coverage % on main and 85%>
```

This value should be updated in each PR to reflect any increase in coverage
compared to the main branch as a result of the PR.

This ensures a high coverage minimum and no coverage regression.


## Static Code Analysis

There are many potential problems with code that can be spotted based on
analysing source code without executing it, such as mismatches in type
expectations. Additionally, code formatting discussions during PRs can be
cumbersome and take up a lot of time.

The automated static code analysis tools that should be used locally and
enforced through the CI system are listed in the
[`lint`](https://github.com/canonical/platform-engineering-charm-template/blob/main/tox.toml#L44)
section and the
[`static`](https://github.com/canonical/platform-engineering-charm-template/blob/main/tox.toml#L107)
section of our charm template.

Note:

- Disabling checks should be the last resort, alternatives such as refactoring
  the code should be considered first. For example, instead of disabling the
  `too-many-arguments` `pylint` rule, consider grouping the arguments, e.g.,
  using a `typing.NamedTuple`.
- When disabling a rule, if the tool allows for it, use the name of the rule
  rather than the code. For example, for `pylint`, always use the name of the
  rule (like `too-many-arguments`) rather than the code. This makes it easier
  for readers to know which rule is being disabled and potentially why.
- If a rule is disabled, a comment should to be included above the line
  disabling the rule explaining why the rule is disabled. This will mean that
  future readers don't have to guess why it was disabled and can also consider
  whether the disable can be removed. For rules tied to import, it may be better
  to comment on each usage rather than on the import. Note that comments for
  import must be added at the start of an import section to prevent the
  formatter from messing up the import sections:

  ```python
  # Comment explaining why subprocess is imported.
  import logging
  import os
  import subprocess  # nosec B404
  import time
  ```

- Disabling should be done as specifically as possible. That means, disabling
  the narrowest rule possible on the narrowest section of code. For example,
  instead of disabling a rule entirely, disable it on a file. Instead of
  disabling a rule for a file, disable it for just a line of code. The preferred
  way is to disable on a line of code:

  ```python
  <code>  # disable rule
  ```

  If a rule needs to be disabled for a section, re-enable it as soon as
  possible:

  ```python
  # disable rule
  <code>
  # enable rule
  ```

This ensures consistency across our projects, catches many potential bugs
before code is deployed and simplifies PRs.


## Continuous integration

### CI-CD

The team maintains a number of repositories which are generally quite similar.
If each of the repositories maintains its own workflows, it is difficult to
introduce new tools across the repositories owned by the team. Additionally, if
shared workflows are unreliable, the team is unable to consistently merge
changes and have confidence in the CI-CD.

Use [`operator-workflows`](https://github.com/canonical/operator-workflows) for
the CI-CD of any repositories owned by the team. Even if the repository is not a
charm, such as a GitHub action, use it to the extent possible. If a repository
has unique requirements for certain workflows, use the `operator-workflows` as
much as possible. Consider proposing changes to `operator-workflows` instead of
doing something custom in a repository. Also consider whether to make partial
use of workflows in `operator-workflows` and add anything that can't be done
with `operator-workflows` to the individual repository, if the CI-CD
requirements are unique to a repository.

For any changes to `operator-workflows`, add tests just like we expect for any
other repository.

Using shared workflows will make it easy to evolve the workflows used by all our
repositories and roll out new tooling and checks across them. It will also avoid
duplication in many repositories.

Adding tests to `operator-workflows` will ensure stability of the workflows and
provide examples for how to use them.


### Failing Status Checks

The team uses GitHub actions to run CI which includes automated status checks
to verify the code works as expected. If PRs are merged with failing status
checks, there are potential bugs in the code which may lead to downtime or
other operational issues.

PRs should only be merged if all status checks pass. Changes should only be landed
if are urgently needed in production and the failures can't be fixed in a reasonable
timeline. Some examples include:
* If the team has recently taken over a new charm and changes are urgently
needed and the test suit of the existing charm is failing for spurious reasons.
* A tool we depend on is not working, no previous working version is available
and a change is urgently needed to fix a critical issue in production.

Even in the above cases it is not clear whether it is reasonable to merge a PR
with failing checks due to the high risks this entails.
Judgement is required in these cases weighing the
risks of introducing bugs with the urgency and impact of the underlying need to
land the change.

Before merging the PR with failing status checks evaluate the following options:

* Change the code to fix the problem.
* Re-run the test in case of suspected flakiness.
* Wait for an upstream fix for the issue.
* Remove the test if it doesn't add value.
* Disable the status check (e.g., mark the test as
  [`xfail`](https://docs.pytest.org/en/7.1.x/how-to/skipping.html)). This
  should not be done lightly as the value the status check provides to the team
  is lost and tracking a disabled test is challenging.

If it is deemed that a change should land despite a failing status check, the
following artifacts should be added to the PR:

* If the status check can be run in another way, e.g. locally, a copy of the run
  (e.g., a copy of the terminal output) including the git commit SHA which is
  being approved and the status check passing
* The reason why the PR needs to be merged without the status check passing
  (e.g., because the fix is needed in production and the status check is failing
  due to problems with GitHub).

The PR should be otherwise ready to be merged (e.g., has been approved).

Note that only repository admins will be able to force merge pull requests.

Resolving the underlying reason the status check is failing should be high
priority so that the team can rely on the automation again.

This will ensure that we minimise the number of bugs in our code and tooling.


## Publication

### Publishing to a channel

Charms published to tracks different from `latest` should guarantee seemlessly
upgrades between revisions, that is, revisions should not introduce breaking
changes.

## Development environment

### Development Environment: opencode

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
