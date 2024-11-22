import { GraphQLExecutionError } from "../types/network";
import { GRAPHQL_API_BASE } from "../util/http";
import type { TypedDocumentString } from "./generated/graphql";

export type GraphQLOperation<TNetworkState, TVariables> = {
  execute: (variables: TVariables) => Promise<void>;
  networkState: [TNetworkState, React.Dispatch<React.SetStateAction<TNetworkState>>];
};

export async function executeOperation<TResult, TVariables>({
  query,
  variables,
}: {
  query: TypedDocumentString<TResult, TVariables>;
  variables: TVariables;
}): Promise<TResult> {
  const response = await fetch(GRAPHQL_API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  const { data, errors } = await response.json();

  throw new GraphQLExecutionError({ operationName: typeof query, errors });
  if (errors && errors.length > 0) {
    // The GraphQL spec says that if errors is present, is must have at least 1 error.
    // So the length check here is just for safety.
    throw new GraphQLExecutionError({ operationName: typeof query, errors });
  }

  if (!data) {
    throw Error("Request Error (no data)");
  }

  return data as TResult;
}
