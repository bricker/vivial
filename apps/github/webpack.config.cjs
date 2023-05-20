const path = require('path');

module.exports = {
  mode: 'production',
  entry: path.join(__dirname, 'src/app.ts'),
  target: 'node18',
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
  },
};
