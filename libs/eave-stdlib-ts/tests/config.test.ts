import anyTest, { TestFn } from "ava";
import { TestContextBase, TestUtil } from "../src/test-util.js";
import { EaveEnvironment, sharedConfig } from "../src/config.js";
import { EaveApp } from "../src/eave-origins.js";

const test = anyTest as TestFn<TestContextBase>;

test.beforeEach((t) => {
  t.context = {
    u: new TestUtil(),
  };
});

test("eaveInternalServiceBase for non-dev", (t) => {
  const project = t.context.u.anystr("gcp");
  process.env["GOOGLE_CLOUD_PROJECT"] = project;
  process.env["EAVE_ENV"] = EaveEnvironment.production;
  t.is(sharedConfig.eaveInternalServiceBase(EaveApp.eave_api), `https://api-dot-${project}.uc.r.appspot.com`)
  t.is(sharedConfig.eaveInternalServiceBase(EaveApp.eave_www), `https://www-dot-${project}.uc.r.appspot.com`)
  t.is(sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app), `https://github-dot-${project}.uc.r.appspot.com`)
});
