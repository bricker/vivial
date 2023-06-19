const path = require('node:path');

const config = {
  extends: [
    './node_modules/@eave-fyi/es-config/eslint',
    './node_modules/@eave-fyi/es-config/eslint/typescript',
  ],
  parserOptions: {
    project: path.join(__dirname, 'tsconfig.json'),
  },
};

module.exports = config;
