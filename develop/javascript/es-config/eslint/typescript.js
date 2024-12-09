// @ts-check

/**
 * @typedef {import("eslint").Linter.LegacyConfig} ESLintConfig
 */

/** @type ESLintConfig */
const config = {
  overrides: [
    {
      files: ["*.ts", "*.tsx"],
      extends: [
        "plugin:@typescript-eslint/recommended-type-checked",
        // "plugin:@typescript-eslint/stylistic-checked",
      ],
      plugins: ["@typescript-eslint"],
      parser: "@typescript-eslint/parser",
      parserOptions: {
        projectService: true,
        tsconfigRootDir: process.env["EAVE_HOME"],
      },
      rules: {
        /* Turn off things automatically enabled by the "recommended" preset. */
        "@typescript-eslint/prefer-promise-reject-errors": "off", // Rejecting with a non-error isn't ideal, but not a bug.
        "@typescript-eslint/no-non-null-assertion": "off", // Useful language feature
        "@typescript-eslint/no-explicit-any": "off", // useful language feature
        "@typescript-eslint/no-empty-interface": "off", // useful for readability
        "@typescript-eslint/no-empty-function": "off", // useful for readability

        /* Turn on things not included in the "recommended" preset */
        "@typescript-eslint/no-floating-promises": "warn", // A genuine source of bugs
        "@typescript-eslint/no-shadow": "warn",
        "no-shadow": "off", // There is a bug with this rule for typescript files, replaced by above
        "@typescript-eslint/no-misused-promises": [
          "warn",
          {
            checksVoidReturn: {
              /**
               * This allows passing an async function to non-async JSX function props, eg `onClick`.
               * That could cause a bug, but it's so common that hacking around it every time would be a bad developer experience.
               */
              attributes: false,
              /**
               * The rest are here for reference. They all default to `true`.
               */
              // arguments: true,
              // inheritedMethods: true,
              // properties: true,
              // returns: true,
              // variables: true,
            },
          },
        ],
        "@typescript-eslint/switch-exhaustiveness-check": [
          "warn",
          {
            // https://typescript-eslint.io/rules/switch-exhaustiveness-check
            allowDefaultCaseForExhaustiveSwitch: true,
            considerDefaultExhaustiveForUnions: true,
            requireDefaultForNonUnion: true,
          },
        ],
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
  ],
};

module.exports = config;
