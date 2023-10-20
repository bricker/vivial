// @ts-check
const path = require("node:path");
const dotenv = require("dotenv");
const { EAVE_HOME, GOOGLE_CLOUD_PROJECT } = require("./constants.cjs");

function loadStandardDotenvFiles() {
  dotenv.config({
    path: path.join(EAVE_HOME, "develop/shared/share.env"),
    override: true,
  });

  dotenv.config({ path: path.join(EAVE_HOME, ".env"), override: true });

  try {
    dotenv.config({
      path: path.join(EAVE_HOME, `.${GOOGLE_CLOUD_PROJECT}.env`),
      override: true,
    });
  } catch (e) {
    console.warn(`.${GOOGLE_CLOUD_PROJECT}.env file not found`);
  }
}

function populateEnv(
  /** @type {import("dotenv").DotenvPopulateInput} */ parsed,
) {
  dotenv.populate(process.env, parsed, { override: true });
}

module.exports = { loadStandardDotenvFiles, populateEnv };
