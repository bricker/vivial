const config = {
  extends: ["eslint:recommended", "prettier"],
  plugins: [],
  ignorePatterns: ["node_modules", "dist", ".*"],
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  parserOptions: {
    ecmaVersion: "latest",
    impliedStrict: true,
    sourceType: "module",
  },
  rules: {
    // Rules that enforce consistent code style, but may not be fixable by a formatter. These could also indicate a bug.
    curly: ["warn", "all"],
    "no-var": "warn",
    "prefer-const": "warn",
    "no-useless-computed-key": "warn",
    "no-multi-assign": "warn",
    "import/extensions": "off", // extensions always required
    "default-param-last": "warn",
    "quote-props": ["warn", "as-needed"],

    // Rules that may indicate a bug
    "import/no-unresolved": "off", // https://github.com/import-js/eslint-plugin-import/issues/1810
    "no-unused-private-class-members": "warn",
    "no-template-curly-in-string": "warn",
    "no-self-compare": "warn",
    "no-constructor-return": "warn",
    "no-constant-binary-expression": "warn",
    "array-callback-return": "warn",
    "default-case": "warn",
    "default-case-last": "warn",
    eqeqeq: "warn",
    "guard-for-in": "warn",
    "no-invalid-this": "error",
    "no-new-wrappers": "warn",
    "no-octal-escape": "warn",
    "no-unused-expressions": "warn",
    radix: "warn",
    "no-unused-vars": [
      "warn",
      {
        varsIgnorePattern: "^_",
        argsIgnorePattern: "^_",
      },
    ],
    "no-restricted-syntax": [
      "error",
      {
        selector: "ForInStatement", // for...in is genuinely confusing and can cause bugs.
        message: "If you intend to iterate over an array, use for...of",
      },
    ],
    "no-use-before-define": [
      "error",
      {
        functions: false,
        classes: false,
        variables: true,
      },
    ],

    // Rules enabled by default that I don't like
    "import/prefer-default-export": "off",
    "import/order": "off", // prettier handles this
  },
  overrides: [
    {
      // Force eslint to lint the following additional extensions.
      files: ["*.cjs", "*.mjs"],
    },
    {
      files: ["*.test.js"],
      rules: {
        "no-unused-vars": "off", // Allow ava test context to be unused
      },
    },
    {
      files: ["*.ts"],
      extends: ["plugin:@typescript-eslint/recommended"],
      plugins: ["@typescript-eslint"],
      parser: "@typescript-eslint/parser",
      rules: {
        "@typescript-eslint/no-floating-promises": "warn", // A genuine source of bugs
        "@typescript-eslint/no-non-null-assertion": "off", // Useful language feature
        "@typescript-eslint/no-shadow": "warn",
        "no-shadow": "off", // There is a bug with this rule for typescript files, replaced by above
        "@typescript-eslint/no-explicit-any": "off", // useful language feature
        "@typescript-eslint/no-empty-interface": "off", // useful for readability
        "@typescript-eslint/no-empty-function": "off", // useful for readability
        "@typescript-eslint/no-unused-vars": [
          "warn",
          {
            varsIgnorePattern: "^_",
            argsIgnorePattern: "^_",
          },
        ],
        "@typescript-eslint/ban-ts-comment": [
          "error",
          {
            "ts-expect-error": "allow-with-description",
            "ts-ignore": "allow-with-description",
            "ts-nocheck": "allow-with-description",
            "ts-check": false, // always allowed
            minimumDescriptionLength: 1,
          },
        ],
      },
    },
    {
      files: ["*.test.ts"],
      rules: {
        "@typescript-eslint/no-unused-vars": "off", // Allow ava test context to be unused
      },
    },
  ],
};

module.exports = config;
