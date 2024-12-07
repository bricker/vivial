// @ts-check

const { requireGraphQLSchema } = require("@graphql-eslint/eslint-plugin");
const { Kind } = require("graphql");

/**
 * @typedef {import("@graphql-eslint/eslint-plugin").GraphQLESLintRule<any, true>} GraphQLESLintRule
 * @typedef {import("graphql").FieldNode} FieldNode
 */

/** @type GraphQLESLintRule */
const rule = {
  meta: {
    type: "problem",
    schema: false,
  },

  create(context) {
    requireGraphQLSchema("@eave-fyi/graphql-required-viewer-selections", context);

    return {
      Field(node) {
        const rootGqlType = node.typeInfo().gqlType;
        if (!rootGqlType) {
          // If gqlType isn't available, don't warn.
          return;
        }

        const isViewerField =
          "ofType" in rootGqlType &&
          "name" in rootGqlType.ofType &&
          ["ViewerQueries", "ViewerMutations"].includes(rootGqlType.ofType.name);

        if (!isViewerField) {
          return;
        }

        const hasRequiredInlineFragment = node.selectionSet?.selections.some((selection) => {
          const selectionGqlType = selection.typeInfo().gqlType;
          if (!selectionGqlType) {
            return true; // If gqlType isn't available, don't warn.
          }

          return (
            "name" in selectionGqlType &&
            selectionGqlType.name === "UnauthenticatedViewer" &&
            selection.kind === Kind.INLINE_FRAGMENT &&
            selection.selectionSet?.selections.some((s) => {
              return s.kind === Kind.FIELD && s.name.value === "authAction" && !("alias" in s && !!s.alias); // disallow alias for this field
            })
          );
        });

        if (!hasRequiredInlineFragment) {
          context.report({
            node,
            message:
              "Field `UnauthenticatedViewer.authAction` (unaliased) is mandatory on Viewer operations, to support automated auth token refresh.",
          });
        }
      },
    };
  },
};

module.exports = rule;
