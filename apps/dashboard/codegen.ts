import { buildCodegenConfig } from "@eave-fyi/develop/codegen";

const schema = process.env["GRAPHQL_SCHEMA"] || "http://api.eave.run:8080/graphql";

export default buildCodegenConfig({
  schema,
  documents: ["eave/dashboard/**/*.graphql"],
  destination: "./eave/dashboard/js/graphql/generated/graphql.ts",
});
