/** Helper type to union w/ response data types */
export type NetworkState<TDataType> = {
  loading: boolean;
  data?: TDataType;
  error?: unknown; // We use `unknown` here because pretty much anything can be thrown, so assuming it's an `Error` type is dangerous.
};

export class GraphQLExecutionError extends Error {
  errors?: unknown[]; // We use `unknown` here because GraphQL errors don't have a specified schema.
  constructor({ operationName, errors }: { operationName?: string; errors?: unknown[] }) {
    super(`A GraphQL execution error occurred during ${operationName}`);
    this.errors = errors;
  }
}
