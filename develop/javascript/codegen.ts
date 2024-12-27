import { type AddPluginConfig } from "@graphql-codegen/add";
import { type CodegenConfig } from "@graphql-codegen/cli";
import { addTypenameSelectionDocumentTransform } from "@graphql-codegen/client-preset";
import { type TypeScriptTypedDocumentNodesConfig } from "@graphql-codegen/typed-document-node";
import { type TypeScriptPluginConfig } from "@graphql-codegen/typescript";
import { type TypeScriptDocumentsPluginConfig } from "@graphql-codegen/typescript-operations";

export function buildCodegenConfig({ schema, documents, destination}: { schema: string; documents: string[], destination: string; }): CodegenConfig {
  return {
    schema,
    ignoreNoDocuments: true,
    noSilentErrors: true,
    documents,

    generates: {
      [destination]: {
        overwrite: true,
        documentTransforms: [addTypenameSelectionDocumentTransform],
        plugins: [
          {
            add: <AddPluginConfig>{
              placement: "prepend",
              content: "// @ts-nocheck",
            },
          },
          {
            add: <AddPluginConfig>{
              placement: "prepend",
              content: "/* eslint-disable */",
            },
          },
          {
            typescript: <TypeScriptPluginConfig>{},
          },
          {
            "typescript-operations": <TypeScriptDocumentsPluginConfig>{},
          },
          {
            "typed-document-node": <TypeScriptTypedDocumentNodesConfig>{
              documentMode: "string",
            },
          },
        ],
        config: <TypeScriptDocumentsPluginConfig & TypeScriptTypedDocumentNodesConfig & TypeScriptPluginConfig>{
          printFieldsOnNewLines: true,
          useTypeImports: true,
          strictScalars: true,
          defaultScalarType: "string",
          scalars: {
            // These scalars match what the server provided, including the scalars built-in to Strawberry:
            // https://strawberry.rocks/docs/types/scalars
            UUID: "string",
            Void: "null",
            DateTime: "string",
            Date: "string",
            Time: "string",
            Decimal: "string",
            JSON: "string",
            Base16: "string",
            Base32: "string",
            Base64: "string",
          },
        },
      },
    },
  };
};
