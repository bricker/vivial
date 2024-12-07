import { type AddPluginConfig } from "@graphql-codegen/add";
import type { CodegenConfig } from "@graphql-codegen/cli";
import { addTypenameSelectionDocumentTransform, type ClientPresetConfig } from "@graphql-codegen/client-preset";
const schema = process.env["GRAPHQL_SCHEMA"] || "http://api.eave.run:8080/graphql";

const config: CodegenConfig = {
  schema,
  documents: ["eave/dashboard/**/*.graphql"],
  ignoreNoDocuments: true,
  generates: {
    "./eave/dashboard/js/graphql/generated/": {
      preset: "client",
      presetConfig: <ClientPresetConfig>{
        fragmentMasking: false,
      },
      documentTransforms: [addTypenameSelectionDocumentTransform],
      config: {
        // See here: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client#config-api
        // The options here are forwarded to other plugins and the exact properties aren't available in a type,
        // so use the documentation to know which options are available.
        documentMode: "string",
        defaultScalarType: "string",
        strictScalars: true,
        useTypeImports: true,
        // nonOptionalTypename: true,

        scalars: {
          // These scalars match what the server provided, including the scalars built-in to Strawberry:
          // https://strawberry.rocks/docs/types/scalars
          UUID: {
            input: "string",
            output: "string",
          },
          Void: {
            input: "null",
            output: "null",
          },
          DateTime: {
            input: "string",
            output: "string",
          },
          Date: {
            input: "string",
            output: "string",
          },
          Time: {
            input: "string",
            output: "string",
          },
          Decimal: {
            input: "string",
            output: "string",
          },
          JSON: {
            input: "string",
            output: "string",
          },
          Base16: {
            input: "string",
            output: "string",
          },
          Base32: {
            input: "string",
            output: "string",
          },
          Base64: {
            input: "string",
            output: "string",
          },
        },
      },
      plugins: [
        {
          add: <AddPluginConfig>{
            placement: "prepend",
            content: "// @ts-nocheck",
          },
        },
      ],
    },
  },
};

export default config;
