const path = require('node:path');

module.exports = {
  apps: [{
    name: 'ast-ts',
    script: './server.ts',
    out_file: '/dev/stdout',
    error_file: '/dev/stderr',
    interpreter: path.join(__dirname, 'node_modules/.bin/ts-node'),
    interpreter_args: '--swc',
  }],
};
