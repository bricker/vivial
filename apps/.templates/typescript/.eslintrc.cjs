const path = require('node:path');

const config = {
  extends: [
    './node_modules/@eave-fyi/es-config/eslint',
    './node_modules/@eave-fyi/es-config/eslint/typescript',
    './node_modules/@eave-fyi/es-config/eslint/yaml',
  ],
  parserOptions: {
    project: path.join(__dirname, 'tsconfig.json'),
  },
  rules: {
    'no-console': 'off',
  },
};

module.exports = config;
