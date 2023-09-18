import anyTest, { TestFn } from 'ava';
import { TestContextBase, TestUtil, makeRequest, mockSigning } from '@eave-fyi/eave-stdlib-ts/src/test-util.js';
import sinon from "sinon";
import { app } from "../src/app.js";
import { RunApiDocumentationTaskRequestBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js';

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
    path: "/_/github/run-api-documentation",
    // input: {} satisfies RunApiDocumentationTaskRequestBody
  });

  t.not(response.status, 404);
});
