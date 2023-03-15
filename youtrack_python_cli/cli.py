"""
CLI interface.
"""

import dataclasses
import http
import json
import logging
import os
import re
import subprocess
from typing import Tuple

import click
from rich import print_json
from rich.console import Console
from rich.table import Table
from you_track_rest_api_client import AuthenticatedClient
from you_track_rest_api_client.api.default import get_issues_id

# from you_track_rest_api_client.models import MyDataModel
from you_track_rest_api_client.types import Response

from ._version import VERSION


class Issue(dict):
    """
    Issue data class, used to print a table of issue data.
    """

    def __init__(self, ticket, issue: dict):
        self.ticket = ticket
        items_to_keep = [
            "idReadable",
            "summary",
            "assignee_name",
            "reporter_name",
            "description",
            "url",
        ]
        filtered_dict = {k: v for k, v in issue.items() if k in items_to_keep}
        filtered_dict = dict(
            sorted(
                filtered_dict.items(),
                key=lambda pair: items_to_keep.index(pair[0]),
            )
        )
        # truncate description to 1024 chars
        if (
            filtered_dict.get("description")
            and len(filtered_dict["description"]) > 1024
        ):
            filtered_dict["description"] = (
                filtered_dict["description"][:1024] + "..."
            )
        super().__init__(filtered_dict)

    def print_table(self):
        """Print a pretty table of the issue data."""
        table = Table(title=f"Issue data for {self.ticket}")

        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        for key, value in self.items():
            table.add_row(key, value)
            table.add_section()

        console = Console()
        console.print(table)


@dataclasses.dataclass
class CliCtx:
    """
    Context object for the CLI, forwarded from the top-level command group
    """

    url: str
    youtrack: AuthenticatedClient
    verbose: bool


def get_config(key: str) -> str:
    """
    Get a config value from git config, or environment variables.
    """
    config = None

    # try git config
    try:
        config = (
            subprocess.check_output(["git", "config", f"youtrack.{key}"])
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        pass

    # try environment variable- overrides git config
    env_var = f"YOUTRACK_{key.upper()}"
    if env_var in os.environ:
        config = os.environ[env_var]

    if not config:
        raise click.UsageError(
            f"missing config value for '{key}', please set via environment"
            f" variable '{env_var}', or via 'git config youtrack.{key}'"
        )

    return config


def load_config(url: str, token: str) -> Tuple[str, str]:
    """
    Load configs.
    """
    return url or get_config("url"), token or get_config("token")


@click.group()
@click.option("--verbose", help="Log verbosely", is_flag=True)
@click.option(
    "--url",
    help=(
        "Explicit youtrack url. Can be configured here, or via environment"
        " variable YOUTRACK_URL, or via 'git config youtrack.url'."
    ),
)
@click.option(
    "--token",
    help=(
        "Explicit youtrack token. Can be configured here, or via environment"
        " variable YOUTRACK_TOKEN, or via 'git config youtrack.token'."
    ),
)
@click.version_option(version=VERSION)
@click.pass_context
def cli(ctx, verbose, url, token):
    """
    Top-level command group, for global args.
    """
    if verbose:
        click.echo(f"version: {VERSION}")

        logging.basicConfig(level=logging.DEBUG)

    url, token = load_config(url, token)

    ctx.obj = CliCtx(
        url, AuthenticatedClient(base_url=url, token=token), verbose
    )


@cli.command()
@click.option(
    "--ticket", help="Ticket id, of the form PROJECT-1234", required=True
)
@click.option(
    "--confirm-prompt",
    help=(
        "Prompt the user to type in the issue, can be used as part of a git"
        " pre-push script for confirming issue"
    ),
    is_flag=True,
)
@click.pass_obj
def get(ctx: CliCtx, ticket, confirm_prompt):
    """
    Fetch a ticket by id. Optionally prompt the user to confirm the ticket id,
    useful for git pre-push hooks.
    """
    if not re.match(r"^[A-Za-z]+-\d+$", ticket):
        raise click.BadParameter("ticket must be of the form PROJECT-1234")

    # issue api request
    ticket_response: Response = get_issues_id.sync_detailed(
        id=ticket, client=ctx.youtrack
    )

    # check for response error
    if ticket_response.status_code != http.HTTPStatus.OK:
        raise click.UsageError(
            "unexpected HTTP status code, check your youtrack token:"
            f" {ticket_response.status_code}"
        )

    # parse json
    response_text = ticket_response.content.decode("utf-8")
    if ctx.verbose:
        print_json(response_text)
    issue_json = json.loads(response_text)

    # inject some additional fields that the Issue() class uses
    # 1. ticket URL
    issue_json[
        "url"
    ] = f"{ctx.url.partition('/api')[0]}/issue/{issue_json['idReadable']}"
    # 2. reporter name
    issue_json["reporter_name"] = issue_json["reporter"]["login"]
    # 3. assignee name, if present
    for field in issue_json["customFields"]:
        if field["name"] == "Assignee":
            issue_json["assignee_name"] = field["value"]["name"]

    issue = Issue(ticket, issue_json)
    issue.print_table()

    if confirm_prompt:
        while (
            click.prompt("Type the ticket id to confirm").lower()
            != ticket.lower()
        ):
            print("Ticket id did not match, try again!")


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
