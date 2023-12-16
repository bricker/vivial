import {
  ConfluencePage,
  ConfluenceSpace,
  ConfluenceSpaceStatus,
  ConfluenceSpaceType,
} from "@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js";
import { CreateContentRequestBody } from "@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import {
  TestContextBase,
  TestUtil,
  makeRequest,
  mockSigning,
} from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import anyTest, { TestFn } from "ava";
import { constants as httpConstants } from "node:http2";
import sinon from "sinon";
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
  sandbox
    .stub(ConfluenceClient, "getAuthedConfluenceClient")
    .returns(Promise.resolve(confluenceClient));

  t.context = {
    sandbox,
    confluenceClient,
    u: util,
  };
});

test.afterEach((t) => {
  t.context.sandbox.restore();
});

// TODO: There are so many API calls in this endpoint that need to be mocked
test.serial.skip("createContent", async (t) => {
  t.context.confluenceClient.getSpaceByKey.returns(
    Promise.resolve({
      id: t.context.u.anystr(),
      key: t.context.u.anystr(),
      name: t.context.u.anystr(),
      type: ConfluenceSpaceType.global,
      status: ConfluenceSpaceStatus.current,
      homepage: {
        id: t.context.u.anystr(),
        status: "current",
        title: t.context.u.anystr(),
      } satisfies ConfluencePage,
    } satisfies ConfluenceSpace),
  );

  const response = await makeRequest({
    app,
    path: "/confluence/api/content/create",
    method: "post",
    teamId: t.context.u.anystr("team id"),
    audience: EaveApp.eave_confluence_app,
    origin: EaveApp.eave_www,
    input: {
      confluence_destination: {
        space_key: t.context.u.anystr("space_key"),
      },
      document: {
        title: t.context.u.anystr("doc title"),
        content: t.context.u.anystr("doc content"),
        parent: null,
      },
    } satisfies CreateContentRequestBody,
  });

  t.assert(t.context.confluenceClient.getSpaceByKey.called);
  t.assert(response.statusCode === httpConstants.HTTP_STATUS_OK);
});

test.serial("returns 400 if no space is found", async (t) => {
  t.context.confluenceClient.getSpaceByKey.returns(Promise.resolve(null));

  const response = await makeRequest({
    app,
    path: "/confluence/api/content/create",
    method: "post",
    teamId: t.context.u.anystr("team id"),
    audience: EaveApp.eave_confluence_app,
    origin: EaveApp.eave_www,
    input: {
      confluence_destination: {
        space_key: t.context.u.anystr("space_key"),
      },
      document: {
        title: t.context.u.anystr("doc title"),
        content: t.context.u.anystr("doc content"),
        parent: null,
      },
    } satisfies CreateContentRequestBody,
  });

  t.assert(t.context.confluenceClient.getSpaceByKey.called);
  t.assert(response.statusCode === httpConstants.HTTP_STATUS_BAD_REQUEST);
});

test.serial("returns 400 if space.homepage is empty", async (t) => {
  t.context.confluenceClient.getSpaceByKey.returns(
    Promise.resolve({
      id: t.context.u.anystr(),
      key: t.context.u.anystr(),
      name: t.context.u.anystr(),
      type: ConfluenceSpaceType.global,
      status: ConfluenceSpaceStatus.current,
      homepage: undefined,
    } satisfies ConfluenceSpace),
  );

  const response = await makeRequest({
    app,
    path: "/confluence/api/content/create",
    method: "post",
    teamId: t.context.u.anystr("team id"),
    audience: EaveApp.eave_confluence_app,
    origin: EaveApp.eave_www,
    input: {
      confluence_destination: {
        space_key: t.context.u.anystr("space_key"),
      },
      document: {
        title: t.context.u.anystr("doc title"),
        content: t.context.u.anystr("doc content"),
        parent: null,
      },
    } satisfies CreateContentRequestBody,
  });

  t.assert(t.context.confluenceClient.getSpaceByKey.called);
  t.assert(response.statusCode === httpConstants.HTTP_STATUS_BAD_REQUEST);
});
