function buildConfig() {
  const config = {
    schema: './node_modules/@octokit/graphql-schema/schema.graphql',
    documents: [
      './src/graphql/**/*.graphql',
    ],
  };

  return config;
}

module.exports = buildConfig();
