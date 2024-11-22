const config = {
  overrides: [
    {
      files: ["*.ts", "*.tsx"],
      extends: ["plugin:@typescript-eslint/recommended-type-checked"],
      plugins: ["@typescript-eslint"],
      parser: "@typescript-eslint/parser",
      parserOptions: {
        projectService: true,
        tsconfigRootDir: process.env["EAVE_HOME"],
      },
      rules: {
        "@typescript-eslint/no-floating-promises": "warn", // A genuine source of bugs
        "@typescript-eslint/no-non-null-assertion": "off", // Useful language feature
        "@typescript-eslint/no-shadow": "warn",
        "no-shadow": "off", // There is a bug with this rule for typescript files, replaced by above
        "@typescript-eslint/no-explicit-any": "off", // useful language feature
        "@typescript-eslint/no-empty-interface": "off", // useful for readability
        "@typescript-eslint/no-empty-function": "off", // useful for readability
        "@typescript-eslint/switch-exhaustiveness-check": [
          "warn",
          {
            allowDefaultCaseForExhaustiveSwitch: true,

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
    {
      files: ["*.test.ts"],
      rules: {
        "@typescript-eslint/no-unused-vars": "off", // Allow ava test context to be unused
      },
    },
  ],
};

module.exports = config;
