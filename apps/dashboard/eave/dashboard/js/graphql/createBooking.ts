import { useState } from "react";
import { NetworkState } from "../types";
import { GRAPHQL_API_BASE } from "../util/http-util";

type CreateBookingRequest = {
  accountId: string;
  outingId: string;
  reserverDetailsId: string;
};
type CreateBookingResponse = {
  bookingId: string;
};

type CreateBookingNetworkState = NetworkState & {
  data?: CreateBookingResponse;
};

type CreateBookingEncapsulation = {
  execute: ({ req, ctx }: { req: CreateBookingRequest; ctx: CreateBookingEncapsulation }) => void;
  networkState: [CreateBookingNetworkState, React.Dispatch<React.SetStateAction<CreateBookingNetworkState>>];
};

export type CreateBookingCtx = { createBooking?: CreateBookingEncapsulation };

function createBookingExecute({ req, ctx }: { req: CreateBookingRequest; ctx: CreateBookingEncapsulation }): void {
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
      query: `mutation {
  createBooking(
    accountId: "${req.accountId}",
    outingId: "${req.outingId}",
    reserverDetailsId: "${req.reserverDetailsId}") {
    __typename
    ... on CreateBookingSuccess {
      booking {
        id
      }
    }
    ... on CreateBookingError {
      errorCode
    }
  }
}`,
    }),
  })
    .then((resp) => {
      return resp.json();
    })
    .then((data) => {
      // handle gql error
      if (data.__typename === "CreateBookingError" || data.data === null) {
        throw new Error(data?.data?.createBooking?.errorCode || "INTERNAL_SERVER_ERROR");
      }

      setNetworkState((prev) => ({
        ...prev,
        data: { bookingId: data.data.createBooking.booking.id },
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

export function createBooking(): CreateBookingCtx {
  return {
    createBooking: {
      execute: createBookingExecute,
      networkState: useState<CreateBookingNetworkState>({
        loading: false,
      }),
    },
  };
}
