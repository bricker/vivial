function buildConfig() {
  const config = {
    extends: [
      './node_modules/@bricker/tooling-configs/configs/eslintrc.cjs',
    ],
    // Add your config overrides here
  };

  return config;
}

module.exports = buildConfig();
