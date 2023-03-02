const secrets = require('./secrets.json');

function buildConfig() {
  const config = {
    schema: {
      'https://api.github.com/graphql': {
        headers: {
          authorization: `Bearer ${secrets.GITHUB_TOKEN}`,
        },
      },
    },
  };

  return config;
}

module.exports = buildConfig();
