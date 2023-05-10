const config = {
  extends: [
    '@eave-fyi/es-config/eslint',
    '@eave-fyi/es-config/eslint/typescript',
    '@eave-fyi/es-config/eslint/yaml',
  ],
  rules: {
    'no-console': 'off',
  },
};

module.exports = config;
