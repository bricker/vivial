const webpack = require("webpack");
const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env, argv) => {
  const mode = argv.mode || "development";
  return {
    mode,
    entry: {
      index: "./src/eave-client.mjs",
    },
    output: {
      filename: "eave-client.min.js",
      path: path.resolve(__dirname, "dist"),
    },
    optimization: {
      minimize: true,
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
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
            },
          },
        },
      ],
    },
    plugins: [
      new webpack.DefinePlugin({
        PRODUCTION: mode === "production",
      }),
    ],
  };
};
