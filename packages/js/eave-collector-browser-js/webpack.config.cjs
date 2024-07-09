const webpack = require("webpack");
const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env, argv) => {
  const mode = argv.mode || "development";
  const trackerUrl = env.TRACKER_URL || "https://api.eave.fyi/public/ingest/browser";
  const dropConsole = mode === "development" ? false : ["debug"];

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
            compress: {
              drop_console: dropConsole,
            },
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
        WEBPACK_ENV_MODE: JSON.stringify(mode),
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
