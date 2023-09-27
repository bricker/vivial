import { familySync, GLIBC } from "detect-libc";

export default (/* { projectDir } */) => {
  return {
    files: ["tests/**/*.test.ts"],
    extensions: {
      ts: "module",
    },
    nodeArguments: ["--loader=tsx"],
    // worker threads may need to be disabled to prevent test failures in some linux flavors
    // https://github.com/lovell/sharp/issues/3164
    workerThreads: familySync() !== GLIBC,
    require: [`${process.env["EAVE_HOME"]}/develop/javascript/es-config/ava/test-setup.js`],
  };
};
