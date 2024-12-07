import type { AddPluginConfig } from "@graphql-codegen/add";
import type { CodegenConfig } from "@graphql-codegen/cli";
import type { ClientPresetConfig } from "@graphql-codegen/client-preset";
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
      config: {
        // See here: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client#config-api
        // The options here are forwarded to other plugins and the exact properties aren't available in a type,
        // so use the documentation to know which options are available.
        documentMode: "string",
        defaultScalarType: "string",
        strictScalars: true,
        useTypeImports: true,

        /**
         * It is important that graphql-codegen _does not_ add `__typename` to the generated types unless it's explicitly selected.
         * When `__typename` is always added to the generated types, then the typescript compiler thinks the field is available and doesn't give errors.
         * But, in the code, we cast the JSON responses to the response type (eg, `response.json() as CreateAccountMutation`).
         * So typescript is actually just working with the data that was returned from the server, which may not actually include `__typename`.
         * By disabling this flag, the generated types will only have `__typename` if it was explicitly selected, and so typescript will behave as expected.
         */
        skipTypename: true,
        nonOptionalTypename: false,

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
