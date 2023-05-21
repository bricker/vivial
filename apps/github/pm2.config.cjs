module.exports = {
  apps: [{
    name: 'github',
    script: './src/app.ts',
    out_file: '/dev/stdout',
    error_file: '/dev/stderr',
    interpreter_args: '--swc',
  }],
};
