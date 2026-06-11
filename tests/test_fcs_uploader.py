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
from unittest.mock import MagicMock, patch

from scripts.fcs_uploader import (
    DEFAULT_BASE_URL,
    DEFAULT_BROWSE_ORIGIN,
    DEFAULT_DELETE_RIGHT,
    DEFAULT_FIELD_NAME,
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
        self.assertEqual(cfg.field_folder, "folder")
        self.assertEqual(cfg.field_tableid, "tableid")
        self.assertEqual(cfg.field_linkedto, "linkedto")
        self.assertEqual(cfg.field_psno, "psno")
        self.assertEqual(cfg.field_deleteright, "deleteright")
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
        self.assertEqual(cfg.params_as, DEFAULT_PARAMS_AS)
        self.assertTrue(cfg.verify_ssl)

    def test_fromEnv_overridesBaseUrl(self):
        cfg = FCSConfig.from_env(env={"FCS_BASE_URL": "http://localhost:8080"})
        self.assertEqual(cfg.base_url, "http://localhost:8080")

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

    def test_fromEnv_invalidParamsAs_fallsBackToDefaultAndWarns(self):
        with patch("sys.stderr", new_callable=StringIO) as stderr:
            cfg = FCSConfig.from_env(env={"FCS_PARAMS_AS": "invalid"})
        self.assertEqual(cfg.params_as, DEFAULT_PARAMS_AS)
        self.assertIn("falling back", stderr.getvalue())

    def test_fromEnv_overridesBrowseOrigin(self):
        cfg = FCSConfig.from_env(env={"FCS_BROWSE_ORIGIN": "https://example.test"})
        self.assertEqual(cfg.browse_origin, "https://example.test")

    def test_fromEnv_overridesMetadataFieldNames(self):
        cfg = FCSConfig.from_env(
            env={
                "FCS_FIELD_FOLDER": "FolderName",
                "FCS_FIELD_TABLEID": "TableId",
                "FCS_FIELD_LINKEDTO": "LinkedTo",
                "FCS_FIELD_PSNO": "PsNo",
                "FCS_FIELD_DELETERIGHT": "DeleteRight",
            }
        )
        self.assertEqual(cfg.field_folder, "FolderName")
        self.assertEqual(cfg.field_tableid, "TableId")
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
# FCSClient – request resolution
# ---------------------------------------------------------------------------


class TestFCSClientResolveRequest(unittest.TestCase):
    def _make_client(self, **overrides):
        cfg = FCSConfig(**overrides)
        return FCSClient(cfg)

    def test_resolveRequest_formMode_putsMetadataIntoFormFields(self):
        client = self._make_client()
        url, query_params, form_fields = client._resolve_request("INPUT", "Proj_2026-06-10", None)
        self.assertEqual(url, f"{DEFAULT_BASE_URL}{DEFAULT_UPLOAD_PATH}")
        self.assertEqual(query_params, {})
        self.assertEqual(
            form_fields,
            {
                "folder": "UnitTestCaseAgent",
                "tableid": "INPUT",
                "linkedto": "Proj_2026-06-10",
                "psno": "20342252",
                "deleteright": "False",
            },
        )

    def test_resolveRequest_queryMode_putsMetadataIntoQueryParams(self):
        client = self._make_client(params_as="query")
        url, query_params, form_fields = client._resolve_request("OUTPUT", "Proj_2026-06-10", {"foo": "bar"})
        self.assertEqual(url, f"{DEFAULT_BASE_URL}{DEFAULT_UPLOAD_PATH}")
        self.assertEqual(form_fields, {})
        self.assertEqual(query_params["folder"], "UnitTestCaseAgent")
        self.assertEqual(query_params["tableid"], "OUTPUT")
        self.assertEqual(query_params["linkedto"], "Proj_2026-06-10")
        self.assertEqual(query_params["foo"], "bar")

    def test_resolveRequest_bothMode_putsMetadataIntoQueryAndForm(self):
        client = self._make_client(params_as="both")
        _, query_params, form_fields = client._resolve_request("INPUT", "X_2026-06-10", {"foo": "bar"})
        self.assertEqual(query_params["tableid"], "INPUT")
        self.assertEqual(form_fields["tableid"], "INPUT")
        self.assertEqual(query_params["foo"], "bar")
        self.assertNotIn("foo", form_fields)

    def test_resolveRequest_customFieldNames_reflected(self):
        client = self._make_client(
            field_folder="FolderName",
            field_tableid="TableId",
            field_linkedto="LinkedTo",
            field_psno="PsNo",
            field_deleteright="DeleteRight",
        )
        _, query_params, form_fields = client._resolve_request("INPUT", "X", None)
        self.assertEqual(query_params, {})
        self.assertEqual(form_fields["FolderName"], "UnitTestCaseAgent")
        self.assertEqual(form_fields["TableId"], "INPUT")
        self.assertEqual(form_fields["LinkedTo"], "X")
        self.assertEqual(form_fields["PsNo"], "20342252")
        self.assertEqual(form_fields["DeleteRight"], "False")


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
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertIn("mytoken", headers["Authorization"])
        self.assertEqual(headers["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(headers["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")

    def test_buildHeaders_basicAuthPreferred_overToken(self):
        cfg = FCSConfig(username="u", password="p", token="tok")
        client = FCSClient(cfg)
        headers = client._build_headers()
        self.assertNotIn("Authorization", headers)
        self.assertEqual(headers["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(headers["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")

    def test_buildHeaders_noToken_includesOriginAndReferer(self):
        client = FCSClient(FCSConfig())
        self.assertEqual(
            client._build_headers(),
            {
                "Origin": DEFAULT_BROWSE_ORIGIN,
                "Referer": f"{DEFAULT_BROWSE_ORIGIN}/",
            },
        )


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
        self.assertIsNone(kwargs["params"])
        self.assertEqual(
            kwargs["data"],
            {
                "folder": "UnitTestCaseAgent",
                "tableid": "INPUT",
                "linkedto": "Proj_2026-06-10",
                "psno": "20342252",
                "deleteright": "False",
            },
        )
        self.assertEqual(kwargs["headers"]["Origin"], DEFAULT_BROWSE_ORIGIN)
        self.assertEqual(kwargs["headers"]["Referer"], f"{DEFAULT_BROWSE_ORIGIN}/")

    @patch("scripts.fcs_uploader.requests.request")
    @patch("scripts.fcs_uploader.time.sleep")
    def test_uploadWithRetry_queryMode_passesMetadataViaParams(self, mock_sleep, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"result": "ok"}
        mock_request.return_value = mock_response

        client = FCSClient(FCSConfig(params_as="query"))
        f = self._make_tmp_file()
        result = client.upload_file(f, "OUTPUT", "Proj_2026-06-10", extra_params={"foo": "bar"})
        self.assertIn("foo=bar", result["url"])
        _, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["tableid"], "OUTPUT")
        self.assertEqual(kwargs["params"]["foo"], "bar")
        self.assertIsNone(kwargs["data"])
        mock_sleep.assert_not_called()

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

    def test_parseArgs_probeFlag_setsTrue(self):
        args = _parse_args(["upload", "/tmp/x.txt", "INPUT", "X", "--probe"])
        self.assertTrue(args.probe)

    def test_parseArgs_invalidTableId_fails(self):
        with self.assertRaises(SystemExit):
            _parse_args(["upload", "/tmp/x.txt", "INVALID"])

    def test_parseArgs_lowercaseTableId_accepted(self):
        args = _parse_args(["upload", "/tmp/x.txt", "input", "X"])
        self.assertEqual(args.tableid, "input")


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
        self.assertEqual(kwargs["linkedto"], "TestProject_2026-06-10")
        self.assertEqual(kwargs["tableid"], "OUTPUT")

    @patch("builtins.print")
    @patch("scripts.fcs_uploader.FCSClient.probe_request")
    @patch("scripts.fcs_uploader.FCSConfig.from_env")
    def test_main_probe_printsResolvedRequestWithoutUpload(
        self,
        mock_from_env,
        mock_probe,
        mock_print,
    ):
        mock_from_env.return_value = FCSConfig()
        mock_probe.return_value = {
            "method": "POST",
            "url": "https://example.test/api/DocumentUpload",
            "query_params": {},
            "form_fields": {"tableid": "INPUT"},
            "headers": {"Origin": DEFAULT_BROWSE_ORIGIN},
            "file_field": "file",
            "local_path": "/tmp/x.txt",
        }

        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            tmp.write(b"data")
            tmp.flush()
            main(["upload", tmp.name, "INPUT", "MyProj_2026-06-10", "--probe"])

        mock_probe.assert_called_once()
        printed = mock_print.call_args[0][0]
        self.assertIn('"method": "POST"', printed)
        self.assertIn('"tableid": "INPUT"', printed)

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


if __name__ == "__main__":
    unittest.main()
