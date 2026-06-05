#!/usr/bin/env python3
"""Fetch Azure DevOps User Stories and convert them into Markdown for the Unit Test Generator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
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
    pat: str
    work_item_type: str
    team: str | None = None
    states: list[str] | None = None
    area_path: str | None = None
    iteration_path: str | None = None
    assigned_to: str | None = None
    tags: list[str] | None = None
    ids: list[int] | None = None
    from_date: date | None = None
    to_date: date | None = None
    date_field: str | None = None


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
    parser.add_argument(
        "--iteration-path",
        help="Optional iteration path filter (or AZURE_DEVOPS_ITERATION_PATH)",
    )
    parser.add_argument(
        "--assigned-to",
        help="Optional assignee filter (or AZURE_DEVOPS_ASSIGNED_TO)",
    )
    parser.add_argument(
        "--tags",
        help="CSV of tags; item must contain all tags (or AZURE_DEVOPS_TAGS)",
    )
    parser.add_argument(
        "--ids",
        help="CSV of work item IDs (or AZURE_DEVOPS_IDS)",
    )
    parser.add_argument(
        "--from-date",
        help="Lower bound date in YYYY-MM-DD (or AZURE_DEVOPS_FROM_DATE)",
    )
    parser.add_argument(
        "--to-date",
        help="Upper bound date in YYYY-MM-DD (or AZURE_DEVOPS_TO_DATE)",
    )
    parser.add_argument(
        "--date-field",
        choices=["None", "ChangedDate", "CreatedDate"],
        help="Optional date field for from/to date filters (or AZURE_DEVOPS_DATE_FIELD)",
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


def _csv_to_int_list(value: str | None, *, verbose: bool = False) -> list[int] | None:
    if value is None:
        return None

    valid_ids: list[int] = []
    dropped: list[str] = []
    for item in value.split(","):
        token = item.strip()
        if not token:
            continue
        try:
            valid_ids.append(int(token))
        except ValueError:
            dropped.append(token)

    if dropped and verbose:
        print(
            f"Warning: ignored non-integer IDs: {', '.join(dropped)}",
            file=sys.stderr,
        )
    return valid_ids or None


def _parse_iso_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Invalid date '{value}': expected YYYY-MM-DD") from error


def _normalize_date_field(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    normalized_lower = normalized.lower()
    if not normalized or normalized_lower == "none":
        return None
    if normalized_lower == "changeddate":
        return "ChangedDate"
    if normalized_lower == "createddate":
        return "CreatedDate"
    raise ValueError("Invalid date field. Expected None, ChangedDate or CreatedDate.")


def _effective_date_field(
    from_date: date | None, to_date: date | None, date_field: str | None
) -> str | None:
    if not from_date and not to_date:
        return None
    return date_field or "ChangedDate"


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
    iteration_path = _pick_arg_or_env(
        getattr(args, "iteration_path", None), env, "AZURE_DEVOPS_ITERATION_PATH"
    )
    assigned_to = _pick_arg_or_env(getattr(args, "assigned_to", None), env, "AZURE_DEVOPS_ASSIGNED_TO")
    tags = _csv_to_list(_pick_arg_or_env(getattr(args, "tags", None), env, "AZURE_DEVOPS_TAGS"))
    ids = _csv_to_int_list(
        _pick_arg_or_env(getattr(args, "ids", None), env, "AZURE_DEVOPS_IDS"),
        verbose=bool(getattr(args, "verbose", False)),
    )
    from_date = _parse_iso_date(
        _pick_arg_or_env(getattr(args, "from_date", None), env, "AZURE_DEVOPS_FROM_DATE")
    )
    to_date = _parse_iso_date(_pick_arg_or_env(getattr(args, "to_date", None), env, "AZURE_DEVOPS_TO_DATE"))
    date_field = _normalize_date_field(
        _pick_arg_or_env(getattr(args, "date_field", None), env, "AZURE_DEVOPS_DATE_FIELD")
    )

    if not org:
        raise ValueError("Missing Azure DevOps organization. Set --org or AZURE_DEVOPS_ORG.")
    if not project:
        raise ValueError("Missing Azure DevOps project. Set --project or AZURE_DEVOPS_PROJECT.")
    if not pat:
        raise MissingPATError(
            "Missing AZURE_DEVOPS_PAT. Provide a PAT with Work Items: Read scope."
        )
    if from_date and to_date and from_date > to_date:
        raise ValueError(
            f"Invalid date range: from-date {from_date.isoformat()} is after to-date {to_date.isoformat()}."
        )

    return AzureDevOpsConfig(
        org=org,
        project=project,
        team=team or None,
        pat=pat,
        work_item_type=work_item_type,
        states=states,
        area_path=area_path,
        iteration_path=iteration_path,
        assigned_to=assigned_to,
        tags=tags,
        ids=ids,
        from_date=from_date,
        to_date=to_date,
        date_field=date_field,
    )


def _escape_wiql_value(value: str) -> str:
    return value.replace("'", "''")


def build_wiql(config: AzureDevOpsConfig) -> str:
    date_field = _effective_date_field(config.from_date, config.to_date, config.date_field)
    filters = [f"[System.WorkItemType] = '{_escape_wiql_value(config.work_item_type)}'"]

    if config.states:
        escaped_states = ", ".join(f"'{_escape_wiql_value(state)}'" for state in config.states)
        filters.append(f"[System.State] IN ({escaped_states})")
    else:
        filters.append("[System.State] <> 'Removed'")

    if config.area_path:
        filters.append(f"[System.AreaPath] UNDER '{_escape_wiql_value(config.area_path)}'")
    if config.iteration_path:
        filters.append(f"[System.IterationPath] UNDER '{_escape_wiql_value(config.iteration_path)}'")
    if config.assigned_to:
        filters.append(f"[System.AssignedTo] CONTAINS '{_escape_wiql_value(config.assigned_to)}'")
    if config.tags:
        for tag in config.tags:
            filters.append(f"[System.Tags] CONTAINS '{_escape_wiql_value(tag)}'")
    if config.ids:
        joined_ids = ", ".join(str(work_item_id) for work_item_id in config.ids)
        filters.append(f"[System.Id] IN ({joined_ids})")
    if config.from_date and date_field:
        filters.append(f"[System.{date_field}] >= '{config.from_date.isoformat()}'")
    if config.to_date and date_field:
        filters.append(f"[System.{date_field}] <= '{config.to_date.isoformat()}T23:59:59'")

    where_clause = "\n  AND ".join(filters)
    return (
        "SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], [System.AssignedTo], "
        "[Microsoft.VSTS.Common.Priority], [System.Description], "
        "[Microsoft.VSTS.Common.AcceptanceCriteria], [System.Tags], [System.AreaPath], "
        "[System.IterationPath], [System.ChangedDate], [System.CreatedDate]\n"
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


def _is_team_not_found_error(response: requests.Response) -> bool:
    """Return True when the response is an HTTP 500 TeamNotFoundException."""
    if response.status_code != 500:
        return False
    try:
        body = response.json()
        return body.get("typeKey") == "TeamNotFoundException"
    except Exception:
        return False


def _chunked(values: list[int], size: int) -> Iterable[list[int]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def query_work_item_ids(config: AzureDevOpsConfig, verbose: bool = False) -> list[int]:
    if verbose:
        print("Running WIQL query against Azure DevOps...", file=sys.stderr)

    wiql_query = build_wiql(config)
    response = requests.post(
        wiql_url(config),
        json={"query": wiql_query},
        auth=("", config.pat),
        timeout=30,
    )

    # If the team name is invalid Azure DevOps returns HTTP 500 TeamNotFoundException.
    # Retry without the team context so the query still runs at the project level.
    if config.team and _is_team_not_found_error(response):
        print(
            f"Warning: team '{config.team}' was not found; retrying WIQL query without team context.",
            file=sys.stderr,
        )
        fallback_config = AzureDevOpsConfig(
            org=config.org,
            project=config.project,
            pat=config.pat,
            work_item_type=config.work_item_type,
            team=None,
            states=config.states,
            area_path=config.area_path,
            iteration_path=config.iteration_path,
            assigned_to=config.assigned_to,
            tags=config.tags,
            ids=config.ids,
            from_date=config.from_date,
            to_date=config.to_date,
            date_field=config.date_field,
        )
        response = requests.post(
            wiql_url(fallback_config),
            json={"query": wiql_query},
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

    if not ids:
        print(
            f"No work items matched type='{config.work_item_type}'. "
            "If your project uses a different process template, try "
            '--work-item-type "Product Backlog Item" (Scrum), "Issue" (Basic), or "Requirement" (CMMI).',
            file=sys.stderr,
        )

    return ids


def fetch_work_items(config: AzureDevOpsConfig, ids: list[int], verbose: bool = False) -> list[dict[str, Any]]:
    if not ids:
        return []

    fields = [
        "System.Id",
        "System.Title",
        "System.WorkItemType",
        "System.State",
        "System.AssignedTo",
        "Microsoft.VSTS.Common.Priority",
        "System.Description",
        "Microsoft.VSTS.Common.AcceptanceCriteria",
        "System.Tags",
        "System.AreaPath",
        "System.IterationPath",
        "System.ChangedDate",
        "System.CreatedDate",
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


def _filter_to_type(work_items: list[dict[str, Any]], work_item_type: str) -> list[dict[str, Any]]:
    """Drop any work items whose type does not match *work_item_type* (case-insensitive, trimmed).

    Logs a warning to stderr for every work item that is dropped, grouped by type.
    """
    target = work_item_type.strip().lower()
    kept: list[dict[str, Any]] = []
    dropped_by_type: dict[str, int] = {}

    for item in work_items:
        fields = item.get("fields", {}) if isinstance(item.get("fields"), dict) else {}
        actual = str(fields.get("System.WorkItemType", "")).strip()
        if actual.lower() == target:
            kept.append(item)
        else:
            dropped_by_type[actual] = dropped_by_type.get(actual, 0) + 1

    if dropped_by_type:
        total = sum(dropped_by_type.values())
        detail = ", ".join(f"{k}={v}" for k, v in sorted(dropped_by_type.items()))
        print(
            f"Warning: dropped {total} work item(s) whose type did not match "
            f"'{work_item_type}' (found: {detail}).",
            file=sys.stderr,
        )

    return kept


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


def render_markdown(
    work_items: list[dict[str, Any]],
    org: str,
    project: str,
    work_item_type: str = "User Story",
    states: list[str] | None = None,
    area_path: str | None = None,
    iteration_path: str | None = None,
    assigned_to: str | None = None,
    tags: list[str] | None = None,
    ids: list[int] | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    date_field: str | None = None,
) -> str:
    effective_date_field = _effective_date_field(from_date, to_date, date_field)
    filter_parts = [f"type={work_item_type}"]
    if states:
        filter_parts.append(f"states={', '.join(states)}")
    if iteration_path:
        filter_parts.append(f"iteration={iteration_path}")
    if area_path:
        filter_parts.append(f"area={area_path}")
    if assigned_to:
        filter_parts.append(f"assigned_to={assigned_to}")
    if tags:
        filter_parts.append(f"tags={','.join(tags)}")
    if ids:
        filter_parts.append(f"ids={','.join(str(item_id) for item_id in ids)}")
    if from_date and to_date and effective_date_field:
        filter_parts.append(
            f"{effective_date_field.replace('Date', '').lower()} between {from_date.isoformat()} and {to_date.isoformat()}"
        )
    elif from_date and effective_date_field:
        filter_parts.append(
            f"{effective_date_field.replace('Date', '').lower()} on/after {from_date.isoformat()}"
        )
    elif to_date and effective_date_field:
        filter_parts.append(
            f"{effective_date_field.replace('Date', '').lower()} on/before {to_date.isoformat()}"
        )

    lines: list[str] = [
        "# User Stories",
        "",
        f"_Filters: {' · '.join(filter_parts)}._",
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
        changed_date = _clean_cell(fields.get("System.ChangedDate") or "")
        created_date = _clean_cell(fields.get("System.CreatedDate") or "")
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
                f"| Work Item Type | {_clean_cell(fields.get('System.WorkItemType'))} |",
                f"| State | {state} |",
                f"| Priority | {priority} |",
                f"| Assigned To | {assigned_to} |",
                f"| Area Path | {area_path} |",
                f"| Iteration Path | {iteration_path} |",
                f"| Changed Date | {changed_date} |",
                f"| Created Date | {created_date} |",
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
    wiql = build_wiql(config)
    if args.dry_run:
        print("Resolved WIQL:", file=sys.stderr)
        print(wiql, file=sys.stderr)
    ids = query_work_item_ids(config, verbose=args.verbose)
    if args.dry_run:
        print(f"Matching work item IDs: {len(ids)}", file=sys.stderr)
    work_items = fetch_work_items(config, ids, verbose=args.verbose)
    work_items = _filter_to_type(work_items, config.work_item_type)
    markdown = render_markdown(
        work_items,
        config.org,
        config.project,
        work_item_type=config.work_item_type,
        states=config.states,
        area_path=config.area_path,
        iteration_path=config.iteration_path,
        assigned_to=config.assigned_to,
        tags=config.tags,
        ids=config.ids,
        from_date=config.from_date,
        to_date=config.to_date,
        date_field=config.date_field,
    )

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
