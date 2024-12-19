// @ts-check

/**
 * @typedef {import("eslint").Linter.LegacyConfig} ESLintConfig
 */

/** @type ESLintConfig */
const config = {
  overrides: [
    {
      files: ["*.graphql", "*.gql"],
      extends: "plugin:@graphql-eslint/operations-recommended",
      plugins: ["@graphql-eslint", "@eave-fyi/eslint-plugin"],
      rules: {
        // If the client needs the ID they'll select it.
        // "@graphql-eslint/require-id-when-available": "off",
        "@graphql-eslint/selection-set-depth": [
          "error",
          {
            maxDepth: 10, // This matches the limit on the server
          },
        ],
        "@graphql-eslint/require-selections": [
          "error",
          {
            fieldName: [
              // This is necessary for refresh token logic
              // Note that this is only enforced if `UnauthenticatedViewer` inline fragment is selected
              // So it doesn't prevent an operation from leaving that out entirely, which would also be a bug.
              "authFailureReason",
            ],
          },
        ],
        "@eave-fyi/graphql-required-viewer-selections": "error",
      },
    },
  ],
};

module.exports = config;
