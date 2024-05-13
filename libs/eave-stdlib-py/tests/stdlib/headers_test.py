from eave.stdlib import headers

from .base import StdlibBaseTestCase


class HeadersTest(StdlibBaseTestCase):
    """
    Because these headers are referenced by name outside of this codebase, it's important that they don't change without careful consideration. These tests will catch any changes to the header names.
    """

    async def test_header_values(self):
        assert headers.EAVE_ACCOUNT_ID_HEADER == "eave-account-id"
        assert headers.EAVE_ORIGIN_HEADER == "eave-origin"
        assert headers.EAVE_REQUEST_ID_HEADER == "eave-request-id"
        assert headers.EAVE_CRON_DISPATCH_KEY_HEADER == "eave-cron-dispatch-key"
        assert headers.EAVE_DEV_BYPASS_HEADER == "X-Google-EAVEDEV"
        assert headers.EAVE_LB_HEADER == "eave-lb"
        assert headers.GCP_CLOUD_TRACE_CONTEXT == "X-Cloud-Trace-Context"
        assert headers.GCP_GAE_REQUEST_LOG_ID == "X-Appengine-Request-Log-Id"
        assert headers.GCP_GAE_TASK_EXECUTION_COUNT == "X-AppEngine-TaskExecutionCount"

        assert headers.MIME_TYPE_JSON == "application/json"
        assert headers.MIME_TYPE_TEXT == "text/plain"
        assert headers.ENCODING_GZIP == "gzip"
