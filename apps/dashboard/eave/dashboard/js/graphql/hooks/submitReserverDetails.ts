import { useState } from "react";
import { NetworkState } from "../../types/network";
import {
  SubmitReserverDetailsDocument,
  type SubmitReserverDetailsMutation,
  type SubmitReserverDetailsMutationVariables,
} from "../generated/graphql";
import { executeOperation, type GraphQLOperation } from "../graphql-fetch";

type SubmitReserverDetailsNetworkState = NetworkState<SubmitReserverDetailsMutation>;

export type SubmitReserverDetailsOperation = GraphQLOperation<
  SubmitReserverDetailsNetworkState,
  SubmitReserverDetailsMutationVariables
>;

export function makeSubmitReserverDetailsOperation(): SubmitReserverDetailsOperation {
  return {
    execute: async function (variables: SubmitReserverDetailsMutationVariables) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      try {
        const data = await executeOperation({ query: SubmitReserverDetailsDocument, variables });
        const result = data.viewer.submitReserverDetails;

        switch (result.__typename) {
          case "SubmitReserverDetailsSuccess": {
            setNetworkState((prev) => ({
              ...prev,
              data,
            }));

            break;
          }
          case "SubmitReserverDetailsFailure": {
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
    networkState: useState<SubmitReserverDetailsNetworkState>({
      loading: false,
    }),
  };
}
