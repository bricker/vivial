const webpack = require("webpack"); // eslint-disable-line
const path = require("node:path");
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
 *
 * @returns {webpack.Configuration}
 */
module.exports = (env, argv) => {
  const mode = argv.mode || MODE_DEVELOPMENT;

  return {
    mode,
    entry: path.join(__dirname, "eave/dashboard/js/index.tsx"),
    devtool: mode === MODE_DEVELOPMENT ? "eval-source-map" : false,
    output: {
      path: path.join(__dirname, "eave/dashboard/static/dist"),
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
        // {
        //   test: /\.jsx?$/,
        //   exclude: /node_modules/,
        //   use: {
        //     loader: "babel-loader",
        //     options: {
        //       presets: ["@babel/preset-env", "@babel/preset-react"],
        //     },
        //   },
        // },
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
      alias: {
        "$eave-dashboard": path.resolve(__dirname, "eave/dashboard"),
      },
    },

    // This configuration is only used by the dev server, which we currently don't use in development.
    devServer: {
      server: "http",
      static: {
        directory: path.join(__dirname, "eave/dashboard/static"),
        publicPath: "/static",
      },
      client: {
        overlay: false,
      },
    },
  };
};
