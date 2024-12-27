const TerserPlugin = require("terser-webpack-plugin");
require("webpack-dev-server"); // for devServer config typing

const MODE_DEVELOPMENT = "development";

/**
 * @typedef {{ mode?: "none" | "development" | "production"; }} WebpackArgs
 */

/**
 * @typedef {{ }} EnvConfig
 */

/**
 * @param {EnvConfig} env
 * @param {WebpackArgs} argv
 * @param {{ entry: string; staticDirectory: string; alias: {[key: string]: string}; }} config
 *
 * @returns {import("webpack").Configuration}
 */
module.exports = function buildWebpackConfig(env, argv, { entry, staticDirectory, alias }) {
  const mode = argv.mode || MODE_DEVELOPMENT;

  return {
    mode,
    entry,
    devtool: mode === MODE_DEVELOPMENT ? "eval-source-map" : false,
    output: {
      path: `${staticDirectory}/dist`,
    },
    optimization: {
      minimize: mode !== MODE_DEVELOPMENT,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            mangle: true,
            compress: {
              drop_console: ["debug"],
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
          test: /\.tsx?$/,
          exclude: /node_modules/,
          use: {
            loader: "ts-loader",
          },
        },
        {
          test: /\.css$/,
          use: [{ loader: "style-loader" }, { loader: "css-loader" }],
        },
        {
          test: /\.(png|jpg|jpeg|gif)$/,
          loader: "file-loader",
        },
        {
          test: /\.graphql$/,
          exclude: /node_modules/,
          loader: "raw-loader",
        },
      ],
    },

    resolve: {
      extensions: [".ts", ".tsx", ".js", ".jsx"],
      alias,
    },

    // This configuration is only used by the dev server, which we currently don't use in development.
    devServer: {
      server: "http",
      static: {
        directory: staticDirectory,
        publicPath: "/static",
      },
      client: {
        overlay: false,
      },
    },
  };
};
