const config = {
  extends: [
    'airbnb-base',
    'prettier',
  ],
  plugins: [],
  ignorePatterns: [
    'node_modules',
    '*.doccarchive',
    '!.github',
    'dist',
    'generated',
    '.venv',
    '__pycache__',
    'vendor',
    '\.*',
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
    'no-restricted-syntax': ['error', {
      selector: 'ForInStatement', // for...in is genuinely confusing and can cause bugs.
      message: 'If you intend to iterate over an array, use for...of',
    }],
    camelcase: 'off', // Our API request bodies use snake case
    'no-param-reassign': 'off', // I understand that this may indicate a bug, but it is so common that it makes sense to completely disable it.
    'import/prefer-default-export': 'off', // Preference
    'class-methods-use-this': 'off', // Preference
    'max-classes-per-file': 'off', // Preference
    'max-len': 'off', // Preference
    'no-else-return': 'off', // else after return can be good for readability
    'no-useless-return': 'off', // useless returns are good for readability and don't necessarily indicate bugs
    'no-continue': 'off', // continues are a valid and useful language feature
    'no-await-in-loop': 'off', // awaiting in a loop is a valid and useful language feature
    'no-console': 'off', // Appengine reads stdout and stderr for app logs
    'dot-notation': 'off',
    'no-use-before-define': ['error', {
      functions: false,
      classes: false,
      variables: true,
    }],
    // Style preferences
    'prefer-destructuring': 'off',
    'no-underscore-dangle': 'off',
    'arrow-body-style': 'off',
  },
  overrides: [
    {
      // Force eslint to lint the following additional extensions.
      files: ['*.cjs', '*.mjs'],
    },
    {
      // ava's `t` context variable is intended to be modified during the lifecycle of a test.
      files: ['*.test.js', '*.test.ts'],
      rules: {
        'no-param-reassign': 'off',
        'import/no-extraneous-dependencies': 'off',
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
