const path = require('node:path');

const config = {
  extends: [
    './develop/javascript/es-config/eslint',
    './develop/javascript/es-config/eslint/typescript',
    './develop/javascript/es-config/eslint/graphql',
    './develop/javascript/es-config/eslint/yaml',
    './develop/javascript/es-config/eslint/react',
  ],
  parserOptions: {
    project: './tsconfig.json',
  },
};

module.exports = config;
