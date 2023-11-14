import {
  TestContextBase,
  TestUtil,
} from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import anyTest, { TestFn } from "ava";
import sinon from "sinon";
import request from "supertest";
import { app } from "../src/app.js";

interface TestContext extends TestContextBase {
  sandbox: sinon.SinonSandbox;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const util = new TestUtil();

  t.context = {
    sandbox,
    u: util,
  };
});

test.afterEach((t) => {
  t.context.sandbox.restore();
});

test("status endpoint is alive", async (t) => {
  const response = await request(app).get("/github/status");
  t.assert(response.ok);
  t.is(response.body.status, "OK");
});
