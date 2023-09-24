import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { TestContextBase, TestUtil, makeRequest, mockSigning } from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import anyTest, { TestFn } from "ava";
import sinon from "sinon";
import { app } from "../src/app.js";

interface TestContext extends TestContextBase {
  sandbox: sinon.SinonSandbox;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const util = new TestUtil();
  mockSigning({ sandbox });

  t.context = {
    sandbox,
    u: util,
  };
});

test.afterEach((t) => {
  t.context.sandbox.restore();
});

// TODO: Mocking for external API requests
test("endpoint is alive", async (t) => {
  const response = await makeRequest({
    app,
    audience: EaveApp.eave_github_app,
    path: "/github/api/subscribe",
    teamId: t.context.u.anystr("team id"),
    // input: {
    // } satisfies CreateGithubResourceSubscriptionRequestBody,
  });

  t.not(response.status, 404);
});
