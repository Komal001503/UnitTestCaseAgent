#!/usr/bin/env python3
"""Fetch Azure DevOps work items and render user stories as Markdown."""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import quote

import html2text
import requests


API_VERSION = "7.1"
DEFAULT_WORK_ITEM_TYPE = "User Story"
DEFAULT_OUTPUT_PATH = Path("azure_devops_user_stories.md")
BATCH_SIZE = 200
WIQL_LIMIT = 20000
FIELDS = [
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
]


@dataclass(frozen=True)
class Config:
    org: str
    project: str
    team: str | None
    pat: str
    work_item_type: str
    states: list[str] | None
    area_path: str | None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Azure DevOps user stories and convert them to Markdown."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Output Markdown file path.")
    parser.add_argument("--org", help="Azure DevOps organization name.")
    parser.add_argument("--project", help="Azure DevOps project name.")
    parser.add_argument("--team", help="Azure DevOps team name (optional).")
    parser.add_argument("--work-item-type", help=f"Work item type (default: {DEFAULT_WORK_ITEM_TYPE}).")
    parser.add_argument(
        "--states",
        help="Comma-separated states to include (default: all except Removed).",
    )
    parser.add_argument("--area-path", help="Optional Area Path filter.")
    parser.add_argument("--dry-run", action="store_true", help="Print WIQL and counts without writing output.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args(argv)


def _split_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    parsed = [part.strip() for part in value.split(",") if part.strip()]
    return parsed or None


def resolve_config(args: argparse.Namespace) -> Config:
    org = args.org or os.getenv("AZURE_DEVOPS_ORG", "")
    project = args.project or os.getenv("AZURE_DEVOPS_PROJECT", "")
    team = args.team or os.getenv("AZURE_DEVOPS_TEAM") or None
    pat = os.getenv("AZURE_DEVOPS_PAT", "")
    work_item_type = args.work_item_type or os.getenv("AZURE_DEVOPS_WORK_ITEM_TYPE", DEFAULT_WORK_ITEM_TYPE)
    states = _split_csv(args.states) if args.states is not None else _split_csv(os.getenv("AZURE_DEVOPS_STATES"))
    area_path = args.area_path if args.area_path is not None else os.getenv("AZURE_DEVOPS_AREA_PATH")

    if not pat.strip():
        raise ValueError("AZURE_DEVOPS_PAT is required. Set it in your environment before running this script.")
    if not org.strip():
        raise ValueError("AZURE_DEVOPS_ORG is required (or pass --org).")
    if not project.strip():
        raise ValueError("AZURE_DEVOPS_PROJECT is required (or pass --project).")

    return Config(
        org=org.strip(),
        project=project.strip(),
        team=team.strip() if team else None,
        pat=pat.strip(),
        work_item_type=work_item_type.strip() or DEFAULT_WORK_ITEM_TYPE,
        states=states,
        area_path=area_path.strip() if area_path else None,
    )


def _escape_wiql_literal(value: str) -> str:
    return value.replace("'", "''")


def build_wiql(config: Config) -> str:
    lines = [
        "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo],",
        "       [Microsoft.VSTS.Common.Priority], [System.Description],",
        "       [Microsoft.VSTS.Common.AcceptanceCriteria], [System.Tags], [System.AreaPath], [System.IterationPath]",
        "FROM WorkItems",
        f"WHERE [System.WorkItemType] = '{_escape_wiql_literal(config.work_item_type)}'",
        "  AND [System.TeamProject] = @project",
    ]
    if config.states:
        quoted = ", ".join(f"'{_escape_wiql_literal(state)}'" for state in config.states)
        lines.append(f"  AND [System.State] IN ({quoted})")
    else:
        lines.append("  AND [System.State] <> 'Removed'")
    if config.area_path:
        lines.append(f"  AND [System.AreaPath] UNDER '{_escape_wiql_literal(config.area_path)}'")
    lines.append("ORDER BY [System.Id]")
    return "\n".join(lines)


def _wiql_url(config: Config) -> str:
    base = _ado_project_base_url(config)
    if config.team:
        return f"{base}/{quote(config.team, safe='')}/_apis/wit/wiql?api-version={API_VERSION}"
    return f"{base}/_apis/wit/wiql?api-version={API_VERSION}"


def _workitems_batch_url(config: Config) -> str:
    return f"{_ado_project_base_url(config)}/_apis/wit/workitemsbatch?api-version={API_VERSION}"


def _ado_project_base_url(config: Config) -> str:
    return f"https://dev.azure.com/{quote(config.org, safe='')}/{quote(config.project, safe='')}"


def _request_json(session: requests.Session, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    response = session.request(method, url, timeout=30, **kwargs)
    if response.status_code >= 400:
        message = f"Azure DevOps API error {response.status_code} for {url}"
        if response.status_code == 401:
            message += ". Check PAT scopes/expiry."
        elif response.status_code == 404:
            message += ". Check org/project/team name."
        try:
            payload = response.json()
            detail = payload.get("message") or payload.get("error", {}).get("message")
            if detail:
                message += f" Details: {detail}"
        except Exception:
            pass
        raise RuntimeError(message)
    return response.json()


def fetch_work_item_ids(session: requests.Session, config: Config, wiql: str) -> list[int]:
    payload = _request_json(session, "POST", _wiql_url(config), json={"query": wiql})
    work_items = payload.get("workItems", [])
    ids = [int(item["id"]) for item in work_items if "id" in item]
    if len(ids) >= WIQL_LIMIT:
        logging.warning(
            (
                "WIQL returned %s IDs. Azure DevOps WIQL is limited to %s IDs per query; "
                "some work items may be omitted. Consider narrowing results with --states or --area-path."
            ),
            len(ids),
            WIQL_LIMIT,
        )
    return sorted(set(ids))


def _chunked(items: list[int], size: int) -> list[list[int]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def fetch_work_items(session: requests.Session, config: Config, ids: list[int]) -> list[dict[str, Any]]:
    if not ids:
        return []
    all_items: list[dict[str, Any]] = []
    url = _workitems_batch_url(config)
    for chunk in _chunked(ids, BATCH_SIZE):
        body = {"ids": chunk, "fields": FIELDS}
        payload = _request_json(session, "POST", url, json=body)
        all_items.extend(payload.get("value", []))
    return sorted(all_items, key=lambda item: item.get("fields", {}).get("System.Id", 0))


def _markdown_renderer() -> html2text.HTML2Text:
    renderer = html2text.HTML2Text()
    renderer.body_width = 0
    renderer.ignore_links = True
    renderer.ignore_images = True
    renderer.ignore_emphasis = False
    return renderer


def _html_to_text(value: Any, renderer: html2text.HTML2Text) -> str:
    if value is None:
        return ""
    text = renderer.handle(str(value))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _stringify_assigned_to(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("displayName") or value.get("uniqueName") or "")
    return str(value or "")


def _clean_cell(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "-"
    return text.replace("\n", "<br>").replace("|", "\\|")


def to_markdown(config: Config, work_items: list[dict[str, Any]]) -> str:
    renderer = _markdown_renderer()
    lines: list[str] = [
        "# User Stories",
        "",
        f"Total stories: {len(work_items)}",
        "",
        "| Story ID | Title | State | Priority | Assigned To |",
        "|----------|-------|-------|----------|-------------|",
    ]

    for item in work_items:
        fields = item.get("fields", {})
        story_id = fields.get("System.Id", "")
        title = fields.get("System.Title", "")
        state = fields.get("System.State", "")
        priority = fields.get("Microsoft.VSTS.Common.Priority", "")
        assigned_to = _stringify_assigned_to(fields.get("System.AssignedTo"))
        lines.append(
            f"| US-{_clean_cell(story_id)} | {_clean_cell(title)} | {_clean_cell(state)} | {_clean_cell(priority)} | {_clean_cell(assigned_to)} |"
        )

    if work_items:
        lines.extend(["", "---", ""])

    for item in work_items:
        fields = item.get("fields", {})
        story_id = fields.get("System.Id", "")
        title = str(fields.get("System.Title", "")).strip() or "Untitled"
        state = fields.get("System.State", "")
        priority = fields.get("Microsoft.VSTS.Common.Priority", "")
        assigned_to = _stringify_assigned_to(fields.get("System.AssignedTo"))
        area_path = fields.get("System.AreaPath", "")
        iteration_path = fields.get("System.IterationPath", "")
        tags = fields.get("System.Tags", "")
        description = _html_to_text(fields.get("System.Description"), renderer)
        acceptance = _html_to_text(fields.get("Microsoft.VSTS.Common.AcceptanceCriteria"), renderer)
        work_item_url = f"{_ado_project_base_url(config)}/_workitems/edit/{story_id}"

        lines.extend(
            [
                f"## US-{story_id} — {title}",
                "",
                "| Field | Value |",
                "|---|---|",
                f"| ID | US-{_clean_cell(story_id)} |",
                f"| State | {_clean_cell(state)} |",
                f"| Priority | {_clean_cell(priority)} |",
                f"| Assigned To | {_clean_cell(assigned_to)} |",
                f"| Area Path | {_clean_cell(area_path)} |",
                f"| Iteration Path | {_clean_cell(iteration_path)} |",
                f"| Tags | {_clean_cell(tags)} |",
                f"| ADO URL | {work_item_url} |",
                "",
                "### Description",
                "",
                description or "_No description provided._",
                "",
                "### Acceptance Criteria",
                "",
                acceptance or "_No acceptance criteria provided._",
                "",
                "---",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def run(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")
    config = resolve_config(args)
    wiql = build_wiql(config)

    with requests.Session() as session:
        session.auth = ("", config.pat)
        session.headers.update({"Content-Type": "application/json"})
        ids = fetch_work_item_ids(session, config, wiql)
        work_items = fetch_work_items(session, config, ids)

    if args.dry_run:
        print("Resolved WIQL:")
        print(wiql)
        print(f"Fetched {len(work_items)} work items.")
        return 0

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_markdown(config, work_items), encoding="utf-8")
    print(f"Markdown written to {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run(args)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except requests.RequestException as error:
        print(f"Error: Azure DevOps request failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
