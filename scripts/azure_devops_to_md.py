#!/usr/bin/env python3
"""Fetch User Stories from Azure DevOps Boards and write them to a Markdown file.

The output Markdown is compatible with the Unit Test Generator agent — invoke it exactly
as you would for a file produced by ``scripts/excel_to_md.py``.

WIQL note: Azure DevOps caps WIQL result sets at 20,000 work-item IDs.  If your backlog
exceeds that limit the script will process only the first 20,000 items returned by the
query.

Environment variables (CLI flags override):
  AZURE_DEVOPS_ORG               ADO organisation name (required)
  AZURE_DEVOPS_PROJECT           ADO project name (required)
  AZURE_DEVOPS_TEAM              ADO team name (optional; omit for project-level endpoint)
  AZURE_DEVOPS_PAT               Personal Access Token with Work Items: Read scope (required)
  AZURE_DEVOPS_WORK_ITEM_TYPE    Work item type to fetch (default: "User Story")
  AZURE_DEVOPS_STATES            Comma-separated state filter (default: all except Removed)
  AZURE_DEVOPS_AREA_PATH         Area path filter (optional)
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from typing import Any

import html2text
import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_VERSION = "7.1"
BATCH_SIZE = 200  # max IDs per workitemsbatch call


# ---------------------------------------------------------------------------
# HTML → plain-text helper
# ---------------------------------------------------------------------------
def _html_to_md(html: str | None) -> str:
    """Convert an HTML string to clean plain-text / Markdown."""
    if not html:
        return ""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.body_width = 0  # no line-wrapping
    return converter.handle(html).strip()


# ---------------------------------------------------------------------------
# Azure DevOps API helpers
# ---------------------------------------------------------------------------
def _base_url(org: str, project: str, team: str | None = None) -> str:
    parts = ["https://dev.azure.com", org, project]
    if team:
        parts.append(team)
    return "/".join(parts)


def _run_wiql(
    org: str,
    project: str,
    team: str | None,
    pat: str,
    work_item_type: str,
    states: list[str] | None,
    area_path: str | None,
    verbose: bool,
) -> list[int]:
    """Execute a WIQL query and return a sorted list of matching work-item IDs."""
    conditions = [f"[System.WorkItemType] = '{work_item_type}'"]
    if states:
        quoted = ", ".join(f"'{s}'" for s in states)
        conditions.append(f"[System.State] IN ({quoted})")
    else:
        conditions.append("[System.State] <> 'Removed'")
    if area_path:
        conditions.append(f"[System.AreaPath] UNDER '{area_path}'")

    where_clause = " AND ".join(conditions)
    wiql = (
        "SELECT [System.Id], [System.Title], [System.State], "
        "[System.AssignedTo], [Microsoft.VSTS.Common.Priority], "
        "[System.Description], [Microsoft.VSTS.Common.AcceptanceCriteria], "
        "[System.Tags], [System.AreaPath], [System.IterationPath] "
        f"FROM WorkItems WHERE {where_clause} ORDER BY [System.Id] ASC"
    )

    base = _base_url(org, project, team)
    url = f"{base}/_apis/wit/wiql?api-version={API_VERSION}"

    if verbose:
        print(f"[verbose] WIQL endpoint: {url}", file=sys.stderr)
        print(f"[verbose] WIQL query:\n{wiql}", file=sys.stderr)

    resp = requests.post(url, json={"query": wiql}, auth=("", pat), timeout=60)
    _check_response(resp, org, project, team)

    work_item_refs = resp.json().get("workItems", [])
    ids = sorted(int(item["id"]) for item in work_item_refs)
    if verbose:
        print(f"[verbose] WIQL returned {len(ids)} work-item ID(s).", file=sys.stderr)
    return ids


def _fetch_work_items(
    org: str,
    project: str,
    ids: list[int],
    pat: str,
    verbose: bool,
) -> list[dict[str, Any]]:
    """Batch-fetch full work items for *ids* (chunks of BATCH_SIZE)."""
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
    url = (
        f"https://dev.azure.com/{org}/{project}"
        f"/_apis/wit/workitemsbatch?api-version={API_VERSION}"
    )
    items: list[dict[str, Any]] = []
    for i in range(0, len(ids), BATCH_SIZE):
        chunk = ids[i : i + BATCH_SIZE]
        if verbose:
            print(
                f"[verbose] Fetching work items {chunk[0]}–{chunk[-1]} "
                f"({len(chunk)} item(s))…",
                file=sys.stderr,
            )
        resp = requests.post(
            url,
            json={"ids": chunk, "fields": fields},
            auth=("", pat),
            timeout=120,
        )
        _check_response(resp, org, project, None)
        items.extend(resp.json().get("value", []))
    return items


def _check_response(
    resp: requests.Response,
    org: str,
    project: str,
    team: str | None,
) -> None:
    """Raise a friendly error on HTTP 4xx/5xx."""
    if resp.status_code == 401:
        print(
            "Error: HTTP 401 Unauthorized. "
            "Check that AZURE_DEVOPS_PAT is correct, not expired, "
            "and has 'Work Items: Read' scope.",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code == 404:
        target = f"org='{org}', project='{project}'"
        if team:
            target += f", team='{team}'"
        print(
            f"Error: HTTP 404 Not Found. "
            f"Check the organisation, project, and team names ({target}).",
            file=sys.stderr,
        )
        sys.exit(1)
    resp.raise_for_status()


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------
def _field(item: dict[str, Any], name: str) -> str:
    """Return a work-item field value as a string (empty string if absent)."""
    value = item.get("fields", {}).get(name)
    if value is None:
        return ""
    # AssignedTo is a dict with a "displayName" key
    if isinstance(value, dict):
        return value.get("displayName", "")
    return str(value)


def _render_markdown(
    items: list[dict[str, Any]],
    org: str,
    project: str,
) -> str:
    """Convert a list of ADO work-item dicts to a Markdown string."""
    lines: list[str] = []

    # ── Top-of-file summary table ──────────────────────────────────────────
    lines.append("# Azure DevOps User Stories\n")
    lines.append(
        f"| Story ID | Title | State | Priority | Assigned To |"
    )
    lines.append(
        f"|----------|-------|-------|----------|-------------|"
    )
    for item in items:
        sid = _field(item, "System.Id")
        title = _field(item, "System.Title").replace("|", "\\|")
        state = _field(item, "System.State")
        priority = _field(item, "Microsoft.VSTS.Common.Priority")
        assigned = _field(item, "System.AssignedTo").replace("|", "\\|")
        lines.append(f"| US-{sid} | {title} | {state} | {priority} | {assigned} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Individual story sections ─────────────────────────────────────────
    for item in items:
        sid = _field(item, "System.Id")
        title = _field(item, "System.Title")
        state = _field(item, "System.State")
        priority = _field(item, "Microsoft.VSTS.Common.Priority")
        assigned = _field(item, "System.AssignedTo")
        area = _field(item, "System.AreaPath")
        iteration = _field(item, "System.IterationPath")
        tags = _field(item, "System.Tags")
        ado_url = (
            f"https://dev.azure.com/{org}/{project}/_workitems/edit/{sid}"
        )

        description_md = _html_to_md(_field(item, "System.Description"))
        acceptance_md = _html_to_md(
            _field(item, "Microsoft.VSTS.Common.AcceptanceCriteria")
        )

        lines.append(f"## US-{sid} — {title}\n")

        # Metadata table
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| ID | {sid} |")
        lines.append(f"| State | {state} |")
        lines.append(f"| Priority | {priority} |")
        lines.append(f"| Assigned To | {assigned} |")
        lines.append(f"| Area Path | {area} |")
        lines.append(f"| Iteration Path | {iteration} |")
        lines.append(f"| Tags | {tags} |")
        lines.append(f"| ADO URL | {ado_url} |")
        lines.append("")

        lines.append("### Description\n")
        lines.append(description_md if description_md else "_No description provided._")
        lines.append("")

        lines.append("### Acceptance Criteria\n")
        lines.append(
            acceptance_md if acceptance_md else "_No acceptance criteria provided._"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch User Stories from Azure DevOps Boards and write them to "
            "a Markdown file consumable by the Unit Test Generator agent."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Environment variables (all overridable by the corresponding flag):
              AZURE_DEVOPS_ORG               ADO organisation name
              AZURE_DEVOPS_PROJECT           ADO project name
              AZURE_DEVOPS_TEAM              ADO team name (optional)
              AZURE_DEVOPS_PAT               Personal Access Token (required)
              AZURE_DEVOPS_WORK_ITEM_TYPE    Work item type (default: User Story)
              AZURE_DEVOPS_STATES            Comma-separated state filter
              AZURE_DEVOPS_AREA_PATH         Area path filter (optional)
            """
        ),
    )
    parser.add_argument(
        "--org",
        default=os.environ.get("AZURE_DEVOPS_ORG", ""),
        help="Azure DevOps organisation name (env: AZURE_DEVOPS_ORG)",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("AZURE_DEVOPS_PROJECT", ""),
        help="Azure DevOps project name (env: AZURE_DEVOPS_PROJECT)",
    )
    parser.add_argument(
        "--team",
        default=os.environ.get("AZURE_DEVOPS_TEAM", ""),
        help="Azure DevOps team name (env: AZURE_DEVOPS_TEAM, optional)",
    )
    parser.add_argument(
        "--work-item-type",
        default=os.environ.get("AZURE_DEVOPS_WORK_ITEM_TYPE", "User Story"),
        help="Work item type to fetch (env: AZURE_DEVOPS_WORK_ITEM_TYPE, default: User Story)",
    )
    parser.add_argument(
        "--states",
        default=os.environ.get("AZURE_DEVOPS_STATES", ""),
        help=(
            "Comma-separated list of states to include "
            "(env: AZURE_DEVOPS_STATES, default: all except Removed)"
        ),
    )
    parser.add_argument(
        "--area-path",
        default=os.environ.get("AZURE_DEVOPS_AREA_PATH", ""),
        help="Area path filter (env: AZURE_DEVOPS_AREA_PATH, optional)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="azure_devops_user_stories.md",
        help="Output Markdown file path (default: azure_devops_user_stories.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved WIQL and matched item count; do not write output file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging to stderr",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # ── Validate required config ───────────────────────────────────────────
    pat = os.environ.get("AZURE_DEVOPS_PAT", "")
    if not pat:
        print(
            "Error: AZURE_DEVOPS_PAT environment variable is required but not set.\n"
            "Create a PAT at https://dev.azure.com with 'Work Items: Read' scope "
            "and export it as AZURE_DEVOPS_PAT.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.org:
        print(
            "Error: Azure DevOps organisation not specified. "
            "Use --org or set AZURE_DEVOPS_ORG.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.project:
        print(
            "Error: Azure DevOps project not specified. "
            "Use --project or set AZURE_DEVOPS_PROJECT.",
            file=sys.stderr,
        )
        sys.exit(1)

    team: str | None = args.team or None
    states: list[str] | None = (
        [s.strip() for s in args.states.split(",") if s.strip()]
        if args.states
        else None
    )
    area_path: str | None = args.area_path or None

    # ── Run WIQL ──────────────────────────────────────────────────────────
    ids = _run_wiql(
        org=args.org,
        project=args.project,
        team=team,
        pat=pat,
        work_item_type=args.work_item_type,
        states=states,
        area_path=area_path,
        verbose=args.verbose,
    )

    if args.dry_run:
        print(f"Dry run: {len(ids)} work item(s) matched.", file=sys.stderr)
        print(f"IDs: {ids}", file=sys.stderr)
        return

    if not ids:
        print(
            "No matching work items found. "
            "Check your filters (--states, --area-path, --work-item-type).",
            file=sys.stderr,
        )
        sys.exit(0)

    # ── Fetch full work items ─────────────────────────────────────────────
    items = _fetch_work_items(
        org=args.org,
        project=args.project,
        ids=ids,
        pat=pat,
        verbose=args.verbose,
    )

    # Sort deterministically by Id ascending
    items.sort(key=lambda it: int(it.get("id", 0)))

    # ── Render Markdown ───────────────────────────────────────────────────
    markdown = _render_markdown(items, org=args.org, project=args.project)

    # ── Write output ──────────────────────────────────────────────────────
    output_path = args.output
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    print(f"Markdown written to {output_path} ({len(items)} story/stories).", file=sys.stderr)


if __name__ == "__main__":
    main()
