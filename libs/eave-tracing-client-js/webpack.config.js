const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    index: './eave-client.js',
  },
  output: {
    filename: 'eave-client.min.js',
    path: path.resolve(__dirname, 'dist'),
  },
};
