import { useState } from "react";
import { NetworkState } from "../../types/network";
import { GRAPHQL_API_BASE } from "../../util/http";
import query from "../mutation/createPaymentIntent.graphql";

type CreatePaymentIntentRequest = {
  placeholder: string;
};

type CreatePaymentIntentResponse = {
  data?: {
    viewer: {
      payment: {
        createPaymentIntent: {
          __typename: string;
          paymentIntent?: {
            clientSecret?: string;
          };
          failureReason?: string;
        };
      };
    };
  };
  errors?: any[];
};

type CreatePaymentIntentNetworkState = NetworkState & CreatePaymentIntentResponse;

export type CreatePaymentIntentCtx = {
  execute: ({ req }: { req: CreatePaymentIntentRequest }) => void;
  networkState: [
    CreatePaymentIntentNetworkState,
    React.Dispatch<React.SetStateAction<CreatePaymentIntentNetworkState>>,
  ];
};

export function createCreatePaymentIntentCtx(): CreatePaymentIntentCtx {
  return {
    execute: function ({ req }: { req: CreatePaymentIntentRequest }) {
      const [, setNetworkState] = this.networkState;
      setNetworkState({
        loading: true,
        error: undefined,
        data: undefined,
      });

      fetch(GRAPHQL_API_BASE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          variables: { input: req },
        }),
      })
        .then((resp) => {
          return resp.json();
        })
        .then((resp: CreatePaymentIntentResponse) => {
          console.log(resp);
          const failureReason = resp.data?.viewer.payment.createPaymentIntent.failureReason;
          if (resp.errors) {
            console.error(resp.errors);
            throw new Error("GraphQL errors");
          } else if (failureReason) {
            throw new Error(failureReason);
          } else {
            setNetworkState((prev) => ({
              ...prev,
              data: resp.data,
            }));
          }
        })
        .catch((error) => {
          setNetworkState((prev) => ({
            ...prev,
            error,
          }));
        })
        .finally(() => {
          setNetworkState((prev) => ({
            ...prev,
            loading: false,
          }));
        });
    },
    networkState: useState<CreatePaymentIntentNetworkState>({
      loading: false,
    }),
  };
}
