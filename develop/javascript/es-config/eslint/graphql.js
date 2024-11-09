const config = {
  overrides: [
    {
      files: ["*.graphql", "*.gql"],
      extends: "plugin:@graphql-eslint/operations-recommended",
    },
  ],
};

module.exports = config;
