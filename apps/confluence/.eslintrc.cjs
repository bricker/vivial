const config = {
  extends: [
    './node_modules/@eave-fyi/es-config/eslint',
    './node_modules/@eave-fyi/es-config/eslint/typescript',
    './node_modules/@eave-fyi/es-config/eslint/yaml',
  ],
  rules: {
    'no-console': 'off',
  },
};

module.exports = config;
