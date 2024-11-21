import { useState } from "react";
import { NetworkState } from "../../types/network";
import {
  CreatePaymentIntentDocument,
  type CreatePaymentIntentMutation,
  type CreatePaymentIntentMutationVariables,
} from "../generated/graphql";
import { executeOperation, type GraphQLOperation } from "../graphql-fetch";

type CreatePaymentIntentNetworkState = NetworkState<CreatePaymentIntentMutation>;

export type CreatePaymentIntentOperation = GraphQLOperation<
  CreatePaymentIntentNetworkState,
  CreatePaymentIntentMutationVariables
>;

export function makeCreatePaymentIntentOperation(): CreatePaymentIntentOperation {
  return {
    execute: async function (variables: CreatePaymentIntentMutationVariables) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      try {
        const data = await executeOperation({ query: CreatePaymentIntentDocument, variables });
        const result = data.viewer.createPaymentIntent;

        switch (result.__typename) {
          case "CreatePaymentIntentSuccess": {
            setNetworkState((prev) => ({
              ...prev,
              data,
            }));

            break;
          }
          case "CreatePaymentIntentFailure": {
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
    networkState: useState<CreatePaymentIntentNetworkState>({
      loading: false,
    }),
  };
}
