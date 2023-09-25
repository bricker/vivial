module.exports = function buildConfig(name = "express", overrides = {}) {
  return {
    apps: [
      {
        name,
        script: "./server.ts",
        out_file: "/dev/stdout",
        error_file: "/dev/stderr",
        interpreter: "./node_modules/.bin/tsx",
        ...overrides,
      },
    ],
  };
};
