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
};
