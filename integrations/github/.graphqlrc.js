function buildConfig() {
  const config = {
    schema: {
      'https://api.github.com/graphql': {
        headers: {
          authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
        },
      },
    },
  };

  return config;
}

module.exports = buildConfig();
