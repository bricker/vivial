import { useState } from "react";
import { NetworkState, GraphQLExecutionError } from "../../types/network";
import { CreateBookingDocument, CreateBookingSuccess, type CreateBookingFailureReason, type CreateBookingMutation, type CreateBookingMutationVariables, type ValidationError} from "../generated/graphql";
import { executeOperation, type GraphQLOperation } from "../graphql-fetch.js";

type CreateBookingNetworkState = NetworkState<CreateBookingMutation>;

export type CreateBookingOperation = GraphQLOperation<CreateBookingNetworkState, CreateBookingMutationVariables>;

export function makeCreateBookingOperation(): CreateBookingOperation {
  return {
    execute: async function (variables: CreateBookingMutationVariables) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      try {
        const data = await executeOperation({ query: CreateBookingDocument, variables });
        const result = data.viewer.createBooking;

        switch (result.__typename) {
          case "CreateBookingSuccess": {
            setNetworkState((prev) => ({
              ...prev,
              data,
            }));

            break;
          }
          case "CreateBookingFailure": {
            // failure
            throw Error(result.failureReason);
            break;
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
    networkState: useState<CreateBookingNetworkState>({
      loading: false,
    }),
  };
}
