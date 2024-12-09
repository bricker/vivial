// @ts-check

/**
 * @typedef {import("eslint").Linter.LegacyConfig} ESLintConfig
 */

/** @type ESLintConfig */
const config = {
  overrides: [
    {
      files: ["*.yaml", "*.yml"],
      extends: ["plugin:yaml/recommended"],
      plugins: ["yaml"],
    },
  ],
};

module.exports = config;
