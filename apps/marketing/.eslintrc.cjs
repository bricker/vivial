const config = {
  extends: [
    './node_modules/@eave-fyi/es-config/eslint',
    './node_modules/@eave-fyi/es-config/eslint/react',
    './node_modules/@eave-fyi/es-config/eslint/yaml',
  ],
  rules: { 'react/no-unescaped-entities': 0 },
};

module.exports = config;
