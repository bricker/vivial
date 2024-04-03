const path = require('path');

module.exports = {
  mode: 'development',
  entry: {
    index: './src/eave-client.js',
  },
  output: {
    filename: 'eave-client.min.js',
    path: path.resolve(__dirname, 'dist'),
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
};
