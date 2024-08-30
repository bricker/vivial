// @ts-check

const webpack = require("webpack");
const path = require("node:path");
const TerserPlugin = require("terser-webpack-plugin");
require("webpack-dev-server"); // for devServer config typing

/**
 * @typedef {{ mode?: "none" | "development" | "production"; }} WebpackArgs
 */

/**
 * @typedef {{ EAVE_API_BASE_URL?: string; }} EnvConfig
 */

/**
 * @param {EnvConfig} env
 * @param {WebpackArgs} argv
 *
 * @returns {webpack.Configuration}
 */
const configFunc = (env, argv) => {
  const mode = argv.mode || "development";
  const trackerUrl = env.EAVE_API_BASE_URL || "https://api.eave.fyi/";

  /** @type webpack.Configuration */
  const config = {
    mode,
    entry: {
      index: "./src/main.ts",
    },
    output: {
      filename: "collector.js",
      path: path.resolve(__dirname, "dist"),
    },
    devtool: false,
    optimization: {
      minimize: mode !== "development",
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            mangle: true,
            compress: {
              drop_console: mode === "development" ? false : ["debug"],
            },
            format: {
              comments: false,
              ecma: 2015,
            },
          },
          extractComments: false,
        }),
      ],
    },
    module: {
      rules: [
        {
          test: /\.ts?$/,
          exclude: /node_modules/,
          use: {
            loader: "ts-loader",
          },
        },
      ],
    },
    plugins: [
      new webpack.DefinePlugin({
        WEBPACK_ENV_EAVE_API_BASE_URL: JSON.stringify(trackerUrl),
        WEBPACK_ENV_MODE: JSON.stringify(mode),
      }),
    ],

    resolve: {
      extensions: [".ts", ".js"],
    },

    devServer: {
      server: "http",
      port: 3001,
      host: "127.0.0.1",
      allowedHosts: ["localhost", "127.0.0.1", ".eave.run"],
    },
  };

  return config;
};

module.exports = configFunc;
