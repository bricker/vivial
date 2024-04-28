const { resolve } = require("dns/promises");
const path = require("path");

module.exports = {
  mode: "development",
  entry: path.join(__dirname, "eave_playground/todoapp/js/App.tsx"),
  devtool: "eval-source-map",
  output: {
    path: path.join(__dirname, "eave_playground/todoapp/static/dist"),
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
        },
      },
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
    ],
  },

  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
  },

  // This configuration is only used by the dev server, which we currently don't use in development.
  devServer: {
    server: "http",
    static: {
      directory: path.join(__dirname, "eave_playground/todoapp/static"),
      publicPath: "/static",
    },
    client: {
      overlay: false,
    },
  },
};
