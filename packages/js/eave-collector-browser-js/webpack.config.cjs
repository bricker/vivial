const webpack = require("webpack");
const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env, argv) => {
  const mode = argv.mode || "development";
  const logLevel = env.LOG_LEVEL?.toUpperCase();

  return {
    mode,
    entry: {
      index: "./src/main.mjs",
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
          test: /\.m?js$/,
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
        LOG_LEVEL: JSON.stringify(logLevel.toUpperCase()),
      }),
    ],

    devServer: {
      server: "http",
      allowedHosts: [
        "localhost",
        "127.0.0.1",
        ".eave.run",
      ],
    },
  };
};
