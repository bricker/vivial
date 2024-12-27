import { buildCodegenConfig } from "../../develop/javascript/codegen-shared";

const schema = process.env["ADMIN_GRAPHQL_SCHEMA"] || "http://api.eave.run:8080/internal/graphql";

export default buildCodegenConfig({
  schema,
  documents: ["eave/admin/**/*.graphql"],
  destination: "./eave/admin/js/graphql/generated/graphql.ts",
});
