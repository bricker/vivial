const config = {
  extends: [
    'airbnb-base',
    'plugin:react/recommended',
    'prettier',
  ],
  plugins: [
    'react',
    'yaml',
  ],
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
    ecmaFeatures: {
      jsx: true,
    },
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
    'object-curly-newline': 'off',
    'function-paren-newline': 'off',
    'arrow-body-style': 'off',
    'react/jsx-filename-extension': 'off',
    'react/prop-types': 'off',
    'react/prefer-stateless-function': 'off',
    'react/jsx-one-expression-per-line': 'off',
  },
  overrides: [
    {
      files: ['*.yml', '*.yaml'],
      extends: 'plugin:yaml/recommended',
      plugins: ['yaml'],
    },
    {
      files: ['*.graphql', '*.gql'],
      parser: '@graphql-eslint/eslint-plugin',
      plugins: ['@graphql-eslint'],
      rules: {
      },
    },
    {
      files: ['*.ts', '*.tsx'],
      extends: ['plugin:@typescript-eslint/recommended'],
      plugins: [
        '@typescript-eslint',
        'unused-imports',
      ],
      parser: '@typescript-eslint/parser',
      rules: {
        '@typescript-eslint/no-floating-promises': 'warn', // A genuine source of bugs
        '@typescript-eslint/no-non-null-assertion': 'off', // Useful language feature
        '@typescript-eslint/no-shadow': 'warn',
        'no-shadow': 'off', // There is a bug with this rule for typescript files, replaced by above
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-empty-interface': 'off',
        '@typescript-eslint/no-empty-function': 'off',
        '@typescript-eslint/no-unused-vars': 'off', // This is replaced by the unused-imports plugin
        'unused-imports/no-unused-imports': 'warn',
        'unused-imports/no-unused-vars': [
          'warn',
          {
            varsIgnorePattern: '^_',
            argsIgnorePattern: '^_',
          },
        ],
      },
    },
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
        'unused-imports/no-unused-vars': 'off'
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
