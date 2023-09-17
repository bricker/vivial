const path = require('node:path');

function buildConfig(name, overrides = {}) {
  return {
    apps: [{
      name,
      script: './server.ts',
      out_file: '/dev/stdout',
      error_file: '/dev/stderr',
      interpreter: path.join(__dirname, 'node_modules/.bin/tsx'),
      ...overrides,
    }],
  };
}
module.exports = buildConfig;