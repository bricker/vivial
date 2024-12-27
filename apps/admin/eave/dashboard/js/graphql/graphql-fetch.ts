import type React from "react";
import { GraphQLExecutionError } from "../types/network";
import { ADMIN_GRAPHQL_API_BASE } from "../util/http";
import { type TypedDocumentString } from "./generated/graphql";

export type GraphQLOperation<TNetworkState, TVariables> = {
  execute: (variables: TVariables) => Promise<void>;
  networkState: [TNetworkState, React.Dispatch<React.SetStateAction<TNetworkState>>];
};

type GraphQLResponse = {
  data?: unknown;
  errors?: unknown;
};

type GraphQLOperationType = "mutation" | "query" | "subscription";

type GraphqlOperationMetadata = {
  operationType?: GraphQLOperationType;
  operationName?: string;
};

export async function executeOperation<TResult, TVariables>({
  query,
  variables, // allowTokenRefresh = true,
}: {
  query: TypedDocumentString<TResult, TVariables>;
  variables: TVariables;
  allowTokenRefresh?: boolean;
}): Promise<TResult> {
  const response = await fetch(ADMIN_GRAPHQL_API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // This is required so that the cookies are sent to the subdomain (api.)
    body: JSON.stringify({
      query,
      variables,
    }),
  });

  /**
   * response.json() returns Promise<any>, which violates our eslint rule about assigning type `any`.
   * So we forcefully give it our expected type.
   * It's still dangerous, because there's no guarantee that the response contains the expected properties,
   * so we also set everything as optional and `unknown` in the GraphQLResponse type for some safety.
   * Additionally, we check that the call to json() didn't return undefined or null, to avoid unhelpful errors.
   */
  const parsedResponse = (await response.json()) as GraphQLResponse | undefined | null;
  if (!parsedResponse) {
    throw Error("Request Error (bad response)");
  }

  const { data, errors } = parsedResponse;

  if (errors && errors instanceof Array && errors.length > 0) {
    // The GraphQL spec says that if errors is present, is must have at least 1 error.
    // So the length check here is just for safety.
    const operationMetadata = getGraphqlOperationMetadata(query.toString());
    // don't throw just because there were errors, would could still have partial data
    console.error(new GraphQLExecutionError({ operationName: operationMetadata?.operationName, errors }));
  }

  if (!data) {
    throw Error("Request Error (no data)");
  }

  const result = data as TResult;
  return result;
}

function getGraphqlOperationMetadata(graphqlDocument: string): GraphqlOperationMetadata | undefined {
  const m = graphqlDocument.match(/(mutation|query)\s+([a-zA-Z0-9_]+)/);
  if (!m) {
    return undefined;
  }

  let operationType: GraphQLOperationType | undefined;
  if (m[1] === "mutation" || m[1] === "query" || m[1] === "subscription") {
    operationType = m[1];
  }

  const operationName = m[2];

  return {
    operationType,
    operationName,
  };
}
