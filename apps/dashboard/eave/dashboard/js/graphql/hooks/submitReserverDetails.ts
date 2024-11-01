import { useState } from "react";
import { NetworkState } from "../../types";
import { GRAPHQL_API_BASE } from "../../util/http-util";
import query from "../mutation/submitReserverDetails.graphql";

type SubmitReserverDetailsRequest = {
  accountId: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
};

type SubmitReserverDetailsResponse = {
  reserverDetailsId: string;
};

type SubmitReserverDetailsNetworkState = NetworkState & {
  data?: SubmitReserverDetailsResponse;
};

type SubmitReserverDetailsEncapsulation = {
  execute: ({ req, ctx }: { req: SubmitReserverDetailsRequest; ctx: SubmitReserverDetailsEncapsulation }) => void;
  networkState: [
    SubmitReserverDetailsNetworkState,
    React.Dispatch<React.SetStateAction<SubmitReserverDetailsNetworkState>>,
  ];
};

export type SubmitReserverDetailsCtx = { submitReserverDetails?: SubmitReserverDetailsEncapsulation };

function submitReserverDetailsExecute({
  req,
  ctx,
}: {
  req: SubmitReserverDetailsRequest;
  ctx: SubmitReserverDetailsEncapsulation;
}): void {
  const [, setNetworkState] = ctx.networkState;

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
      variables: req,
    }),
  })
    .then((resp) => {
      return resp.json();
    })
    .then((data) => {
      // handle gql error
      if (data.__typename === "SubmitReserverDetailsError" || data.data === null) {
        throw new Error(data?.data?.submitReserverDetails?.errorCode || "INTERNAL_SERVER_ERROR");
      }

      setNetworkState((prev) => ({
        ...prev,
        data: { reserverDetailsId: data.data.submitReserverDetails.reserverDetails.id },
      }));
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
}

export function submitReserverDetails(): SubmitReserverDetailsCtx {
  return {
    submitReserverDetails: {
      execute: submitReserverDetailsExecute,
      networkState: useState<SubmitReserverDetailsNetworkState>({
        loading: false,
      }),
    },
  };
}
