const assert = require('node:assert');

const EAVE_HOME = process.env.EAVE_HOME;
assert(EAVE_HOME !== undefined);

function buildConfig() {
  const config = {
    extends: [
      `${EAVE_HOME}/develop/javascript/configs/eslint.config.cjs`,
    ],
    // Add your config overrides here
  };

  return config;
}

module.exports = buildConfig();
