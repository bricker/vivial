// eslint-disable-next-line no-unused-vars
export default ({ projectDir }) => {
  return {
    files: [
      'tests/**/*.test.ts',
    ],
    extensions: {
      ts: 'module',
    },
    nodeArguments: [
      '--loader=ts-node/esm/transpile-only',
    ],
  };
};
