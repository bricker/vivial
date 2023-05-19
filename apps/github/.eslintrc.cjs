const config = {
  extends: [
    '@eave-fyi/eslint-config',
    '@eave-fyi/eslint-config/typescript',
    // '@eave-fyi/eslint-config/graphql',
    '@eave-fyi/eslint-config/yaml',
  ],
  rules: {
    'no-console': 'off',
  },
};

module.exports = config;
