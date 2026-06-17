"""Unit tests for scripts/fcs_uploader.py.

Covers:
- FCSConfig dataclass and from_env() class method
- build_linked_to() helper
- FCSClient URL building, auth, and retry logic
- FCSUploadError exception
- CLI argument parsing
"""

SOURCE_STORY_FILE = None  # These tests are not generated from a user-story Excel file

import tempfile
import unittest
import unittest.mock
from io import StringIO
from pathlib import Path
import socket
from unittest.mock import MagicMock, patch

from scripts.fcs_uploader import (
    DEFAULT_BASE_URL,
    DEFAULT_BROWSE_ORIGIN,
    DEFAULT_DELETE_RIGHT,
    DEFAULT_FIELD_NAME,
    DEFAULT_FIELD_DELETERIGHT,
    DEFAULT_FIELD_FOLDER,
    DEFAULT_FIELD_LINKEDTO,
    DEFAULT_FIELD_PSNO,
    DEFAULT_FIELD_TABLEID,
    DEFAULT_FOLDER,
    DEFAULT_HTTP_METHOD,
    DEFAULT_MAX_RETRIES,
    DEFAULT_PARAMS_AS,
    DEFAULT_PSNO,
    DEFAULT_TIMEOUT,
    DEFAULT_UPLOAD_PATH,
    VALID_TABLE_IDS,
    FCSClient,
    FCSConfig,
    FCSUploadError,
    build_linked_to,
    get_fcs_host,
    main,
    _parse_args,
)


# ---------------------------------------------------------------------------
# FCSConfig tests
# ---------------------------------------------------------------------------


class TestFCSConfigDefaults(unittest.TestCase):
    def test_defaults_matchExpectedValues(self):
        cfg = FCSConfig()
        self.assertEqual(cfg.base_url, DEFAULT_BASE_URL)
        self.assertEqual(cfg.upload_path, DEFAULT_UPLOAD_PATH)
        self.assertEqual(cfg.http_method, DEFAULT_HTTP_METHOD)
        self.assertEqual(cfg.field_name, DEFAULT_FIELD_NAME)
        self.assertEqual(cfg.folder, DEFAULT_FOLDER)
        self.assertEqual(cfg.psno, DEFAULT_PSNO)
        self.assertEqual(cfg.delete_right, DEFAULT_DELETE_RIGHT)
        self.assertEqual(cfg.params_as, DEFAULT_PARAMS_AS)
        self.assertEqual(cfg.browse_origin, DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(cfg.field_folder, DEFAULT_FIELD_FOLDER)
        self.assertEqual(cfg.field_tableid, DEFAULT_FIELD_TABLEID)
        self.assertEqual(cfg.field_linkedto, DEFAULT_FIELD_LINKEDTO)
        self.assertEqual(cfg.field_psno, DEFAULT_FIELD_PSNO)
        self.assertEqual(cfg.field_deleteright, DEFAULT_FIELD_DELETERIGHT)
        self.assertIsNone(cfg.username)
        self.assertIsNone(cfg.password)
        self.assertIsNone(cfg.token)
        self.assertTrue(cfg.verify_ssl)
        self.assertEqual(cfg.timeout, DEFAULT_TIMEOUT)
        self.assertEqual(cfg.max_retries, DEFAULT_MAX_RETRIES)


class TestFCSConfigFromEnv(unittest.TestCase):
    def test_fromEnv_emptyEnv_returnsAllDefaults(self):
        cfg = FCSConfig.from_env(env={})
        self.assertEqual(cfg.base_url, DEFAULT_BASE_URL)
        self.assertEqual(cfg.upload_path, DEFAULT_UPLOAD_PATH)
        self.assertEqual(cfg.psno, DEFAULT_PSNO)
        self.assertTrue(cfg.verify_ssl)

    def test_fromEnv_overridesBaseUrl(self):
        cfg = FCSConfig.from_env(env={"FCS_BASE_URL": "http://localhost:8080"})
        self.assertEqual(cfg.base_url, "http://localhost:8080")

    def test_fromEnv_emptyBaseUrl_fallsBackToDefault(self):
        cfg = FCSConfig.from_env(env={"FCS_BASE_URL": ""})
        self.assertEqual(cfg.base_url, DEFAULT_BASE_URL)

    def test_fromEnv_overridesUploadPath(self):
        cfg = FCSConfig.from_env(env={"FCS_UPLOAD_PATH": "/api/upload"})
        self.assertEqual(cfg.upload_path, "/api/upload")

    def test_fromEnv_overridesHttpMethod(self):
        cfg = FCSConfig.from_env(env={"FCS_HTTP_METHOD": "PUT"})
        self.assertEqual(cfg.http_method, "PUT")

    def test_fromEnv_overridesFieldName(self):
        cfg = FCSConfig.from_env(env={"FCS_FIELD_NAME": "document"})
        self.assertEqual(cfg.field_name, "document")

    def test_fromEnv_overridesPsno(self):
        cfg = FCSConfig.from_env(env={"FCS_PSNO": "99999"})
        self.assertEqual(cfg.psno, "99999")

    def test_fromEnv_overridesDeleteRight(self):
        cfg = FCSConfig.from_env(env={"FCS_DELETE_RIGHT": "True"})
        self.assertEqual(cfg.delete_right, "True")

    def test_fromEnv_overridesParamsAs(self):
        cfg = FCSConfig.from_env(env={"FCS_PARAMS_AS": "both"})
        self.assertEqual(cfg.params_as, "both")

    def test_fromEnv_overridesParamsAsQuery(self):
        cfg = FCSConfig.from_env(env={"FCS_PARAMS_AS": "query"})
        self.assertEqual(cfg.params_as, "query")

    def test_fromEnv_paramsAs_normalizesCase(self):
        cfg = FCSConfig.from_env(env={"FCS_PARAMS_AS": "  BoTh  "})
        self.assertEqual(cfg.params_as, "both")

    def test_fromEnv_invalidParamsAs_fallsBackToFormWithWarning(self):
        with patch("sys.stderr", new_callable=StringIO) as stderr:
            cfg = FCSConfig.from_env(env={"FCS_PARAMS_AS": "invalid"})
        self.assertEqual(cfg.params_as, "form")
        self.assertEqual(
            stderr.getvalue().strip(),
            (
                "[fcs_uploader] Invalid FCS_PARAMS_AS='invalid'; must be 'form', "
                "'query', or 'both'. Falling back to 'form'."
            ),
        )

    def test_fromEnv_overridesBrowseOrigin(self):
        cfg = FCSConfig.from_env(env={"FCS_BROWSE_ORIGIN": "https://example.com:86"})
        self.assertEqual(cfg.browse_origin, "https://example.com:86")

    def test_fromEnv_overridesMetadataFieldNames(self):
        cfg = FCSConfig.from_env(
            env={
                "FCS_FIELD_FOLDER": "Folder",
                "FCS_FIELD_TABLEID": "TableID",
                "FCS_FIELD_LINKEDTO": "LinkedTo",
                "FCS_FIELD_PSNO": "PsNo",
                "FCS_FIELD_DELETERIGHT": "DeleteRight",
            }
        )
        self.assertEqual(cfg.field_folder, "Folder")
        self.assertEqual(cfg.field_tableid, "TableID")
        self.assertEqual(cfg.field_linkedto, "LinkedTo")
        self.assertEqual(cfg.field_psno, "PsNo")
        self.assertEqual(cfg.field_deleteright, "DeleteRight")

    def test_fromEnv_setsUsername(self):
        cfg = FCSConfig.from_env(env={"FCS_USERNAME": "alice"})
        self.assertEqual(cfg.username, "alice")

    def test_fromEnv_setsToken(self):
        cfg = FCSConfig.from_env(env={"FCS_TOKEN": "tok123"})
        self.assertEqual(cfg.token, "tok123")

    def test_fromEnv_emptyUsername_isNone(self):
        cfg = FCSConfig.from_env(env={"FCS_USERNAME": ""})
        self.assertIsNone(cfg.username)

    def test_fromEnv_verifySslFalse_disablesVerification(self):
        for falsy in ("false", "False", "0", "no"):
            with self.subTest(value=falsy):
                cfg = FCSConfig.from_env(env={"FCS_VERIFY_SSL": falsy})
                self.assertFalse(cfg.verify_ssl)

    def test_fromEnv_verifySslTrue_enablesVerification(self):
        cfg = FCSConfig.from_env(env={"FCS_VERIFY_SSL": "true"})
        self.assertTrue(cfg.verify_ssl)

    def test_fromEnv_invalidTimeout_fallsBackToDefault(self):
        cfg = FCSConfig.from_env(env={"FCS_TIMEOUT": "notanumber"})
        self.assertEqual(cfg.timeout, DEFAULT_TIMEOUT)

    def test_fromEnv_validTimeout_parsesCorrectly(self):
        cfg = FCSConfig.from_env(env={"FCS_TIMEOUT": "120"})
        self.assertEqual(cfg.timeout, 120)

    def test_fromEnv_invalidMaxRetries_fallsBackToDefault(self):
        cfg = FCSConfig.from_env(env={"FCS_MAX_RETRIES": "bad"})
        self.assertEqual(cfg.max_retries, DEFAULT_MAX_RETRIES)

    def test_fromEnv_validMaxRetries_parsesCorrectly(self):
        cfg = FCSConfig.from_env(env={"FCS_MAX_RETRIES": "5"})
        self.assertEqual(cfg.max_retries, 5)

    def test_fromEnv_noEnv_readsFromOsEnviron(self):
        """Passing env=None should fall back to os.environ."""
        with patch.dict("os.environ", {"FCS_PSNO": "12345"}, clear=False):
            cfg = FCSConfig.from_env(env=None)
        self.assertEqual(cfg.psno, "12345")


# ---------------------------------------------------------------------------
# build_linked_to tests
# ---------------------------------------------------------------------------


class TestBuildLinkedTo(unittest.TestCase):
    def test_buildLinkedTo_simpleProjectName_sanitisesAndAppendDate(self):
        result = build_linked_to("My Project", "2026-06-10")
        self.assertEqual(result, "MyProject_2026-06-10")

    def test_buildLinkedTo_camelCaseProjectName_preservesCase(self):
        result = build_linked_to("Workforce Management by MX Techies", "2026-06-04")
        self.assertEqual(result, "WorkforceManagementByMXTechies_2026-06-04")

    def test_buildLinkedTo_noDateStamp_usesTodayUtc(self):
        with patch("scripts.fcs_uploader.datetime") as mock_dt:
            mock_dt.datetime.now.return_value.strftime.return_value = "2026-06-10"
            mock_dt.timezone.utc = unittest.mock.sentinel.utc
            result = build_linked_to("TestProject", None)
        self.assertTrue(result.startswith("TestProject_"))

    def test_buildLinkedTo_specialCharsInName_replacedWithUnderscore(self):
        result = build_linked_to("My/Project: Test!", "2026-01-01")
        self.assertNotIn("/", result)
        self.assertNotIn(":", result)
        self.assertNotIn("!", result)

    def test_buildLinkedTo_returnsExpectedFormat(self):
        result = build_linked_to("Alpha", "2026-06-01")
        self.assertEqual(result, "Alpha_2026-06-01")


# ---------------------------------------------------------------------------
# FCSUploadError tests
# ---------------------------------------------------------------------------


class TestFCSUploadError(unittest.TestCase):
    def test_fcsUploadError_isRuntimeError(self):
        err = FCSUploadError("something went wrong")
        self.assertIsInstance(err, RuntimeError)

    def test_fcsUploadError_storesStatusCodeAndBody(self):
        err = FCSUploadError("fail", status_code=500, body="Internal Server Error")
        self.assertEqual(err.status_code, 500)
        self.assertEqual(err.body, "Internal Server Error")

    def test_fcsUploadError_noStatusCode_isNone(self):
        err = FCSUploadError("conn error")
        self.assertIsNone(err.status_code)
        self.assertEqual(err.body, "")


# ---------------------------------------------------------------------------
# FCSClient – URL building
# ---------------------------------------------------------------------------


class TestFCSClientBuildUrl(unittest.TestCase):
    def _make_client(self, **overrides):
        cfg = FCSConfig(**overrides)
        return FCSClient(cfg)

    def test_buildMetadata_includesAllRequiredParams(self):
        client = self._make_client()
        metadata = client._build_metadata("INPUT", "Proj_2026-06-10", None)
        self.assertEqual(metadata["folder"], "UnitTestCaseAgent")
        self.assertEqual(metadata["tableid"], "INPUT")
        self.assertEqual(metadata["linkedto"], "Proj_2026-06-10")
        self.assertEqual(metadata["psno"], "20342252")
        self.assertEqual(metadata["deleteright"], "False")

    def test_buildMetadata_extraParams_added(self):
        client = self._make_client()
        metadata = client._build_metadata("OUTPUT", "Proj_2026-06-10", {"foo": "bar"})
        self.assertEqual(metadata["foo"], "bar")

    def test_buildUrl_baseUrlTrailingSlash_strippedCorrectly(self):
        client = self._make_client(base_url="http://host/", upload_path="/upload")
        url = client._build_url()
        self.assertEqual(url, "http://host/upload")

    def test_buildMetadata_customFieldNames_reflected(self):
        client = self._make_client(field_folder="Folder", field_tableid="TableID")
        metadata = client._build_metadata("INPUT", "X", None)
        self.assertIn("Folder", metadata)
        self.assertIn("TableID", metadata)

    def test_buildRequestTarget_paramsAsForm_dataOnly(self):
        client = self._make_client(params_as="form")
        metadata = client._build_metadata("INPUT", "X", None)
        url, data = client._build_request_target(metadata)
        self.assertNotIn("?", url)
        self.assertEqual(data, metadata)

    def test_buildRequestTarget_paramsAsQuery_urlOnly(self):
        client = self._make_client(params_as="query")
        metadata = client._build_metadata("INPUT", "X", None)
        url, data = client._build_request_target(metadata)
        self.assertIn("tableid=INPUT", url)
        self.assertIsNone(data)

    def test_buildRequestTarget_paramsAsBoth_urlAndData(self):
        client = self._make_client(params_as="both")
        metadata = client._build_metadata("INPUT", "X", None)
        url, data = client._build_request_target(metadata)
        self.assertIn("tableid=INPUT", url)
        self.assertEqual(data, metadata)


# ---------------------------------------------------------------------------
# FCSClient – authentication
# ---------------------------------------------------------------------------


class TestFCSClientAuth(unittest.TestCase):
    def test_buildAuth_usernameAndPassword_returnsBasicAuth(self):
        from requests.auth import HTTPBasicAuth
        cfg = FCSConfig(username="u", password="p")
        client = FCSClient(cfg)
        auth = client._build_auth()
        self.assertIsInstance(auth, HTTPBasicAuth)

    def test_buildAuth_noCredentials_returnsNone(self):
        client = FCSClient(FCSConfig())
        self.assertIsNone(client._build_auth())

    def test_buildHeaders_tokenSet_addsBearerAuth(self):
        cfg = FCSConfig(token="mytoken")
        client = FCSClient(cfg)
        headers = client._build_headers()
        self.assertEqual(headers["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(headers["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertIn("mytoken", headers["Authorization"])

    def test_buildHeaders_basicAuthPreferred_overToken(self):
        cfg = FCSConfig(username="u", password="p", token="tok")
        client = FCSClient(cfg)
        headers = client._build_headers()
        self.assertIn("Origin", headers)
        self.assertIn("Referer", headers)
        self.assertNotIn("Authorization", headers)

    def test_buildHeaders_noToken_includesOriginAndReferer(self):
        client = FCSClient(FCSConfig())
        headers = client._build_headers()
        self.assertEqual(headers["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(headers["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")


# ---------------------------------------------------------------------------
# FCSClient – upload_file validation
# ---------------------------------------------------------------------------


class TestFCSClientUploadFileValidation(unittest.TestCase):
    def setUp(self):
        self.client = FCSClient(FCSConfig())

    def test_uploadFile_invalidTableId_raisesValueError(self):
        with self.assertRaises(ValueError) as ctx:
            self.client.upload_file(Path("/tmp/x.txt"), "INVALID", "Proj_2026-06-10")
        self.assertIn("tableid", str(ctx.exception).lower())

    def test_uploadFile_fileNotFound_raisesValueError(self):
        with self.assertRaises(ValueError) as ctx:
            self.client.upload_file(Path("/nonexistent/file.txt"), "INPUT", "X")
        self.assertIn("not found", str(ctx.exception).lower())

    def test_uploadFile_tableidCaseInsensitive_accepted(self):
        """input/output in lowercase should be accepted (normalised to upper)."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            with patch.object(self.client, "_upload_with_retry", return_value={"status_code": 200, "url": "", "body": ""}):
                result = self.client.upload_file(Path(tmp.name), "input", "X")
        self.assertEqual(result["status_code"], 200)


# ---------------------------------------------------------------------------
# FCSClient – upload_with_retry (mocked requests)
# ---------------------------------------------------------------------------


class TestFCSClientRetry(unittest.TestCase):
    def _make_client(self, max_retries=2):
        cfg = FCSConfig(max_retries=max_retries)
        return FCSClient(cfg)

    def _make_tmp_file(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(b"hello")
        tmp.flush()
        tmp.close()
        return Path(tmp.name)

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_success200_returnsDict(self, mock_sleep, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"result": "ok"}
        mock_request.return_value = mock_response

        client = self._make_client()
        f = self._make_tmp_file()
        result = client.upload_file(f, "INPUT", "Proj_2026-06-10")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["body"], {"result": "ok"})
        mock_sleep.assert_not_called()
        _, kwargs = mock_request.call_args
        self.assertIsInstance(kwargs.get("data"), dict)
        self.assertEqual(kwargs["headers"]["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(kwargs["headers"]["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_paramsAsQuery_sendsNoData(self, mock_sleep, mock_request):
        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.ok = True
        ok_response.json.return_value = {}
        mock_request.return_value = ok_response

        cfg = FCSConfig(params_as="query")
        client = FCSClient(cfg)
        f = self._make_tmp_file()
        result = client.upload_file(f, "INPUT", "Proj_2026")
        self.assertEqual(result["status_code"], 200)
        call_args, kwargs = mock_request.call_args
        self.assertIsNone(kwargs.get("data"))
        self.assertIn("tableid=INPUT", call_args[1])

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_500ThenSuccess_retriesAndSucceeds(self, mock_sleep, mock_request):
        fail_response = MagicMock()
        fail_response.status_code = 503
        fail_response.ok = False
        fail_response.json.return_value = {}

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.ok = True
        ok_response.json.return_value = {"status": "ok"}

        mock_request.side_effect = [fail_response, ok_response]

        client = self._make_client(max_retries=3)
        f = self._make_tmp_file()
        result = client.upload_file(f, "OUTPUT", "Proj_2026")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(mock_request.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_all500_raisesAfterRetries(self, mock_sleep, mock_request):
        fail_response = MagicMock()
        fail_response.status_code = 500
        fail_response.ok = False
        fail_response.json.return_value = "error"
        mock_request.return_value = fail_response

        client = self._make_client(max_retries=2)
        f = self._make_tmp_file()
        with self.assertRaises(FCSUploadError):
            client.upload_file(f, "INPUT", "X")
        self.assertEqual(mock_request.call_count, 2)

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_400_doesNotRetry(self, mock_sleep, mock_request):
        fail_response = MagicMock()
        fail_response.status_code = 400
        fail_response.ok = False
        fail_response.json.return_value = "bad request"
        mock_request.return_value = fail_response

        client = self._make_client(max_retries=3)
        f = self._make_tmp_file()
        with self.assertRaises(FCSUploadError) as ctx:
            client.upload_file(f, "INPUT", "X")
        # Should only be called once – no retry on 4xx
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(ctx.exception.status_code, 400)

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_connectionError_retriesAndRaises(self, mock_sleep, mock_request):
        import requests as req_lib
        mock_request.side_effect = req_lib.exceptions.ConnectionError("refused")

        client = self._make_client(max_retries=2)
        f = self._make_tmp_file()
        with self.assertRaises(FCSUploadError):
            client.upload_file(f, "INPUT", "X")
        self.assertEqual(mock_request.call_count, 2)

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_dnsResolutionFailure_raisesClearError(self, mock_sleep, mock_request):
        import requests as req_lib

        connection_error = req_lib.exceptions.ConnectionError(
            'NameResolutionError("Failed to resolve")'
        )
        connection_error.__cause__ = socket.gaierror("Temporary failure in name resolution")
        mock_request.side_effect = connection_error

        client = self._make_client(max_retries=2)
        f = self._make_tmp_file()
        with self.assertRaises(FCSUploadError) as ctx:
            client.upload_file(f, "INPUT", "X")

        self.assertTrue(str(ctx.exception).startswith("DNS resolution failed for"))
        self.assertIn(get_fcs_host(DEFAULT_BASE_URL), str(ctx.exception))
        self.assertEqual(mock_request.call_count, 2)

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_responseBodyText_returnedWhenNoJson(self, mock_sleep, mock_request):
        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.ok = True
        ok_response.json.side_effect = ValueError("no JSON")
        ok_response.text = "OK plain text"
        mock_request.return_value = ok_response

        client = self._make_client()
        f = self._make_tmp_file()
        result = client.upload_file(f, "OUTPUT", "X")
        self.assertEqual(result["body"], "OK plain text")

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_exponentialBackoff_sleepDoubles(self, mock_sleep, mock_request):
        fail_response = MagicMock()
        fail_response.status_code = 503
        fail_response.ok = False
        fail_response.json.return_value = {}

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.ok = True
        ok_response.json.return_value = {}

        # Fail twice then succeed
        mock_request.side_effect = [fail_response, fail_response, ok_response]

        client = self._make_client(max_retries=3)
        f = self._make_tmp_file()
        client.upload_file(f, "INPUT", "X")

        # sleep called for attempt 1 (2^0=1s) and attempt 2 (2^1=2s)
        sleep_calls = [c[0][0] for c in mock_sleep.call_args_list]
        self.assertEqual(sleep_calls, [1, 2])


# ---------------------------------------------------------------------------
# FCSClient – SSL verification
# ---------------------------------------------------------------------------


class TestFCSClientSslVerification(unittest.TestCase):
    @patch("urllib3.disable_warnings")
    def test_verifySslFalse_disablesUrllib3Warnings(self, mock_disable):
        cfg = FCSConfig(verify_ssl=False)
        FCSClient(cfg)
        mock_disable.assert_called_once()

    def test_verifySslTrue_doesNotDisableWarnings(self):
        with patch("urllib3.disable_warnings") as mock_disable:
            FCSClient(FCSConfig(verify_ssl=True))
        mock_disable.assert_not_called()

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_upload_verifySslFalse_passedToRequests(self, mock_sleep, mock_request):
        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.ok = True
        ok_response.json.return_value = {}
        mock_request.return_value = ok_response

        with patch("urllib3.disable_warnings"):
            cfg = FCSConfig(verify_ssl=False)
            client = FCSClient(cfg)

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            client.upload_file(Path(tmp.name), "INPUT", "X")

        _, kwargs = mock_request.call_args
        self.assertFalse(kwargs.get("verify", True))


# ---------------------------------------------------------------------------
# CLI – argument parsing
# ---------------------------------------------------------------------------


class TestParseArgs(unittest.TestCase):
    def test_parseArgs_uploadWithLinkedto_parsesCorrectly(self):
        args = _parse_args(["upload", "/tmp/x.txt", "INPUT", "MyProj_2026-06-10"])
        self.assertEqual(args.command, "upload")
        self.assertEqual(str(args.local_path), "/tmp/x.txt")
        self.assertEqual(args.tableid, "INPUT")
        self.assertEqual(args.linkedto, "MyProj_2026-06-10")

    def test_parseArgs_uploadWithProjectName_parsesCorrectly(self):
        args = _parse_args([
            "upload", "/tmp/x.txt", "OUTPUT",
            "--project-name", "My Project", "--date-stamp", "2026-06-10",
        ])
        self.assertEqual(args.project_name, "My Project")
        self.assertEqual(args.date_stamp, "2026-06-10")

    def test_parseArgs_extraParams_parsedAsListOfStrings(self):
        args = _parse_args([
            "upload", "/tmp/x.txt", "INPUT", "X",
            "--extra-params", "foo=bar", "baz=qux",
        ])
        self.assertEqual(args.extra_params, ["foo=bar", "baz=qux"])

    def test_parseArgs_probeFlag_parsesTrue(self):
        args = _parse_args(["upload", "/tmp/x.txt", "INPUT", "X", "--probe"])
        self.assertTrue(args.probe)

    def test_parseArgs_invalidTableId_fails(self):
        with self.assertRaises(SystemExit):
            _parse_args(["upload", "/tmp/x.txt", "INVALID"])

    def test_parseArgs_lowercaseTableId_accepted(self):
        args = _parse_args(["upload", "/tmp/x.txt", "input", "X"])
        self.assertEqual(args.tableid, "input")

    def test_parseArgs_checkConnectivity_parsesCorrectly(self):
        args = _parse_args(["check-connectivity"])
        self.assertEqual(args.command, "check-connectivity")


# ---------------------------------------------------------------------------
# CLI – main() integration
# ---------------------------------------------------------------------------


class TestMain(unittest.TestCase):
    @patch("scripts.fcs_uploader.FCSClient.upload_file")
    @patch("scripts.fcs_uploader.FCSConfig.from_env")
    def test_main_uploadWithLinkedto_callsUploadFile(self, mock_from_env, mock_upload):
        mock_from_env.return_value = FCSConfig()
        mock_upload.return_value = {"status_code": 200, "url": "http://x", "body": "ok"}

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            main(["upload", tmp.name, "INPUT", "MyProj_2026-06-10"])

        mock_upload.assert_called_once()

    @patch("scripts.fcs_uploader.FCSClient.upload_file")
    @patch("scripts.fcs_uploader.FCSConfig.from_env")
    def test_main_uploadWithProjectName_buildsLinkedto(self, mock_from_env, mock_upload):
        mock_from_env.return_value = FCSConfig()
        mock_upload.return_value = {"status_code": 200, "url": "http://x", "body": "ok"}

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            main(["upload", tmp.name, "OUTPUT",
                  "--project-name", "Test Project", "--date-stamp", "2026-06-10"])

        _, kwargs = mock_upload.call_args
        # linkedto should have been built from project name
        self.assertIn("linkedto", kwargs)
        self.assertEqual(kwargs["linkedto"], "TestProject_2026-06-10")

    @patch("scripts.fcs_uploader.FCSClient.upload_file")
    @patch("scripts.fcs_uploader.FCSConfig.from_env")
    @patch("builtins.print")
    def test_main_probe_doesNotUpload(self, mock_print, mock_from_env, mock_upload):
        mock_from_env.return_value = FCSConfig()
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            main(["upload", tmp.name, "INPUT", "X", "--probe"])
        mock_upload.assert_not_called()
        self.assertTrue(mock_print.called)

    def test_main_noLinkedtoNoProjectName_exits(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            with self.assertRaises(SystemExit):
                main(["upload", tmp.name, "INPUT"])

    def test_main_invalidExtraParam_exits(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            with self.assertRaises(SystemExit):
                main(["upload", tmp.name, "INPUT", "X", "--extra-params", "noequals"])

    @patch("scripts.fcs_uploader.socket.gethostbyname", return_value="127.0.0.1")
    @patch("builtins.print")
    def test_main_checkConnectivity_success_exitsZero(self, mock_print, mock_gethostbyname):
        main(["check-connectivity"])
        mock_gethostbyname.assert_called_once_with(get_fcs_host(DEFAULT_BASE_URL))
        mock_print.assert_called_once_with(
            f"[fcs] FC S connectivity check succeeded — host '{get_fcs_host(DEFAULT_BASE_URL)}' resolved."
        )

    @patch("scripts.fcs_uploader.socket.gethostbyname", side_effect=socket.gaierror("no such host"))
    def test_main_checkConnectivity_dnsFailure_exitsTwo(self, mock_gethostbyname):
        with patch("sys.stderr", new_callable=StringIO) as stderr:
            with self.assertRaises(SystemExit) as ctx:
                main(["check-connectivity"])

        self.assertEqual(ctx.exception.code, 2)
        self.assertEqual(mock_gethostbyname.call_count, 1)
        self.assertIn("could not resolve host", stderr.getvalue())
        self.assertIn(get_fcs_host(DEFAULT_BASE_URL), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
