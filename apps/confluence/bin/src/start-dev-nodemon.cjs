// @ts-check
const nodemon = require("nodemon/lib");
const {
  loadStandardDotenvFiles,
  populateEnv,
} = require("../../../../develop/javascript/dotenv-loader.cjs");
const { EAVE_HOME } = require("../../../../develop/javascript/constants.cjs");

loadStandardDotenvFiles();
populateEnv({
  GAE_SERVICE: "confluence",
  PORT: "5400",
});

nodemon(
  [
    `--exec ${EAVE_HOME}/node_modules/.bin/tsx`,
    "--watch ./src",
    `--watch ${EAVE_HOME}/libs/eave-stdlib-ts`,
    "--delay 5",
    "./server.ts",
  ].join(" "),
);
