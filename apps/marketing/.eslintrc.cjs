const config = {
  extends: [
    '@eave-fyi/es-config/eslint',
    '@eave-fyi/es-config/eslint/react',
    '@eave-fyi/es-config/eslint/yaml',
  ],
  rules: { 'react/no-unescaped-entities': 0 },
};

module.exports = config;
