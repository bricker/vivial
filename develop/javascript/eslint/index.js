const config = {
  extends: [
    'airbnb-base',
  ],
  plugins: [],
  ignorePatterns: [
    'node_modules',
    '*.doccarchive',
    '!.github',
    'dist',
  ],
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  parserOptions: {
    ecmaVersion: 'latest',
    impliedStrict: true,
  },
  rules: {
    'import/no-unresolved': 'off', // https://github.com/import-js/eslint-plugin-import/issues/1810
    'import/extensions': 'off', // extensions always required
    'import/prefer-default-export': 'off',
    'arrow-body-style': 'off',
    'no-param-reassign': 'warn',
    'class-methods-use-this': 'off',
    'max-classes-per-file': 'off',
    'no-restricted-syntax': 'off',
    'object-curly-newline': 'off',
    'max-len': 'off',
    'function-paren-newline': 'off',
    'no-useless-return': 'off',
    'no-continue': 'off',
    'no-console': 'warn',
    'no-underscore-dangle': 'off',
    'dot-notation': 'off',
    'no-use-before-define': ['error', {
      functions: false,
      classes: false,
      variables: true,
    }],
  },
  overrides: [
    {
      // Force eslint to lint the following additional extensions.
      files: ['*.cjs', '*.mjs'],
    },
    {
      // ava's `t` context variable is intended to be modified during the lifecycle of a test.
      files: ['*.test.js'],
      rules: {
        'no-param-reassign': 'off',
      },
    },
    {
      // template curly syntax ${{ expr }} is used by github actions workflows
      files: ['.github/workflows/src/**/*.js'],
      rules: {
        'no-template-curly-in-string': 'off',
      },
    },
  ],
};

module.exports = config;
