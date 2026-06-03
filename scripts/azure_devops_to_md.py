#!/usr/bin/env python3
"""Fetch Azure DevOps User Stories and convert them into Markdown for the Unit Test Generator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping
from urllib.parse import quote

import html2text
import requests

API_VERSION = "7.1"
WIQL_LIMIT = 20_000
_BATCH_SIZE = 200


class MissingPATError(ValueError):
    """Raised when AZURE_DEVOPS_PAT is not provided."""


@dataclass(frozen=True)
class AzureDevOpsConfig:
    org: str
    project: str
    team: str | None
    pat: str
    work_item_type: str
    states: list[str] | None
    area_path: str | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pull Azure DevOps User Stories and convert them to Markdown."
    )
    parser.add_argument(
        "--output",
        default="azure_devops_user_stories.md",
        help="Output Markdown file path (default: azure_devops_user_stories.md)",
    )
    parser.add_argument("--org", help="Azure DevOps organization (or AZURE_DEVOPS_ORG)")
    parser.add_argument("--project", help="Azure DevOps project (or AZURE_DEVOPS_PROJECT)")
    parser.add_argument(
        "--team",
        help="Azure DevOps team name (optional, or AZURE_DEVOPS_TEAM)",
    )
    parser.add_argument(
        "--work-item-type",
        help="Work item type (default: AZURE_DEVOPS_WORK_ITEM_TYPE or User Story)",
    )
    parser.add_argument(
        "--states",
        help="CSV of states to include (default: all except Removed)",
    )
    parser.add_argument(
        "--area-path",
        help="Optional area path filter (or AZURE_DEVOPS_AREA_PATH)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print Markdown instead of writing file")
    parser.add_argument("--verbose", action="store_true", help="Print progress details")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _csv_to_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _pick_arg_or_env(arg_value: str | None, env: Mapping[str, str], env_name: str) -> str | None:
    if arg_value is not None:
        return arg_value
    return env.get(env_name)


def resolve_config(args: argparse.Namespace, env: Mapping[str, str]) -> AzureDevOpsConfig:
    org = _pick_arg_or_env(args.org, env, "AZURE_DEVOPS_ORG")
    project = _pick_arg_or_env(args.project, env, "AZURE_DEVOPS_PROJECT")
    team = _pick_arg_or_env(args.team, env, "AZURE_DEVOPS_TEAM")
    pat = _pick_arg_or_env(None, env, "AZURE_DEVOPS_PAT")
    work_item_type = _pick_arg_or_env(
        args.work_item_type,
        env,
        "AZURE_DEVOPS_WORK_ITEM_TYPE",
    ) or "User Story"
    states = _csv_to_list(_pick_arg_or_env(args.states, env, "AZURE_DEVOPS_STATES"))
    area_path = _pick_arg_or_env(args.area_path, env, "AZURE_DEVOPS_AREA_PATH")

    if not org:
        raise ValueError("Missing Azure DevOps organization. Set --org or AZURE_DEVOPS_ORG.")
    if not project:
        raise ValueError("Missing Azure DevOps project. Set --project or AZURE_DEVOPS_PROJECT.")
    if not pat:
        raise MissingPATError(
            "Missing AZURE_DEVOPS_PAT. Provide a PAT with Work Items: Read scope."
        )

    return AzureDevOpsConfig(
        org=org,
        project=project,
        team=team or None,
        pat=pat,
        work_item_type=work_item_type,
        states=states,
        area_path=area_path,
    )


def _escape_wiql_value(value: str) -> str:
    return value.replace("'", "''")


def build_wiql(config: AzureDevOpsConfig) -> str:
    filters = [f"[System.WorkItemType] = '{_escape_wiql_value(config.work_item_type)}'"]

    if config.states:
        escaped_states = ", ".join(f"'{_escape_wiql_value(state)}'" for state in config.states)
        filters.append(f"[System.State] IN ({escaped_states})")
    else:
        filters.append("[System.State] <> 'Removed'")

    if config.area_path:
        filters.append(f"[System.AreaPath] UNDER '{_escape_wiql_value(config.area_path)}'")

    where_clause = "\n  AND ".join(filters)
    return (
        "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], "
        "[Microsoft.VSTS.Common.Priority], [System.Description], "
        "[Microsoft.VSTS.Common.AcceptanceCriteria], [System.Tags], [System.AreaPath], "
        "[System.IterationPath]\n"
        "FROM WorkItems\n"
        f"WHERE {where_clause}\n"
        "ORDER BY [System.Id] ASC"
    )


def _base_project_url(config: AzureDevOpsConfig) -> str:
    return "https://dev.azure.com/{org}/{project}".format(
        org=quote(config.org, safe=""),
        project=quote(config.project, safe=""),
    )


def wiql_url(config: AzureDevOpsConfig) -> str:
    base = _base_project_url(config)
    if config.team:
        return f"{base}/{quote(config.team, safe='')}/_apis/wit/wiql?api-version={API_VERSION}"
    return f"{base}/_apis/wit/wiql?api-version={API_VERSION}"


def work_items_batch_url(config: AzureDevOpsConfig) -> str:
    return f"{_base_project_url(config)}/_apis/wit/workitemsbatch?api-version={API_VERSION}"


def _raise_for_http_error(response: requests.Response, context: str) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        if response.status_code == 401:
            raise RuntimeError(
                f"{context} failed with HTTP 401 Unauthorized. Check PAT scopes/expiry."
            ) from error
        if response.status_code == 404:
            raise RuntimeError(
                f"{context} failed with HTTP 404 Not Found. Check org/project/team name."
            ) from error

        detail = response.text.strip()
        if len(detail) > 300:
            detail = f"{detail[:297]}..."
        suffix = f" Details: {detail}" if detail else ""
        raise RuntimeError(
            f"{context} failed with HTTP {response.status_code}.{suffix}"
        ) from error


def _chunked(values: list[int], size: int) -> Iterable[list[int]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def query_work_item_ids(config: AzureDevOpsConfig, verbose: bool = False) -> list[int]:
    if verbose:
        print("Running WIQL query against Azure DevOps...", file=sys.stderr)

    response = requests.post(
        wiql_url(config),
        json={"query": build_wiql(config)},
        auth=("", config.pat),
        timeout=30,
    )
    _raise_for_http_error(response, "WIQL query")
    payload = response.json()

    ids = sorted(
        int(item["id"])
        for item in payload.get("workItems", [])
        if isinstance(item, dict) and "id" in item
    )

    if len(ids) >= WIQL_LIMIT:
        print(
            "Warning: WIQL may return at most 20,000 items. Narrow the query if results are incomplete.",
            file=sys.stderr,
        )

    return ids


def fetch_work_items(config: AzureDevOpsConfig, ids: list[int], verbose: bool = False) -> list[dict[str, Any]]:
    if not ids:
        return []

    fields = [
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

    work_items: list[dict[str, Any]] = []
    for batch_number, chunk in enumerate(_chunked(ids, _BATCH_SIZE), start=1):
        if verbose:
            print(
                f"Fetching batch {batch_number} containing {len(chunk)} work item(s)...",
                file=sys.stderr,
            )

        response = requests.post(
            work_items_batch_url(config),
            json={"ids": chunk, "fields": fields},
            auth=("", config.pat),
            timeout=30,
        )
        _raise_for_http_error(response, "Work items batch query")
        payload = response.json()
        for item in payload.get("value", []):
            if isinstance(item, dict):
                work_items.append(item)

    work_items.sort(key=lambda item: int(item.get("id", 0)))
    return work_items


def _html_to_markdown(value: str | None) -> str:
    if not value:
        return "_Not provided._"

    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_images = True
    converter.single_line_break = True

    markdown = converter.handle(value).strip()
    return markdown or "_Not provided._"


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>").replace("|", "\\|")


def _assigned_to_display(assigned_to: Any) -> str:
    if isinstance(assigned_to, dict):
        display_name = assigned_to.get("displayName")
        unique_name = assigned_to.get("uniqueName")
        return str(display_name or unique_name or "Unassigned")
    if assigned_to:
        return str(assigned_to)
    return "Unassigned"


def render_markdown(work_items: list[dict[str, Any]], org: str, project: str) -> str:
    lines: list[str] = [
        "# User Stories",
        "",
        f"Total stories: {len(work_items)}",
        "",
        "| Story ID | Title | State | Priority | Assigned To |",
        "|----------|-------|-------|----------|-------------|",
    ]

    for item in work_items:
        fields = item.get("fields", {}) if isinstance(item.get("fields"), dict) else {}
        story_id = int(item.get("id", 0))
        title = _clean_cell(fields.get("System.Title") or "Untitled")
        state = _clean_cell(fields.get("System.State") or "")
        priority = _clean_cell(fields.get("Microsoft.VSTS.Common.Priority") or "")
        assigned_to = _clean_cell(_assigned_to_display(fields.get("System.AssignedTo")))
        lines.append(f"| US-{story_id} | {title} | {state} | {priority} | {assigned_to} |")

    for item in work_items:
        fields = item.get("fields", {}) if isinstance(item.get("fields"), dict) else {}
        story_id = int(item.get("id", 0))
        title = _clean_cell(fields.get("System.Title") or "Untitled")
        state = _clean_cell(fields.get("System.State") or "")
        priority = _clean_cell(fields.get("Microsoft.VSTS.Common.Priority") or "")
        assigned_to = _clean_cell(_assigned_to_display(fields.get("System.AssignedTo")))
        area_path = _clean_cell(fields.get("System.AreaPath") or "")
        iteration_path = _clean_cell(fields.get("System.IterationPath") or "")
        tags = _clean_cell(fields.get("System.Tags") or "")
        ado_url = (
            f"https://dev.azure.com/{quote(org, safe='')}/{quote(project, safe='')}/_workitems/edit/{story_id}"
        )

        lines.extend(
            [
                "",
                f"## US-{story_id} — {title}",
                "",
                "| Field | Value |",
                "|-------|-------|",
                f"| ID | US-{story_id} |",
                f"| State | {state} |",
                f"| Priority | {priority} |",
                f"| Assigned To | {assigned_to} |",
                f"| Area Path | {area_path} |",
                f"| Iteration Path | {iteration_path} |",
                f"| Tags | {tags} |",
                f"| ADO URL | [Open in ADO]({ado_url}) |",
                "",
                "### Description",
                "",
                _html_to_markdown(fields.get("System.Description")),
                "",
                "### Acceptance Criteria",
                "",
                _html_to_markdown(fields.get("Microsoft.VSTS.Common.AcceptanceCriteria")),
            ]
        )

    return "\n".join(lines).strip() + "\n"


def run(args: argparse.Namespace, env: Mapping[str, str]) -> tuple[Path | None, str]:
    config = resolve_config(args, env)
    ids = query_work_item_ids(config, verbose=args.verbose)
    work_items = fetch_work_items(config, ids, verbose=args.verbose)
    markdown = render_markdown(work_items, config.org, config.project)

    if args.dry_run:
        return None, markdown

    output_path = Path(args.output)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path, markdown


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    try:
        output_path, markdown = run(args, os.environ)
    except MissingPATError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except Exception as error:  # pragma: no cover - defensive CLI handling
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    if args.dry_run:
        print(markdown)
        print("Dry run complete. No file written.", file=sys.stderr)
        return

    print(f"Markdown written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
