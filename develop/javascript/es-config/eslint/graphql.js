const config = {
  overrides: [
    {
      files: ["*.graphql", "*.gql"],
      extends: "plugin:@graphql-eslint/operations-recommended",
      rules: {
        // If the client needs the ID they'll select it.
        "@graphql-eslint/require-id-when-available": "off",
      },
    },
  ],
};

module.exports = config;
