import { useState } from "react";
import { NetworkState } from "../../types";
import { GRAPHQL_API_BASE } from "../../util/http-util";
import query from "../mutation/submitSurvey.graphql";

type SubmitSurveyRequest = {
  visitorId: string;
  startTime: Date;
  searchAreaIds: Array<string>;
  budget: number;
  headcount: number;
};

type SubmitSurveyResponse = {
  outingId: string;
};

type SubmitSurveyNetworkState = NetworkState & {
  data?: SubmitSurveyResponse;
};

type SubmitSurveyEncapsulation = {
  execute: ({ req, ctx }: { req: SubmitSurveyRequest; ctx: SubmitSurveyEncapsulation }) => void;
  networkState: [SubmitSurveyNetworkState, React.Dispatch<React.SetStateAction<SubmitSurveyNetworkState>>];
};

export type SubmitSurveyCtx = { submitSurvey?: SubmitSurveyEncapsulation };

function submitSurveyExecute({ req, ctx }: { req: SubmitSurveyRequest; ctx: SubmitSurveyEncapsulation }): void {
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
      variables: {
        input: {
          ...req,
          startTime: req.startTime.toISOString(),
        },
      },
    }),
  })
    .then((resp) => {
      return resp.json();
    })
    .then((data) => {
      // handle gql error
      if (data.__typename === "SubmitSurveyError" || data.data === null) {
        throw new Error(data?.data?.submitSurvey?.errorCode || "INTERNAL_SERVER_ERROR");
      }

      setNetworkState((prev) => ({
        ...prev,
        data: { outingId: data.data.submitSurvey.outing.id },
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

// must be a function so that useState isnt invoked in global scope
export function submitSurvey(): SubmitSurveyCtx {
  return {
    submitSurvey: {
      execute: submitSurveyExecute,
      networkState: useState<SubmitSurveyNetworkState>({
        loading: false,
      }),
    },
  };
}
