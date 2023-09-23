import { TestContextBase, TestUtil, mockSigning } from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import anyTest, { TestFn } from "ava";
import sinon from "sinon";
import request from "supertest";
import { app } from "../src/app.js";
import ConfluenceClient from "../src/confluence-client.js";

interface TestContext extends TestContextBase {
  sandbox: sinon.SinonSandbox;
  confluenceClient: sinon.SinonStubbedInstance<ConfluenceClient>;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const util = new TestUtil();
  mockSigning({ sandbox });

  const mockConfluenceClient = new ConfluenceClient(<any>null); // client doesn't matter
  const confluenceClient = sandbox.stub(mockConfluenceClient);
  sandbox.stub(ConfluenceClient, "getAuthedConfluenceClient").returns(Promise.resolve(confluenceClient));

  t.context = {
    sandbox,
    confluenceClient,
    u: util,
  };
});

test.afterEach((t) => {
  t.context.sandbox.restore();
});

test("createContent", async (t) => {
  const response = await request(app)
    .post("/confluence/api/content/create")
    .set({
      "eave-team-id": t.context.u.anystr("team id"),
      "eave-origin": "eave_www",
      "eave-signature": "xxx",
    })
    .send({
      confluence_destination: {
        space_key: t.context.u.anystr("space_key"),
      },
      document: {
        title: t.context.u.anystr("doc title"),
        content: t.context.u.anystr("doc content"),
      },
    });

  t.assert(t.context.confluenceClient.getSpaceByKey.called);
  t.assert(response !== null);
});
