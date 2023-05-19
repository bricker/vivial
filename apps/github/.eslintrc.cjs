const config = {
  extends: [
    '@eave-fyi/eslint-config',
    '@eave-fyi/eslint-config/typescript',
    // FIXME: Add this back. It was removed because something something commonjs
    // '@eave-fyi/eslint-config/graphql',
    '@eave-fyi/eslint-config/yaml',
  ],
  rules: {
    'no-console': 'off',
  },
};

module.exports = config;
