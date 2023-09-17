import anyTest, { TestFn } from "ava";
import request from "supertest";
import { TestContextBase, TestUtil } from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import { app } from "../src/app.js";

interface TestContext extends TestContextBase {}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  t.context = {
    u: new TestUtil(),
  };
});

test.afterEach((t) => {});

test("status", async (t) => {
  const response = await request(app).get("/confluence/status");
  t.assert(response.status === 200);
  t.assert(response.body["status"] === "OK");
});
