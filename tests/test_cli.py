import http

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


def test_basic_operation(snapshot, respx_mock):
    respx_mock.get(
        r"http://youtrack-test/youtrack/api/issues/TEST-1234?fields=%24type%2Ccreated%2CcustomFields%28%24type%2Cid%2Cname%2Cvalue%28%24type%2Cid%2Cname%29%29%2Cdescription%2Cid%2CidReadable%2Clinks%28%24type%2Cdirection%2Cid%2ClinkType%28%24type%2Cid%2ClocalizedName%2Cname%29%29%2CnumberInProject%2Cproject%28%24type%2Cid%2Cname%2CshortName%29%2Creporter%28%24type%2Cid%2Clogin%2CringId%29%2Cresolved%2Csummary%2Cupdated%2Cupdater%28%24type%2Cid%2Clogin%2CringId%29%2Cvisibility%28%24type%2Cid%2CpermittedGroups%28%24type%2Cid%2Cname%2CringId%29%2CpermittedUsers%28%24type%2Cid%2Clogin%2CringId%29%29"  # noqa: E501
    ).respond(
        status_code=http.HTTPStatus.OK,
        json={
            "idReadable": "TEST-1234",
            "reporter": {"login": "testuser"},
            "customFields": [
                {
                    "id": "customfield_10000",
                    "name": "Test Field",
                    "value": {
                        "id": "customfield_10000_value_1",
                        "name": "Test Value",
                    },
                }
            ],
            "description": "Test Description",
        },
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--url",
            "http://youtrack-test/youtrack/api",
            "--token",
            "abc",
            "get",
            "--ticket",
            "TEST-1234",
        ],
    )
    print(result.output)
    assert result.exit_code == 0
    assert result.output == snapshot
