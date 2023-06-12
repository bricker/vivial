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
    'generated',
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
    'no-param-reassign': 'warn', // This rule is weird, sometimes it's good and sometimes it's bad.
    'import/prefer-default-export': 'off', // I refuse to refactor code when I want to add a second export
    'class-methods-use-this': 'off', // I refuse to refactor code if I remove references to `this` in a function
    'max-classes-per-file': 'off', // I refuse to refactor code to make a file shorter
    'max-len': 'off', // I refuse to refactor code to make a line shorter
    'no-else-return': 'off', // else after return can be good for readability
    'no-useless-return': 'off', // useless returns are good for readability and don't cause bugs
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
    'object-curly-newline': 'off',
    'function-paren-newline': 'off',
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
