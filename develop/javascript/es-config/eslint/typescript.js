const config = {
  overrides: [
    {
      files: ["*.ts", "*.tsx"],
      extends: ["plugin:@typescript-eslint/recommended"],
      plugins: ["@typescript-eslint", "unused-imports"],
      parser: "@typescript-eslint/parser",
      rules: {
        "@typescript-eslint/no-floating-promises": "warn", // A genuine source of bugs
        "@typescript-eslint/no-non-null-assertion": "off", // Useful language feature
        "@typescript-eslint/no-shadow": "warn",
        "no-shadow": "off", // There is a bug with this rule for typescript files, replaced by above
        "@typescript-eslint/no-explicit-any": "off",
        "@typescript-eslint/no-empty-interface": "off",
        "@typescript-eslint/no-empty-function": "off",
        "@typescript-eslint/no-unused-vars": "off", // This is replaced by the unused-imports plugin
        "unused-imports/no-unused-imports": "warn",
        "unused-imports/no-unused-vars": [
          "warn",
          {
            varsIgnorePattern: "^_",
            argsIgnorePattern: "^_",
          },
        ],
      },
    },
    {
      files: ["*.test.ts"],
      rules: {
        "unused-imports/no-unused-vars": "off", // Allow ava test context to be unused
      },
    },
  ],
};

module.exports = config;
