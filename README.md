[![GitHub](https://img.shields.io/badge/GitHub-noahp/youtrack--python--cli-8da0cb?style=for-the-badge&logo=github)](https://github.com/noahp/youtrack-python-cli)
[![PyPI
version](https://img.shields.io/pypi/v/youtrack-python-cli.svg?style=for-the-badge&logo=PyPi&logoColor=white)](https://pypi.org/project/youtrack-python-cli/)
[![PyPI
pyversions](https://img.shields.io/pypi/pyversions/youtrack-python-cli.svg?style=for-the-badge&logo=python&logoColor=white&color=ff69b4)](https://pypi.python.org/pypi/youtrack-python-cli/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/noahp/youtrack-python-cli/main.yml?branch=main&logo=github-actions&logoColor=white&style=for-the-badge)](https://github.com/noahp/youtrack-python-cli/actions)
[![codecov](https://img.shields.io/codecov/c/github/noahp/youtrack-python-cli.svg?style=for-the-badge&logo=codecov)](https://codecov.io/gh/noahp/youtrack-python-cli)

# YouTrack Python CLI

Usage:

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

See also [pre-push](pre-push) for a `.git/hooks/pre-push` example script that
will prompt when you try to push new commits with a leading `^[A-Za-z]+-[0-9]+`
string.
