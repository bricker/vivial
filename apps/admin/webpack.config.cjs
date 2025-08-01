const path = require("node:path");
const buildWebpackConfig = require("../../develop/javascript/webpack.config.cjs");

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
    entry: path.join(__dirname, "eave/admin/js/index.tsx"),
    staticDirectory: path.join(__dirname, "eave/admin/static"),
    alias: {
      "$eave-admin": path.resolve(__dirname, "eave/admin"),
    },
  });
};
