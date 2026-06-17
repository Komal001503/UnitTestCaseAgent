#!/usr/bin/env python3
"""FC S (File/Content Server) uploader for UnitTestCaseAgent documents.

Uploads **input** documents (user stories synced from Azure DevOps / converted
from Excel) and **output** documents (generated test-case reports) to the FC S
server using the URL pattern::

    https://vhzqaplmfcs.lthed.com/api/DocumentUpload

.. note::
    The browse UI and upload endpoint use different hosts.  Metadata fields can
    be sent as multipart form fields (default), query parameters, or both.

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
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from urllib.parse import urlencode, urlparse

import requests
from requests.auth import HTTPBasicAuth

# ---------------------------------------------------------------------------
# Re-use the canonical sanitiser from the export script to avoid duplicating
# the regex.  This is the single source of truth for project-name sanitisation
# across the whole tool-chain.
# ---------------------------------------------------------------------------
try:
    from scripts.export_tests_to_text import _sanitize_project_name  # noqa: PLC2701
except ModuleNotFoundError:  # direct script execution fallback
    from export_tests_to_text import _sanitize_project_name  # type: ignore  # pragma: no cover

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://vhzqaplmfcs.lthed.com"
DEFAULT_UPLOAD_PATH = "/api/DocumentUpload"
DEFAULT_HTTP_METHOD = "POST"
DEFAULT_FIELD_NAME = "file"
DEFAULT_FOLDER = "UnitTestCaseAgent"
DEFAULT_PSNO = "20342252"
DEFAULT_DELETE_RIGHT = "False"
DEFAULT_PARAMS_AS = "form"
DEFAULT_BROWSE_ORIGIN = "https://vhziemqsqa.lthed.com:86"
DEFAULT_FIELD_FOLDER = "folder"
DEFAULT_FIELD_TABLEID = "tableid"
DEFAULT_FIELD_LINKEDTO = "linkedto"
DEFAULT_FIELD_PSNO = "psno"
DEFAULT_FIELD_DELETERIGHT = "deleteright"
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
    params_as: str = DEFAULT_PARAMS_AS
    browse_origin: str = DEFAULT_BROWSE_ORIGIN
    field_folder: str = DEFAULT_FIELD_FOLDER
    field_tableid: str = DEFAULT_FIELD_TABLEID
    field_linkedto: str = DEFAULT_FIELD_LINKEDTO
    field_psno: str = DEFAULT_FIELD_PSNO
    field_deleteright: str = DEFAULT_FIELD_DELETERIGHT
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
        ``FCS_UPLOAD_PATH``       /api/DocumentUpload  Path component for upload requests
        ``FCS_HTTP_METHOD``       POST           HTTP verb used for uploads
        ``FCS_FIELD_NAME``        file           Multipart form-field name for the file
        ``FCS_FOLDER``            UnitTestCase…  Folder metadata value
        ``FCS_PSNO``              20342252       Project/site number
        ``FCS_DELETE_RIGHT``      False          Whether the upload grants delete rights
        ``FCS_PARAMS_AS``         form           Send metadata as form/query/both
        ``FCS_BROWSE_ORIGIN``     https://vhzi…  Sent as Origin and Referer headers
        ``FCS_FIELD_FOLDER``      folder         Metadata field name for folder
        ``FCS_FIELD_TABLEID``     tableid        Metadata field name for tableid
        ``FCS_FIELD_LINKEDTO``    linkedto       Metadata field name for linkedto
        ``FCS_FIELD_PSNO``        psno           Metadata field name for psno
        ``FCS_FIELD_DELETERIGHT`` deleteright    Metadata field name for deleteright
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

        def _get_non_empty(key: str, default: str) -> str:
            value = env.get(key)
            return default if value in (None, "") else value

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

        params_as = _get("FCS_PARAMS_AS", DEFAULT_PARAMS_AS).strip().lower()
        if params_as not in {"form", "query", "both"}:
            print(
                f"[fcs_uploader] Invalid FCS_PARAMS_AS={params_as!r}; "
                "must be 'form', 'query', or 'both'. Falling back to 'form'.",
                file=sys.stderr,
            )
            params_as = DEFAULT_PARAMS_AS

        return cls(
            base_url=_get_non_empty("FCS_BASE_URL", DEFAULT_BASE_URL),
            upload_path=_get("FCS_UPLOAD_PATH", DEFAULT_UPLOAD_PATH),
            http_method=_get("FCS_HTTP_METHOD", DEFAULT_HTTP_METHOD),
            field_name=_get("FCS_FIELD_NAME", DEFAULT_FIELD_NAME),
            folder=_get("FCS_FOLDER", DEFAULT_FOLDER),
            psno=_get("FCS_PSNO", DEFAULT_PSNO),
            delete_right=_get("FCS_DELETE_RIGHT", DEFAULT_DELETE_RIGHT),
            params_as=params_as,
            browse_origin=_get("FCS_BROWSE_ORIGIN", DEFAULT_BROWSE_ORIGIN),
            field_folder=_get("FCS_FIELD_FOLDER", DEFAULT_FIELD_FOLDER),
            field_tableid=_get("FCS_FIELD_TABLEID", DEFAULT_FIELD_TABLEID),
            field_linkedto=_get("FCS_FIELD_LINKEDTO", DEFAULT_FIELD_LINKEDTO),
            field_psno=_get("FCS_FIELD_PSNO", DEFAULT_FIELD_PSNO),
            field_deleteright=_get("FCS_FIELD_DELETERIGHT", DEFAULT_FIELD_DELETERIGHT),
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


def get_fcs_host(base_url: str) -> str:
    """Extract the FC S host from a configured base URL."""
    parsed = urlparse(base_url)
    if parsed.hostname:
        return parsed.hostname

    parsed = urlparse(f"https://{base_url}")
    if parsed.hostname:
        return parsed.hostname

    fallback = urlparse(DEFAULT_BASE_URL).hostname
    return fallback or "vhzqaplmfcs.lthed.com"


def check_fcs_connectivity(config: FCSConfig) -> str:
    """Resolve the configured FC S host and return it on success."""
    host = get_fcs_host(config.base_url)
    socket.gethostbyname(host)
    return host


def _is_dns_resolution_error(exc: requests.exceptions.ConnectionError) -> bool:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, socket.gaierror):
            return True
        current = current.__cause__ or current.__context__
    error_text = str(exc)
    return "NameResolutionError" in error_text or "Failed to resolve" in error_text


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
            extra_params: Optional dict of additional metadata fields.

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

        metadata = self._build_metadata(tableid_upper, linkedto, extra_params)
        url, data = self._build_request_target(metadata)
        return self._upload_with_retry(local_path, url, data=data)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_metadata(self, tableid: str, linkedto: str, extra_params: dict | None) -> dict:
        cfg = self._config
        metadata = {
            cfg.field_folder: cfg.folder,
            cfg.field_tableid: tableid,
            cfg.field_linkedto: linkedto,
            cfg.field_psno: cfg.psno,
            cfg.field_deleteright: cfg.delete_right,
        }
        if extra_params:
            metadata.update(extra_params)
        return metadata

    def _build_url(self, query_params: dict | None = None) -> str:
        cfg = self._config
        base = cfg.base_url.rstrip("/")
        path = cfg.upload_path
        url = f"{base}{path}"
        if query_params:
            url = f"{url}?{urlencode(query_params)}"
        return url

    def _build_request_target(self, metadata: dict) -> tuple[str, dict | None]:
        params_as = self._config.params_as
        if params_as == "query":
            return self._build_url(query_params=metadata), None
        if params_as == "both":
            return self._build_url(query_params=metadata), metadata
        # "form" is the default metadata mode.
        return self._build_url(), metadata

    def _build_auth(self):
        cfg = self._config
        if cfg.username and cfg.password:
            return HTTPBasicAuth(cfg.username, cfg.password)
        return None

    def _build_headers(self) -> dict:
        cfg = self._config
        origin = cfg.browse_origin.rstrip("/")
        headers: dict = {
            "Origin": origin,
            "Referer": f"{origin}/",
        }
        if cfg.token and not (cfg.username and cfg.password):
            headers["Authorization"] = "Bearer " + cfg.token
        return headers

    def _upload_with_retry(self, local_path: Path, url: str, *, data: dict | None = None) -> dict:
        cfg = self._config
        method = cfg.http_method.upper()
        auth = self._build_auth()
        headers = self._build_headers()
        last_exc: Exception | None = None
        last_status: int | None = None
        last_body: str = ""

        for attempt in range(cfg.max_retries):
            if attempt > 0:
                # Exponential back-off: 1s, 2s, 4s … on successive retries
                time.sleep(2 ** (attempt - 1))

            try:
                with local_path.open("rb") as fh:
                    response = requests.request(
                        method,
                        url,
                        files={cfg.field_name: (local_path.name, fh)},
                        data=data,
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
            if (
                isinstance(last_exc, requests.exceptions.ConnectionError)
                and _is_dns_resolution_error(last_exc)
            ):
                host = get_fcs_host(url)
                raise FCSUploadError(
                    f"DNS resolution failed for {host}: {last_exc}",
                    status_code=None,
                    body="",
                )
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
            "Defaults target the observed production upload endpoint:\n"
            "https://vhzqaplmfcs.lthed.com/api/DocumentUpload"
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
        help="Additional metadata key-value pairs (routing depends on FCS_PARAMS_AS).",
    )
    up.add_argument(
        "--probe",
        action="store_true",
        help="Print the resolved request URL/metadata and exit without uploading.",
    )

    sub.add_parser(
        "check-connectivity",
        help="Resolve the configured FC S host and exit without uploading.",
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
    metadata = client._build_metadata(args.tableid.upper(), linkedto, extra)
    url, data = client._build_request_target(metadata)
    if args.probe:
        print(f"Probe: method={config.http_method.upper()} url={url}")
        print(f"Probe: metadata_keys={list(metadata.keys())}")
        query_enabled = "?" in url
        form_enabled = data is not None
        print(
            "Probe: metadata_target="
            f"{config.params_as} (query={query_enabled}, form={form_enabled})"
        )
        return
    result = client.upload_file(
        local_path=args.local_path,
        tableid=args.tableid,
        linkedto=linkedto,
        extra_params=extra,
    )
    print(f"Uploaded successfully → {result['url']}")
    print(f"HTTP {result['status_code']}: {result['body']}")


def _run_check_connectivity() -> None:
    config = FCSConfig.from_env()
    host = get_fcs_host(config.base_url)
    try:
        check_fcs_connectivity(config)
    except socket.gaierror as exc:
        print(
            f"[fcs] FC S connectivity check failed — could not resolve host '{host}': {exc}",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    print(f"[fcs] FC S connectivity check succeeded — host '{host}' resolved.")


def main(argv=None) -> None:
    args = _parse_args(argv)
    if args.command == "upload":
        _run_upload(args)
    elif args.command == "check-connectivity":
        _run_check_connectivity()


if __name__ == "__main__":
    main()
