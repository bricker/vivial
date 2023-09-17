import { familySync, GLIBC } from "detect-libc"; // eslint-disable-line import/no-extraneous-dependencies

// eslint-disable-next-line no-unused-vars
export default ({ projectDir }) => {
  return {
    files: ["tests/**/*.test.ts"],
    extensions: {
      ts: "module",
    },
    nodeArguments: ["--loader=tsx"],
    // worker threads may need to be disabled to prevent test failures in some linux flavors
    // https://github.com/lovell/sharp/issues/3164
    workerThreads: familySync() !== GLIBC,
  };
};
