import { useState } from "react";
import { NetworkState } from "../../types/network";
import {
  ReplanOutingDocument,
  type ReplanOutingMutation,
  type ReplanOutingMutationVariables,
} from "../generated/graphql";
import { executeOperation, type GraphQLOperation } from "../graphql-fetch";

type ReplanOutingNetworkState = NetworkState<ReplanOutingMutation>;

export type ReplanOutingOperation = GraphQLOperation<ReplanOutingNetworkState, ReplanOutingMutationVariables>;

export function makeReplanOutingOperation(): ReplanOutingOperation {
  return {
    execute: async function (variables: ReplanOutingMutationVariables) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      try {
        const data = await executeOperation({ query: ReplanOutingDocument, variables });
        const result = data.replanOuting;

        switch (result.__typename) {
          case "ReplanOutingSuccess": {
            setNetworkState((prev) => ({
              ...prev,
              data,
            }));

            break;
          }
          case "ReplanOutingFailure": {
            // failure
            throw Error(result.failureReason);
          }

          default: {
            throw Error("unexpected result type");
          }
        }
      } catch (error: any) {
        setNetworkState((prev) => ({
          ...prev,
          error,
        }));
      } finally {
        setNetworkState((prev) => ({
          ...prev,
          loading: false,
        }));
      }
    },
    networkState: useState<ReplanOutingNetworkState>({
      loading: false,
    }),
  };
}
