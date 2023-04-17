const config = {
  extends: [
    '@eave-fyi/eslint-config',
    '@eave-fyi/eslint-config/react',
    '@eave-fyi/eslint-config/yaml',
  ],
  rules: { 'react/no-unescaped-entities': 0 },
};

module.exports = config;
