import anyTest, { TestFn } from "ava";
import { EaveEnvironment, sharedConfig } from "../src/config.js";
import { EaveApp } from "../src/eave-origins.js";
import { TestContextBase, TestUtil } from "../src/test-util.js";
import * as headers from "../src/headers.js";

const test = anyTest as TestFn<TestContextBase>;

test.beforeEach((t) => {
  t.context = {
    u: new TestUtil(),
  };
});

test("header values", (t) => {
  t.is(headers.EAVE_TEAM_ID_HEADER, "eave-team-id");
  t.is(headers.EAVE_ACCOUNT_ID_HEADER, "eave-account-id");
  t.is(headers.EAVE_SIGNATURE_HEADER, "eave-signature");
  t.is(headers.EAVE_SIG_TS_HEADER, "eave-sig-ts");
  t.is(headers.EAVE_ORIGIN_HEADER, "eave-origin");
  t.is(headers.EAVE_REQUEST_ID_HEADER, "eave-request-id");
  t.is(headers.EAVE_CRON_DISPATCH_KEY_HEADER, "eave-cron-dispatch-key");
  t.is(headers.EAVE_CRON_SHARED_SECRET_HEADER, "eave-cron-shared-secret");
  t.is(headers.EAVE_DEV_BYPASS_HEADER, "x-google-eavedev");
  t.is(headers.EAVE_CTX_KEY, "eave-ctx");
  t.is(headers.GCP_CLOUD_TRACE_CONTEXT, "x-cloud-trace-context");
  t.is(headers.GCP_GAE_REQUEST_LOG_ID, "x-appengine-request-log-id");
  t.is(headers.GCP_GAE_TASK_EXECUTION_COUNT, "x-appengine-taskexecutioncount");
  t.is(headers.MIME_TYPE_JSON, "application/json");
});
