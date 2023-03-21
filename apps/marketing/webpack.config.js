const path = require('path');

module.exports = {
  mode: 'development',
  entry: path.join(__dirname, 'eave_client', 'index.js'),
  devtool: 'eval-source-map',
  output: {
    path: path.resolve(__dirname, 'eave_static', 'dist'),
  },
  module: {
    rules: [
      {
        test: /\.?js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
      },
      {
        test: /\.(png|jpg|jpeg|gif)$/,
        loader: 'file-loader',
      },
    ],
  },
  devServer: {
    server: 'http',
    path: '/static',
    client: {
      overlay: false,
    },
  },
};
