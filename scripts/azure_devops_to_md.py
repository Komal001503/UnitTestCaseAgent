#!/usr/bin/env python3
"""Fetch Azure DevOps User Stories and convert them to Markdown.

The script queries Azure DevOps Boards using WIQL (`api-version=7.1`) and then
retrieves work item details in batches. Azure DevOps WIQL responses are capped
at 20,000 work item IDs per query.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import quote

import html2text
import requests
from requests import Response

DEFAULT_WORK_ITEM_TYPE = "User Story"
DEFAULT_OUTPUT_PATH = Path("azure_devops_user_stories.md")
API_VERSION = "7.1"


@dataclass(frozen=True)
class Config:
    org: str
    project: str
    team: str | None
    pat: str
    work_item_type: str
    states: list[str] | None
    area_path: str | None
    output: Path
    dry_run: bool
    verbose: bool


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull Azure DevOps work items and write markdown user stories."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output Markdown file path")
    parser.add_argument("--org", help="Azure DevOps organization name")
    parser.add_argument("--project", help="Azure DevOps project name")
    parser.add_argument("--team", help="Azure DevOps team name (optional)")
    parser.add_argument("--work-item-type", help=f"Work item type (default: {DEFAULT_WORK_ITEM_TYPE})")
    parser.add_argument("--states", help="Comma-separated list of states to include")
    parser.add_argument("--area-path", help="Optional Area Path filter")
    parser.add_argument("--dry-run", action="store_true", help="Print WIQL and fetched count; do not write file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args(argv)


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_states(value: str | None) -> list[str] | None:
    if not value:
        return None
    states = [state.strip() for state in value.split(",") if state.strip()]
    return states or None


def _escape_wiql_literal(value: str) -> str:
    return value.replace("'", "''")


def resolve_config(args: argparse.Namespace) -> Config:
    org = _clean_optional(args.org) or _clean_optional(_env("AZURE_DEVOPS_ORG"))
    project = _clean_optional(args.project) or _clean_optional(_env("AZURE_DEVOPS_PROJECT"))
    team = _clean_optional(args.team) if args.team is not None else _clean_optional(_env("AZURE_DEVOPS_TEAM"))
    pat = _clean_optional(_env("AZURE_DEVOPS_PAT"))
    work_item_type = _clean_optional(args.work_item_type) or _clean_optional(_env("AZURE_DEVOPS_WORK_ITEM_TYPE")) or DEFAULT_WORK_ITEM_TYPE
    states = _parse_states(args.states) if args.states is not None else _parse_states(_env("AZURE_DEVOPS_STATES"))
    area_path = _clean_optional(args.area_path) if args.area_path is not None else _clean_optional(_env("AZURE_DEVOPS_AREA_PATH"))

    missing = [name for name, value in [("AZURE_DEVOPS_ORG", org), ("AZURE_DEVOPS_PROJECT", project), ("AZURE_DEVOPS_PAT", pat)] if not value]
    if missing:
        if "AZURE_DEVOPS_PAT" in missing:
            raise ValueError("Missing AZURE_DEVOPS_PAT. Set it in environment (Work Items: Read scope).")
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    return Config(
        org=org,
        project=project,
        team=team,
        pat=pat,
        work_item_type=work_item_type,
        states=states,
        area_path=area_path,
        output=Path(args.output),
        dry_run=bool(args.dry_run),
        verbose=bool(args.verbose),
    )


def _env(name: str) -> str | None:
    from os import getenv

    return getenv(name)


def build_wiql_query(config: Config) -> str:
    escaped_type = _escape_wiql_literal(config.work_item_type)
    where = [f"[System.WorkItemType] = '{escaped_type}'"]

    if config.states:
        escaped_states = ", ".join(f"'{_escape_wiql_literal(state)}'" for state in config.states)
        where.append(f"[System.State] IN ({escaped_states})")
    else:
        where.append("[System.State] <> 'Removed'")

    if config.area_path:
        escaped_area = _escape_wiql_literal(config.area_path)
        where.append(f"[System.AreaPath] = '{escaped_area}'")

    return (
        "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], "
        "[Microsoft.VSTS.Common.Priority], [System.Description], "
        "[Microsoft.VSTS.Common.AcceptanceCriteria], [System.Tags], [System.AreaPath], [System.IterationPath] "
        f"FROM WorkItems WHERE {' AND '.join(where)} ORDER BY [System.Id] ASC"
    )


def _wiql_url(config: Config) -> str:
    project = quote(config.project, safe="")
    base = f"https://dev.azure.com/{config.org}/{project}"
    if config.team:
        team = quote(config.team, safe="")
        return f"{base}/{team}/_apis/wit/wiql?api-version={API_VERSION}"
    return f"{base}/_apis/wit/wiql?api-version={API_VERSION}"


def _workitems_batch_url(config: Config) -> str:
    project = quote(config.project, safe="")
    return f"https://dev.azure.com/{config.org}/{project}/_apis/wit/workitemsbatch?api-version={API_VERSION}"


def _raise_for_status_with_context(response: Response) -> None:
    if response.status_code == 401:
        raise RuntimeError("Azure DevOps API returned 401 Unauthorized. Check PAT scopes/expiry.")
    if response.status_code == 404:
        raise RuntimeError("Azure DevOps API returned 404 Not Found. Check org/project/team name.")
    response.raise_for_status()


def _chunked(values: list[int], size: int) -> Iterable[list[int]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def fetch_work_items(config: Config, wiql_query: str) -> list[dict[str, Any]]:
    session = requests.Session()
    session.auth = ("", config.pat)
    session.headers.update({"Content-Type": "application/json"})

    logging.debug("Submitting WIQL query to %s", _wiql_url(config))
    wiql_response = session.post(_wiql_url(config), json={"query": wiql_query}, timeout=30)
    _raise_for_status_with_context(wiql_response)
    wiql_data = wiql_response.json()
    ids = [item["id"] for item in wiql_data.get("workItems", []) if "id" in item]
    ids.sort()

    if not ids:
        return []

    items: list[dict[str, Any]] = []
    for id_chunk in _chunked(ids, 200):
        payload = {
            "ids": id_chunk,
            "fields": [
                "System.Id",
                "System.Title",
                "System.State",
                "System.AssignedTo",
                "Microsoft.VSTS.Common.Priority",
                "System.Description",
                "Microsoft.VSTS.Common.AcceptanceCriteria",
                "System.Tags",
                "System.AreaPath",
                "System.IterationPath",
            ],
        }
        logging.debug("Fetching work item batch with %d IDs", len(id_chunk))
        batch_response = session.post(_workitems_batch_url(config), json=payload, timeout=30)
        _raise_for_status_with_context(batch_response)
        batch_data = batch_response.json()
        items.extend(batch_data.get("value", []))

    items.sort(key=lambda item: int(item.get("fields", {}).get("System.Id", 0)))
    return items


def _to_text(value: Any, converter: html2text.HTML2Text) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return converter.handle(text).strip()


def _assigned_to(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("displayName") or value.get("uniqueName") or "").strip()
    return str(value or "").strip()


def _safe_cell(value: Any) -> str:
    text = str(value or "").strip()
    return text.replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def render_markdown(config: Config, items: list[dict[str, Any]]) -> str:
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.body_width = 0

    lines: list[str] = [
        "# Azure DevOps User Stories",
        "",
        f"Organization: `{config.org}`",
        f"Project: `{config.project}`",
        f"Team: `{config.team or 'N/A'}`",
        "",
        f"Total stories: {len(items)}",
        "",
        "| Story ID | Title | State | Priority | Assigned To |",
        "|---|---|---|---|---|",
    ]

    for item in items:
        fields = item.get("fields", {})
        story_id = fields.get("System.Id", "")
        title = fields.get("System.Title", "")
        state = fields.get("System.State", "")
        priority = fields.get("Microsoft.VSTS.Common.Priority", "")
        assigned_to = _assigned_to(fields.get("System.AssignedTo"))
        lines.append(
            f"| US-{_safe_cell(story_id)} | {_safe_cell(title)} | {_safe_cell(state)} | {_safe_cell(priority)} | {_safe_cell(assigned_to)} |"
        )

    lines.extend(["", "---", ""])

    for item in items:
        fields = item.get("fields", {})
        story_id = fields.get("System.Id", "")
        title = str(fields.get("System.Title", "")).strip()
        state = fields.get("System.State", "")
        priority = fields.get("Microsoft.VSTS.Common.Priority", "")
        assigned_to = _assigned_to(fields.get("System.AssignedTo"))
        area_path = fields.get("System.AreaPath", "")
        iteration_path = fields.get("System.IterationPath", "")
        tags = fields.get("System.Tags", "")
        ado_url = f"https://dev.azure.com/{config.org}/{quote(config.project, safe='')}/_workitems/edit/{story_id}"
        description = _to_text(fields.get("System.Description"), converter) or "_No description provided._"
        acceptance = _to_text(fields.get("Microsoft.VSTS.Common.AcceptanceCriteria"), converter) or "_No acceptance criteria provided._"

        lines.extend(
            [
                f"## US-{story_id} — {title}",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| ID | US-{_safe_cell(story_id)} |",
                f"| State | {_safe_cell(state)} |",
                f"| Priority | {_safe_cell(priority)} |",
                f"| Assigned To | {_safe_cell(assigned_to)} |",
                f"| Area Path | {_safe_cell(area_path)} |",
                f"| Iteration Path | {_safe_cell(iteration_path)} |",
                f"| Tags | {_safe_cell(tags)} |",
                f"| ADO URL | {ado_url} |",
                "",
                "### Description",
                "",
                description,
                "",
                "### Acceptance Criteria",
                "",
                acceptance,
                "",
                "---",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = resolve_config(args)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    logging.basicConfig(
        level=logging.DEBUG if config.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    wiql_query = build_wiql_query(config)
    if config.verbose or config.dry_run:
        print("Resolved WIQL:")
        print(wiql_query)

    try:
        items = fetch_work_items(config, wiql_query)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except requests.HTTPError as error:
        print(f"Error: Azure DevOps API request failed: {error}", file=sys.stderr)
        return 1
    except requests.RequestException as error:
        print(f"Error: Network error while calling Azure DevOps API: {error}", file=sys.stderr)
        return 1

    print(f"Fetched {len(items)} work item(s).")
    if config.dry_run:
        return 0

    markdown = render_markdown(config, items)
    config.output.write_text(markdown, encoding="utf-8")
    print(f"Markdown written to {config.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
