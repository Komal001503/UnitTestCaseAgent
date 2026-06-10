#!/usr/bin/env python3
"""FC S (File/Content Server) uploader for UnitTestCaseAgent documents.

Uploads **input** documents (user stories synced from Azure DevOps / converted
from Excel) and **output** documents (generated test-case reports) to the FC S
server using the URL pattern::

    https://vhziemqsqa.lthed.com:86/Home/Index?folder=UnitTestCaseAgent
        &tableid=<INPUT|OUTPUT>&linkedto=<ProjectName>_<Date>
        &psno=20342252&deleteright=False

.. note::
    ``/Home/Index`` is the **browse** page of an ASP.NET MVC app, not
    necessarily the real upload endpoint.  The actual HTTP method, upload path,
    and multipart field name are therefore configurable via environment
    variables (``FCS_HTTP_METHOD``, ``FCS_UPLOAD_PATH``, ``FCS_FIELD_NAME``)
    so that the client can be adapted once the real upload contract is
    confirmed.  The defaults match the documented URL so the system works
    out-of-the-box with the current endpoint.

Usage (CLI)::

    python scripts/fcs_uploader.py upload path/to/file.xlsx INPUT \\
        MyProject_2026-06-10 [--extra-params key=value ...]

    # Build the linkedto value automatically from a project name:
    python scripts/fcs_uploader.py upload path/to/report.xlsx OUTPUT \\
        --project-name "Workforce Management by MX Techies" [--date-stamp 2026-06-10]
"""

from __future__ import annotations

import argparse
import datetime
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import requests
from requests.auth import HTTPBasicAuth

# ---------------------------------------------------------------------------
# Re-use the canonical sanitiser from the export script to avoid duplicating
# the regex.  This is the single source of truth for project-name sanitisation
# across the whole tool-chain.
# ---------------------------------------------------------------------------
from scripts.export_tests_to_text import _sanitize_project_name  # noqa: PLC2701

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://vhziemqsqa.lthed.com:86"
# NOTE: /Home/Index is the ASP.NET MVC browse page; adjust FCS_UPLOAD_PATH
# once the real upload endpoint is confirmed.
DEFAULT_UPLOAD_PATH = "/Home/Index"
DEFAULT_HTTP_METHOD = "POST"
DEFAULT_FIELD_NAME = "file"
DEFAULT_FOLDER = "UnitTestCaseAgent"
DEFAULT_PSNO = "20342252"
DEFAULT_DELETE_RIGHT = "False"
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3

VALID_TABLE_IDS = {"INPUT", "OUTPUT"}


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class FCSUploadError(RuntimeError):
    """Raised when an upload to the FC S server fails after all retries."""

    def __init__(self, message: str, *, status_code: int | None = None, body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body

    def __str__(self) -> str:  # pragma: no cover
        base = super().__str__()
        if self.status_code is not None:
            return f"{base} (HTTP {self.status_code}): {self.body}"
        return base


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------


@dataclass
class FCSConfig:
    """Configuration for the FC S uploader client.

    All fields can be overridden via environment variables; see
    :meth:`from_env` for the mapping.
    """

    base_url: str = DEFAULT_BASE_URL
    upload_path: str = DEFAULT_UPLOAD_PATH
    http_method: str = DEFAULT_HTTP_METHOD
    field_name: str = DEFAULT_FIELD_NAME
    folder: str = DEFAULT_FOLDER
    psno: str = DEFAULT_PSNO
    delete_right: str = DEFAULT_DELETE_RIGHT
    username: str | None = None
    password: str | None = None
    token: str | None = None
    verify_ssl: bool = True
    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES

    # internal – collect unknown kwargs gracefully
    _extra: dict = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "FCSConfig":
        """Build a :class:`FCSConfig` from environment variables.

        Environment variable → field mapping:

        ========================  =============  =======================================
        Env var                   Default        Description
        ========================  =============  =======================================
        ``FCS_BASE_URL``          (see above)    Base URL of the FC S server
        ``FCS_UPLOAD_PATH``       /Home/Index    Path component for upload requests
        ``FCS_HTTP_METHOD``       POST           HTTP verb used for uploads
        ``FCS_FIELD_NAME``        file           Multipart form-field name for the file
        ``FCS_FOLDER``            UnitTestCase…  Fixed folder param sent in query string
        ``FCS_PSNO``              20342252       Project/site number
        ``FCS_DELETE_RIGHT``      False          Whether the upload grants delete rights
        ``FCS_USERNAME``          —              Basic-auth username (optional)
        ``FCS_PASSWORD``          —              Basic-auth password (optional)
        ``FCS_TOKEN``             —              Bearer token (alternative to basic auth)
        ``FCS_VERIFY_SSL``        true           Set to ``false`` to skip TLS verification
        ``FCS_TIMEOUT``           60             Request timeout in seconds
        ``FCS_MAX_RETRIES``       3              Max retry attempts on transient errors
        ========================  =============  =======================================
        """
        if env is None:
            env = os.environ  # type: ignore[assignment]

        def _get(key: str, default: str) -> str:
            return env.get(key, default)

        verify_ssl_raw = _get("FCS_VERIFY_SSL", "true").lower()
        verify_ssl = verify_ssl_raw not in {"false", "0", "no"}

        try:
            timeout = int(_get("FCS_TIMEOUT", str(DEFAULT_TIMEOUT)))
        except ValueError:
            timeout = DEFAULT_TIMEOUT

        try:
            max_retries = int(_get("FCS_MAX_RETRIES", str(DEFAULT_MAX_RETRIES)))
        except ValueError:
            max_retries = DEFAULT_MAX_RETRIES

        return cls(
            base_url=_get("FCS_BASE_URL", DEFAULT_BASE_URL),
            upload_path=_get("FCS_UPLOAD_PATH", DEFAULT_UPLOAD_PATH),
            http_method=_get("FCS_HTTP_METHOD", DEFAULT_HTTP_METHOD),
            field_name=_get("FCS_FIELD_NAME", DEFAULT_FIELD_NAME),
            folder=_get("FCS_FOLDER", DEFAULT_FOLDER),
            psno=_get("FCS_PSNO", DEFAULT_PSNO),
            delete_right=_get("FCS_DELETE_RIGHT", DEFAULT_DELETE_RIGHT),
            username=env.get("FCS_USERNAME") or None,
            password=env.get("FCS_PASSWORD") or None,
            token=env.get("FCS_TOKEN") or None,
            verify_ssl=verify_ssl,
            timeout=timeout,
            max_retries=max_retries,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_linked_to(project_name: str, date_stamp: str | None = None) -> str:
    """Build the ``linkedto`` query-parameter value for FC S uploads.

    The project name is sanitized using the same logic as the export script
    (``_sanitize_project_name`` from ``scripts/export_tests_to_text.py``), so
    the value is consistent across the entire tool-chain.

    Args:
        project_name: Raw project name (e.g. ``"Workforce Management by MX Techies"``).
        date_stamp:   Date string in ``YYYY-MM-DD`` format.  Defaults to
                      today's UTC date when *None*.

    Returns:
        A string like ``"WorkforceManagementByMXTechies_2026-06-10"``.
    """
    sanitized = _sanitize_project_name(project_name)
    if date_stamp is None:
        date_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return f"{sanitized}_{date_stamp}"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class FCSClient:
    """HTTP client for uploading files to the FC S server.

    Args:
        config: A :class:`FCSConfig` instance (use :meth:`FCSConfig.from_env`
                to build one from environment variables).
    """

    def __init__(self, config: FCSConfig) -> None:
        self._config = config
        if not config.verify_ssl:
            # Suppress InsecureRequestWarning only when verification is off.
            import urllib3  # lazy import – not needed when SSL is verified
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upload_file(
        self,
        local_path: Path,
        tableid: str,
        linkedto: str,
        *,
        extra_params: dict | None = None,
    ) -> dict:
        """Upload *local_path* to the FC S server.

        Args:
            local_path:   Path to the file to upload.
            tableid:      ``"INPUT"`` or ``"OUTPUT"`` (case-insensitive;
                          normalised to uppercase internally).
            linkedto:     Pairing key, e.g. ``"MyProject_2026-06-10"``.  Input
                          and matching output **must** share the same value so
                          they can be paired on the FC S side.
            extra_params: Optional dict of additional query parameters to
                          append to the upload URL.

        Returns:
            ``{"status_code": <int>, "url": "<str>", "body": <json-or-text>}``

        Raises:
            ValueError:       If *tableid* is not ``"INPUT"`` or ``"OUTPUT"``,
                              or if *local_path* does not exist.
            FCSUploadError:   If the upload fails after all retries.
        """
        tableid_upper = tableid.upper()
        if tableid_upper not in VALID_TABLE_IDS:
            raise ValueError(
                f"tableid must be one of {VALID_TABLE_IDS}; got {tableid!r}"
            )

        local_path = Path(local_path)
        if not local_path.exists():
            raise ValueError(f"File not found: {local_path}")

        url = self._build_url(tableid_upper, linkedto, extra_params)
        return self._upload_with_retry(local_path, url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_url(self, tableid: str, linkedto: str, extra_params: dict | None) -> str:
        cfg = self._config
        base = cfg.base_url.rstrip("/")
        path = cfg.upload_path
        params = {
            "folder": cfg.folder,
            "tableid": tableid,
            "linkedto": linkedto,
            "psno": cfg.psno,
            "deleteright": cfg.delete_right,
        }
        if extra_params:
            params.update(extra_params)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}{path}?{query}"

    def _build_auth(self):
        cfg = self._config
        if cfg.username and cfg.password:
            return HTTPBasicAuth(cfg.username, cfg.password)
        return None

    def _build_headers(self) -> dict:
        cfg = self._config
        headers: dict = {}
        if cfg.token and not (cfg.username and cfg.password):
            headers["Authorization"] = "Bearer " + cfg.token
        return headers

    def _upload_with_retry(self, local_path: Path, url: str) -> dict:
        cfg = self._config
        method = cfg.http_method.upper()
        auth = self._build_auth()
        headers = self._build_headers()
        last_exc: Exception | None = None
        last_status: int | None = None
        last_body: str = ""

        for attempt in range(cfg.max_retries):
            delay = 2 ** attempt  # 1s, 2s, 4s …  (attempt 0 → 1s, 1 → 2s, …)
            if attempt > 0:
                time.sleep(delay)

            try:
                with local_path.open("rb") as fh:
                    response = requests.request(
                        method,
                        url,
                        files={cfg.field_name: (local_path.name, fh)},
                        auth=auth,
                        headers=headers,
                        verify=cfg.verify_ssl,
                        timeout=cfg.timeout,
                    )
            except requests.exceptions.ConnectionError as exc:
                last_exc = exc
                continue
            except requests.exceptions.Timeout as exc:
                last_exc = exc
                continue

            last_status = response.status_code
            try:
                last_body = response.json()
            except Exception:
                last_body = response.text

            if response.status_code < 500:
                # 4xx → do not retry; 2xx/3xx → success
                if not response.ok:
                    raise FCSUploadError(
                        f"Upload failed: {local_path.name}",
                        status_code=response.status_code,
                        body=str(last_body),
                    )
                return {"status_code": response.status_code, "url": url, "body": last_body}

            # 5xx → retry
            last_exc = None  # reset connection error tracker

        # All retries exhausted
        if last_exc is not None:
            raise FCSUploadError(
                f"Upload failed after {cfg.max_retries} attempts: {last_exc}",
                status_code=None,
                body="",
            )
        raise FCSUploadError(
            f"Upload failed after {cfg.max_retries} attempts: {local_path.name}",
            status_code=last_status,
            body=str(last_body),
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Upload documents to the FC S (File/Content Server).\n\n"
            "NOTE: /Home/Index is the ASP.NET MVC browse page; adjust\n"
            "FCS_UPLOAD_PATH once the real upload endpoint is confirmed."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    up = sub.add_parser(
        "upload",
        help="Upload a single file to FC S.",
        description=(
            "Upload a file to FC S.  The --linkedto value can be given directly\n"
            "or derived from --project-name (with an optional --date-stamp)."
        ),
    )
    up.add_argument("local_path", type=Path, help="Path to the local file to upload.")
    up.add_argument(
        "tableid",
        choices=["INPUT", "OUTPUT", "input", "output"],
        help="FC S table identifier: INPUT for user stories, OUTPUT for test reports.",
    )
    up.add_argument(
        "linkedto",
        nargs="?",
        default=None,
        help=(
            "Pairing key, e.g. 'MyProject_2026-06-10'.  "
            "If omitted, --project-name must be provided."
        ),
    )
    up.add_argument(
        "--project-name",
        default=None,
        help=(
            "Project name used to build the linkedto value automatically. "
            "Sanitised to CamelCase; combined with --date-stamp (default: today UTC)."
        ),
    )
    up.add_argument(
        "--date-stamp",
        default=None,
        help="Date in YYYY-MM-DD format for the linkedto value (default: today UTC).",
    )
    up.add_argument(
        "--extra-params",
        nargs="*",
        metavar="KEY=VALUE",
        default=[],
        help="Additional query parameters to append to the upload URL.",
    )

    return parser.parse_args(argv)


def _run_upload(args) -> None:  # pragma: no branch
    linkedto = args.linkedto
    if not linkedto:
        if not args.project_name:
            raise SystemExit(
                "Either positional <linkedto> or --project-name must be provided."
            )
        linkedto = build_linked_to(args.project_name, args.date_stamp)

    extra: dict | None = None
    if args.extra_params:
        extra = {}
        for item in args.extra_params:
            if "=" not in item:
                raise SystemExit(f"Invalid extra-param (expected KEY=VALUE): {item!r}")
            k, _, v = item.partition("=")
            extra[k] = v

    config = FCSConfig.from_env()
    client = FCSClient(config)
    result = client.upload_file(
        local_path=args.local_path,
        tableid=args.tableid,
        linkedto=linkedto,
        extra_params=extra,
    )
    print(f"Uploaded successfully → {result['url']}")
    print(f"HTTP {result['status_code']}: {result['body']}")


def main(argv=None) -> None:
    args = _parse_args(argv)
    if args.command == "upload":
        _run_upload(args)


if __name__ == "__main__":
    main()
