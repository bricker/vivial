// allows graphql files loaded by raw-loader to be imported in TS files
declare module "*.graphql" {
  const content: any;
  export default content;
}
