/** @type {import("prettier").Config} */
const config = {
  plugins: [
    "prettier-plugin-multiline-arrays",
    "prettier-plugin-organize-imports",
  ],
  printWidth: 10000,
  multilineArraysWrapThreshold: 3,
};

module.exports = config;
