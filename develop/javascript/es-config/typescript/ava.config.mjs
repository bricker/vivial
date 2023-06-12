export default ({ projectDir }) => {
  return {
    files: [
      'tests/**',
    ],
    extensions: {
      ts: 'module',
    },
    nodeArguments: [
      '--loader=ts-node/esm/transpile-only',
    ],
  };
};