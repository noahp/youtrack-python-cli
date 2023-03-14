import dataclasses
import json
import logging
import re
from http import HTTPStatus

import click
from rich import print_json
from rich.console import Console
from rich.table import Table
from you_track_rest_api_client import AuthenticatedClient
from you_track_rest_api_client.api.default import get_issues_id

# from you_track_rest_api_client.models import MyDataModel
from you_track_rest_api_client.types import Response

from ._version import version


class YouTrack:
    def __init__(self, url: str, token: str):
        self.client = AuthenticatedClient(base_url=url, token=token)


class Issue(dict):
    def __init__(self, ticket, issue: dict):
        self.ticket = ticket
        ITEMS_TO_KEEP = [
            "idReadable",
            "summary",
            "assignee_name",
            "reporter_name",
            "description",
            "url",
        ]
        filtered_dict = {k: v for k, v in issue.items() if k in ITEMS_TO_KEEP}
        filtered_dict = dict(
            sorted(filtered_dict.items(), key=lambda pair: ITEMS_TO_KEEP.index(pair[0]))
        )
        # truncate description to 1024 chars
        if len(filtered_dict["description"]) > 1024:
            filtered_dict["description"] = filtered_dict["description"][:1024] + "..."
        super().__init__(filtered_dict)

    def print_table(self):
        table = Table(title=f"Issue data for {self.ticket}")

        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        for k, v in self.items():
            table.add_row(k, v)
            table.add_section()

        console = Console()
        console.print(table)


@dataclasses.dataclass
class CliCtx:
    url: str
    youtrack: YouTrack
    verbose: bool


@click.group()
@click.option("--verbose", help="Log verbosely", is_flag=True)
@click.option(
    "--url",
    envvar="YOUTRACK_URL",
    help="Explicit youtrack url, defaults to environment variable YOUTRACK_URL",
)
@click.option(
    "--token",
    envvar="YOUTRACK_TOKEN",
    help="Explicit youtrack token, defaults to environment variable YOUTRACK_TOKEN",
)
@click.version_option(version=version)
@click.pass_context
def cli(ctx, verbose, url, token):
    """
    Top-level command group, for global args.
    """
    if verbose:
        click.echo(f"version: {version}")

        logging.basicConfig(level=logging.DEBUG)

    if not url:
        raise click.BadParameter("url is required")

    ctx.obj = CliCtx(url, YouTrack(url, token), verbose)


@cli.command()
@click.option("--ticket", help="Ticket id, of the form PROJECT-1234", required=True)
@click.option(
    "--confirm-prompt",
    help="Prompt the user to type in the issue, can be used as part of a git pre-push script for confirming issue",
    is_flag=True,
)
@click.pass_context
def get(ctx: CliCtx, ticket, confirm_prompt):
    if not re.match(r"^[A-Za-z]+-\d+$", ticket):
        raise click.BadParameter("ticket must be of the form PROJECT-1234")

    # issue api request
    ticket_response: Response = get_issues_id.sync_detailed(
        id=ticket, client=ctx.obj.youtrack.client
    )

    # check for response error
    if ticket_response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"unexpected status code: {ticket_response.status_code}")

    # parse json
    response_text = ticket_response.content.decode("utf-8")
    if ctx.obj.verbose:
        print_json(response_text)
    issue_json = json.loads(response_text)

    # inject some additional fields that the Issue() class uses
    # 1. ticket URL
    issue_json[
        "url"
    ] = f"{ctx.obj.url.removesuffix('/api')}/issue/{issue_json['idReadable']}"
    # 2. reporter name
    issue_json["reporter_name"] = issue_json["reporter"]["login"]
    # 3. assignee name, if present
    for field in issue_json["customFields"]:
        if field["name"] == "Assignee":
            issue_json["assignee_name"] = field["value"]["name"]

    issue = Issue(ticket, issue_json)
    issue.print_table()

    if confirm_prompt:
        while click.prompt("Type the ticket id to confirm").lower() != ticket.lower():
            print("Ticket id did not match, try again!")


if __name__ == "__main__":
    cli()
