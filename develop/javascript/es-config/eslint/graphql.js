const config = {
  overrides: [
    {
      files: ['*.graphql', '*.gql'],
      plugins: ['graphql'],
      rules: {
        'graphql/template-strings': ['error', {
          env: 'literal',
        }],
      },
    },
  ],
};

module.exports = config;
