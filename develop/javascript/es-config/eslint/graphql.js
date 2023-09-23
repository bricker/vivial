const config = {
  overrides: [
    {
      files: ["*.graphql", "*.gql"],
      parser: "@graphql-eslint/eslint-plugin",
      plugins: ["@graphql-eslint"],
    },
  ],
};

module.exports = config;
