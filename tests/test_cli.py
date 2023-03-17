import http
import subprocess

import pytest
from click.testing import CliRunner

from youtrack_python_cli.cli import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.startswith("cli, version ")


def test_help(snapshot):
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
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
        (BASIC_RESPONSE_JSON, BASIC_GET_ARGS, 0, http.HTTPStatus.OK),
        (
            BASIC_RESPONSE_JSON,
            ["--verbose"] + BASIC_GET_ARGS,
            0,
            http.HTTPStatus.OK,
        ),
        (LONG_DESCRIPTION_JSON, BASIC_GET_ARGS, 0, http.HTTPStatus.OK),
        (
            None,
            BASIC_CLI_ARGS + ["get", "--ticket", "blahblah"],
            2,
            http.HTTPStatus.OK,
        ),
        (BASIC_RESPONSE_JSON, BASIC_GET_ARGS, 2, http.HTTPStatus.UNAUTHORIZED),
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
    )
    print(result.output)
    assert result.exit_code == retval
    assert result.output == snapshot


def test_git_config(snapshot, respx_mock):
    respx_mock.get(BASIC_REQUEST_MOCK_URL).respond(
        status_code=http.HTTPStatus.OK,
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
        status_code=http.HTTPStatus.OK,
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
        status_code=http.HTTPStatus.OK,
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
