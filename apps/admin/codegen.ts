import { buildCodegenConfig } from "@eave-fyi/develop/codegen";

const schema = process.env["ADMIN_GRAPHQL_SCHEMA"] || "http://api.internal.eave.run:8080/internal/graphql";

export default buildCodegenConfig({
  schema,
  documents: ["eave/admin/**/*.graphql"],
  destination: "./eave/admin/js/graphql/generated/",
});
