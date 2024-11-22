import { useState } from "react";
import { NetworkState } from "../../types/network";
import { PlanOutingDocument, type PlanOutingMutation, type PlanOutingMutationVariables } from "../generated/graphql";
import { executeOperation, type GraphQLOperation } from "../graphql-fetch";

type PlanOutingNetworkState = NetworkState<PlanOutingMutation>;

export type PlanOutingOperation = GraphQLOperation<PlanOutingNetworkState, PlanOutingMutationVariables>;

export function makePlanOutingOperation(): PlanOutingOperation {
  return {
    execute: async function (variables: PlanOutingMutationVariables) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      try {
        const data = await executeOperation({ query: PlanOutingDocument, variables });
        const result = data.planOuting;

        switch (result.__typename) {
          case "PlanOutingSuccess": {
            setNetworkState((prev) => ({
              ...prev,
              data,
            }));

            break;
          }
          case "PlanOutingFailure": {
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
    networkState: useState<PlanOutingNetworkState>({
      loading: false,
    }),
  };
}
