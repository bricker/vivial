const webpack = require("webpack");
const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env, argv) => {
  const mode = argv.mode || "development";
  const logLevel = env.LOG_LEVEL?.toUpperCase() || "INFO";
  const trackerUrl =
    env.TRACKER_URL || "https://api.eave.fyi/public/ingest/browser";

  return {
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
            compress: true,
            format: {
              comments: false,
              ecma: "2015",
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
        WEBPACK_ENV_TRACKER_URL: JSON.stringify(trackerUrl),
        WEBPACK_ENV_LOG_LEVEL: JSON.stringify(logLevel.toUpperCase()),
      }),
    ],

    resolve: {
      extensions: [".ts", ".js"],
    },

    devServer: {
      server: "http",
      allowedHosts: ["localhost", "127.0.0.1", ".eave.run"],
    },
  };
};
