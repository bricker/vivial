function buildConfig() {
  const config = {
    extends: [
      'airbnb-base',
      'plugin:yaml/recommended',
    ],
    plugins: [
      'yaml',
    ],
    root: true,
    ignorePatterns: [
      'node_modules',
      '*.doccarchive',
      '!.github',
    ],
    env: {
      browser: true,
      es2022: true,
      node: true,
    },
    parserOptions: {
      ecmaVersion: 13,
      impliedStrict: true,
    },
    rules: {
      'import/no-unresolved': 0, // https://github.com/import-js/eslint-plugin-import/issues/1810
      'import/extensions': 0, // extensions always required
      'arrow-body-style': 0,
      'no-param-reassign': 1,
      'class-methods-use-this': 0,
      'max-classes-per-file': 0,
      'no-restricted-syntax': 0,
      'object-curly-newline': 0,
      'max-len': 0,
      'function-paren-newline': 0,
      'no-useless-return': 0,
      'no-continue': 0,
      'no-console': 0,
      'no-underscore-dangle': 0,
    },
    overrides: [
      {
        // Force eslint to lint the following additional extensions.
        files: ['*.cjs', '*.mjs', '*.yaml', '*.yml'],
      },
      {
        // ava's `t` context variable is intended to be modified during the lifecycle of a test.
        files: ['*.test.js'],
        rules: {
          'no-param-reassign': 0,
        },
      },
      {
        // template curly syntax ${{ expr }} is used by github actions workflows
        files: ['.github/workflows/src/**/*.js'],
        rules: {
          'no-template-curly-in-string': 0,
        },
      },
    ],
  };

  return config;
}

module.exports = buildConfig();
