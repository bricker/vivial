/** Helper type to union w/ response data types */
export type NetworkState<TDataType> = {
  loading: boolean;
  data?: TDataType;
  error?: Error;
};

interface GraphQLExecutionError extends Error {}

interface GraphQLExecutionErrorConstructor extends ErrorConstructor {
  new (errors: any[]): GraphQLExecutionError;
  (errors: any[]): GraphQLExecutionError;
  readonly prototype: GraphQLExecutionError;
}

export declare const GraphQLExecutionError: GraphQLExecutionErrorConstructor;
