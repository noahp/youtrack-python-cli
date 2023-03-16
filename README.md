[![GitHub](https://img.shields.io/badge/GitHub-noahp/youtrack--python--cli-8da0cb?style=for-the-badge&logo=github)](https://github.com/noahp/youtrack-python-cli)
[![PyPI
version](https://img.shields.io/pypi/v/youtrack-python-cli.svg?style=for-the-badge&logo=PyPi&logoColor=white)](https://pypi.org/project/youtrack-python-cli/)
[![PyPI
pyversions](https://img.shields.io/pypi/pyversions/youtrack-python-cli.svg?style=for-the-badge&logo=python&logoColor=white&color=ff69b4)](https://pypi.python.org/pypi/youtrack-python-cli/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/noahp/youtrack-python-cli/main.yml?branch=main&logo=github-actions&logoColor=white&style=for-the-badge)](https://github.com/noahp/youtrack-python-cli/actions)
[![codecov](https://img.shields.io/codecov/c/github/noahp/youtrack-python-cli.svg?style=for-the-badge&logo=codecov)](https://codecov.io/gh/noahp/youtrack-python-cli)

# YouTrack Python CLI

## Installation

```bash
❯ pip install youtrack-python-cli
# OR, if you use virtualenvs or conda envs in your working repo, use pipx:
❯ pipx install youtrack-python-cli
```

## Configuration

The script needs a YouTrack URL to target API requests, and a token for auth.

3 configuration methods:

1. set into current repo's git config:

   ```bash
   ❯ git config youtrack.token "$YOUTRACK_TOKEN"
   ❯ git config youtrack.url https://your-youtrack-server/api
   ```

2. set via environment variables, `YOUTRACK_URL` and `YOUTRACK_TOKEN`
3. set via command line parameters, `--url` and `--token`

## Usage

### As git pre-push hook

See the [`pre-push`](pre-push) example, which can be copied directly into
`.git/hooks/pre-push`. That example checks the commit title for the YouTrack
ticket ID as the first item, for example `EXAMPLE-1234 some commit title`.

### Running standalone

```bash
❯ youtrack-cli --url "https://your-youtrack-server/api" --token $YOUTRACK_TOKEN get --confirm-prompt --ticket example-1234
                                                  Issue data for example-1234
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           Key ┃ Value                                                                                                     ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│    idReadable │ EXAMPLE-9377                                                                                              │
├───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│       summary │ Test ticket title                                                                                         │
├───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ assignee_name │ Jane Doe                                                                                                  │
├───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ reporter_name │ jane                                                                                                      │
├───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│   description │ Long description, truncated to max of 1024 characters                                                     │
├───────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│           url │ https://your-youtrack-server/issue/EXAMPLE-1234                                                           │
└───────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┘
Type the ticket id to confirm: example-1234
```
