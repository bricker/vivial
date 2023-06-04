const path = require('node:path');

// TODO: Share this config across apps
module.exports = {
  apps: [{
    name: 'confluence',
    script: './src/app.ts',
    out_file: '/dev/stdout',
    error_file: '/dev/stderr',
    interpreter: path.join(__dirname, 'node_modules/.bin/ts-node'),
    interpreter_args: '--swc',
  }],
};
