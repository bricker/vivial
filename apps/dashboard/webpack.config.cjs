const path = require("node:path");
const buildWebpackConfig = require("@eave-fyi/develop/webpack.config.cjs");

/**
 * @typedef {{ mode?: "none" | "development" | "production"; }} WebpackArgs
 */

/**
 * @typedef {{ }} EnvConfig
 */

/**
 * @param {EnvConfig} env
 * @param {WebpackArgs} argv
 *
 * @returns {import("webpack").Configuration}
 */
module.exports = (env, argv) => {
  return buildWebpackConfig(env, argv, {
    entry: path.join(__dirname, "eave/dashboard/js/index.tsx"),
    staticDirectory: path.join(__dirname, "eave/dashboard/static"),
    alias: {
      "$eave-dashboard": path.resolve(__dirname, "eave/dashboard"),
    },
  });
};
