import subprocess

import pytest
from click.testing import CliRunner

from youtrack_python_cli.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--version"],
    )
    assert result.exit_code == 0
    assert result.output.startswith("cli, version ")


def test_help(snapshot):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--help"],
    )
    assert result.exit_code == 0
    assert result.output == snapshot


BASIC_RESPONSE_JSON = {
    "idReadable": "TEST-1234",
    "reporter": {"login": "testuser"},
    "customFields": [
        {
            "name": "Assignee",
            "value": {
                "name": "testuser name",
            },
        },
        {
            "name": "NotAssignee",
            "value": {
                "name": "testuser not name",
            },
        },
    ],
    "description": "Test Description",
}
BASIC_RESPONSE_JSON_NO_ASSIGNEE = {
    "idReadable": "TEST-1234",
    "reporter": {"login": "testuser"},
    "customFields": [
        {
            "name": "Assignee",
            "value": None,
        },
    ],
    "description": "Test Description",
}
LONG_DESCRIPTION_JSON = BASIC_RESPONSE_JSON.copy()
LONG_DESCRIPTION_JSON["description"] = "a" * 1025
BASIC_CLI_ARGS = [
    "--url",
    "http://youtrack-test/youtrack/api",
    "--token",
    "abc",
]
BASIC_GET_ARGS = BASIC_CLI_ARGS + [
    "get",
    "--ticket",
    "TEST-1234",
]
BASIC_REQUEST_MOCK_URL = r"http://youtrack-test/youtrack/api/issues/TEST-1234?fields=%24type%2Ccreated%2CcustomFields%28%24type%2Cid%2Cname%2Cvalue%28%24type%2Cid%2Cname%29%29%2Cdescription%2Cid%2CidReadable%2Clinks%28%24type%2Cdirection%2Cid%2ClinkType%28%24type%2Cid%2ClocalizedName%2Cname%29%29%2CnumberInProject%2Cproject%28%24type%2Cid%2Cname%2CshortName%29%2Creporter%28%24type%2Cid%2Clogin%2CringId%29%2Cresolved%2Csummary%2Cupdated%2Cupdater%28%24type%2Cid%2Clogin%2CringId%29%2Cvisibility%28%24type%2Cid%2CpermittedGroups%28%24type%2Cid%2Cname%2CringId%29%2CpermittedUsers%28%24type%2Cid%2Clogin%2CringId%29%29"  # noqa: E501


@pytest.mark.parametrize(
    "json_response,cli_args,retval,http_status_code",
    [
        # use explicit http status codes, snapshots vary depending on python
        # version unfortunately
        (BASIC_RESPONSE_JSON, BASIC_GET_ARGS, 0, 200),
        (
            BASIC_RESPONSE_JSON,
            ["--verbose"] + BASIC_GET_ARGS,
            0,
            200,
        ),
        (LONG_DESCRIPTION_JSON, BASIC_GET_ARGS, 0, 200),
        (
            None,
            BASIC_CLI_ARGS + ["get", "--ticket", "blahblah"],
            2,
            200,
        ),
        (BASIC_RESPONSE_JSON, BASIC_GET_ARGS, 2, 401),
        # test that when there's no assignee, we don't crash
        (BASIC_RESPONSE_JSON_NO_ASSIGNEE, BASIC_GET_ARGS, 0, 200),
    ],
)
def test_basic_operation(
    json_response, cli_args, retval, http_status_code, snapshot, respx_mock
):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=http_status_code,
        json=json_response,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        cli_args,
        # enable CI explicity, though it's normally set in tox. this is in case
        # the user is running pytest manually.
        env={"CI": "1"},
    )
    print(result.output)
    assert result.exit_code == retval
    assert result.output == snapshot


def test_git_config(snapshot, respx_mock):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=200,
        json=BASIC_RESPONSE_JSON,
    )

    runner = CliRunner()

    with runner.isolated_filesystem():
        subprocess.check_call(["git", "init"])
        subprocess.check_call(
            [
                "git",
                "config",
                "youtrack.url",
                "http://youtrack-test/youtrack/api",
            ]
        )
        subprocess.check_call(["git", "config", "youtrack.token", "abc"])
        result = runner.invoke(
            cli,
            [
                "get",
                "--ticket",
                "TEST-1234",
            ],
        )
        assert result.exit_code == 0
        assert result.output == snapshot


def test_env_config(snapshot, respx_mock):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=200,
        json=BASIC_RESPONSE_JSON,
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "get",
            "--ticket",
            "TEST-1234",
        ],
        env={
            "YOUTRACK_URL": "http://youtrack-test/youtrack/api",
            "YOUTRACK_TOKEN": "abc",
        },
    )
    assert result.exit_code == 0
    assert result.output == snapshot


def test_no_config_error(snapshot, respx_mock):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "get",
            "--ticket",
            "TEST-1234",
        ],
    )
    assert result.exit_code == 2
    assert result.output == snapshot


def test_confirm_prompt(snapshot, respx_mock):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=200,
        json=BASIC_RESPONSE_JSON,
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        BASIC_GET_ARGS + ["--confirm-prompt"],
        input="n\nTEST-1234",
    )
    assert result.exit_code == 0
    assert result.output == snapshot


def test_no_ci_run(respx_mock):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=200,
        json=BASIC_RESPONSE_JSON,
    )

    runner = CliRunner()

    result = runner.invoke(
        cli,
        BASIC_GET_ARGS,
        env={"CI": ""},
    )
    assert result.exit_code == 0
    # don't care about the output.
