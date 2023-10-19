#!/usr/bin/env node

const dotenv = require("dotenv");
const path = require("node:path");
const nodemon = require("../../../node_modules/nodemon/lib/");

const EAVE_HOME = process.env["EAVE_HOME"];

dotenv.config({
  path: path.join(EAVE_HOME, "develop/shared/share.env"),
  override: true,
});
dotenv.config({ path: path.join(EAVE_HOME, ".env"), override: true });

try {
  dotenv.config({
    path: path.join(EAVE_HOME, ".eavefyi-dev.env"),
    override: true,
  });
} catch (e) {
  console.warn(".eavefyi-dev.env file not found");
}

dotenv.populate(
  process.env,
  {
    GAE_SERVICE: "github",
    PORT: "5300",
  },
  { override: true },
);

nodemon(
  [
    `--exec ${EAVE_HOME}/node_modules/.bin/tsx`,
    "--watch ./src",
    `--watch ${EAVE_HOME}/libs/eave-stdlib-ts`,
    "--delay 5",
    "./server.ts",
  ].join(" "),
);
