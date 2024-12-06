// @ts-check

/**
 * @typedef {import("eslint").Linter.LegacyConfig} ESLintConfig
 */

/** @type ESLintConfig */
const config = {
  extends: ["plugin:yaml/recommended"],
  plugins: ["yaml"],
};

module.exports = config;
