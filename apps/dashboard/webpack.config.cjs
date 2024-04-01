const path = require("path");

module.exports = {
  mode: "development",
  entry: path.join(__dirname, "eave/dashboard/js/index.js"),
  devtool: "eval-source-map",
  output: {
    path: path.join(__dirname, "eave/dashboard/static/dist"),
  },
  module: {
    rules: [
      {
        test: /\.?(jsx|js)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
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
