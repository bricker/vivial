import { GraphQLExecutionError } from "../types/network";
import { CORE_API_BASE, GRAPHQL_API_BASE } from "../util/http";
import {
  AuthenticationFailureReason,
  type TypedDocumentString,
  type ViewerMutations,
  type ViewerQueries,
} from "./generated/graphql";

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

function isViewerOperation(data: any): data is { viewer: ViewerMutations | ViewerQueries } {
  return !!data && "viewer" in data;
}

async function refreshTokens() {
  const response = await fetch(`${CORE_API_BASE}/public/refresh_tokens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }, // this endpoint doesn't actually accept any input, but no harm in setting this header.
    credentials: "include", // This is required so that the cookies are sent to the subdomain (api.)
  });

  if (response.ok) {
    return;
  } else {
    throw Error(`Refresh tokens failed (${response.status})`);
  }
}

export async function executeOperation<TResult, TVariables>({
  query,
  variables,
  allowTokenRefresh = true,
}: {
  query: TypedDocumentString<TResult, TVariables>;
  variables: TVariables;
  allowTokenRefresh?: boolean;
}): Promise<TResult> {
  const response = await fetch(GRAPHQL_API_BASE, {
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
    throw new GraphQLExecutionError({ operationName: operationMetadata?.operationName, errors });
  }

  if (!data) {
    throw Error("Request Error (no data)");
  }

  const result = data as TResult;

  if (isViewerOperation(result) && result.viewer.__typename === "UnauthenticatedViewer") {
    if (result.viewer.authFailureReason) {
      switch (result.viewer.authFailureReason) {
        case AuthenticationFailureReason.AccessTokenExpired: {
          if (allowTokenRefresh) {
            await refreshTokens();
            return executeOperation({ query, variables, allowTokenRefresh: false });
          } else {
            // In this case, we throw an error because we don't want the UI to see `ACCESS_TOKEN_EXPIRED` and think
            // it needs to do something about that. If we already tried refreshing the token and the request failed again,
            // then it should be treated as an error.
            throw Error("Token refresh already attempted.");
          }
        }
        case AuthenticationFailureReason.AccessTokenInvalid: {
          // Do nothing (return the data as-is); this case is here just for reference.
          // The caller should handle this case, usually by calling dispatch(loggedOut())
          break;
        }
        default: {
          // It's unsafe to do anything here, because if an enum case is added to the GraphQL schema, we can't assume
          // what we should do. So we'll just return the data as-is and let the UI handle it.
        }
      }
    }
  }

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
