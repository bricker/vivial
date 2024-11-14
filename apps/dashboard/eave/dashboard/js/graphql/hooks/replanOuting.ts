import { useState } from "react";
import { NetworkState } from "../../types/network";
import { GRAPHQL_API_BASE } from "../../util/http";
import query from "../mutation/replanOuting.graphql";

type ReplanOutingRequest = {
  visitorId: string;
  outingId: string;
};

type ReplanOutingResponse = {
  outingId: string;
};

type ReplanOutingNetworkState = NetworkState & {
  data?: ReplanOutingResponse;
};

type ReplanOutingEncapsulation = {
  execute: ({ req, ctx }: { req: ReplanOutingRequest; ctx: ReplanOutingEncapsulation }) => void;
  networkState: [ReplanOutingNetworkState, React.Dispatch<React.SetStateAction<ReplanOutingNetworkState>>];
};

export type ReplanOutingCtx = { replanOuting?: ReplanOutingEncapsulation };

function replanOutingExecute({ req, ctx }: { req: ReplanOutingRequest; ctx: ReplanOutingEncapsulation }): void {
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
      variables: { input: req },
    }),
  })
    .then((resp) => {
      return resp.json();
    })
    .then((data) => {
      // handle gql error
      if (data.__typename === "ReplanOutingError" || data.data === null) {
        throw new Error(data.data?.replanOuting?.errorCode || "INTERNAL_SERVER_ERROR");
      }

      setNetworkState((prev) => ({
        ...prev,
        data: { outingId: data.data.replanOuting.outing.id },
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

export function replanOuting(): ReplanOutingCtx {
  return {
    replanOuting: {
      execute: replanOutingExecute,
      networkState: useState<ReplanOutingNetworkState>({
        loading: false,
      }),
    },
  };
}
