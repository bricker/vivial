// import anyTest, { TestFn } from "ava";
// import {
//   ExpressAPIDocumentor,
//   Repo,
// } from "../../src/api-documenting/ecma/express-api-documentor.js";
// import { LogContext } from "../../src/logging.js";
// import { TestContextBase, TestUtil } from "../../src/test-util.js";

// const test = anyTest as TestFn<TestContextBase>;

// test.beforeEach((t) => {
//   t.context = {
//     u: new TestUtil(),
//   };
// });

// const ctx = new LogContext();

// test("it is alive", (t) => {
//   const repo: Repo = {
//     name: "test-repo",
//     url: "test-url",
//   };

//   const d = new ExpressAPIDocumentor(repo, ctx);
//   t.assert(d);
// });

// test("it finds the express apps", async (t) => {
//   const repo: Repo = {
//     name: "test-repo",
//     url: "test-url",
//   };

//   const d = new ExpressAPIDocumentor(repo, ctx);
//   const v = await d.getExpressAPIs({
//     dir: `${process.env["EAVE_HOME"]}/libs/eave-stdlib-ts/tests/api-documenting/test-projects`,
//   });

//   t.assert(
//     v.some((api) => {
//       return api.name === "Express Ts API" && api.endpoints.length === 1;
//     }),
//   );
// });
