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
    def __init__(self, issue: dict):
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
@click.pass_context
def get(ctx: CliCtx, ticket):
    if not re.match(r"^[A-Za-z]+-\d+$", ticket):
        raise click.BadParameter("ticket must be of the form PROJECT-1234")

    ticket_response: Response = get_issues_id.sync_detailed(
        id=ticket, client=ctx.obj.youtrack.client
    )

    if ticket_response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"unexpected status code: {ticket_response.status_code}")

    issue_json = json.loads(ticket_response.content.decode("utf-8"))
    issue_json[
        "url"
    ] = f"{ctx.obj.url.removesuffix('/api')}/issue/{issue_json['idReadable']}"
    issue_json["reporter_name"] = issue_json["reporter"]["login"]

    for field in issue_json["customFields"]:
        if field["name"] == "Assignee":
            issue_json["assignee_name"] = field["value"]["name"]

    issue = Issue(issue_json)

    table = Table(title=f"Issue data for {ticket}")

    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    for k, v in issue.items():
        table.add_row(k, v)
        table.add_section()

    if ctx.obj.verbose:
        print_json(ticket_response.content.decode("utf-8"))

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
