import { useState } from "react";
import { NetworkState } from "../types";
import { GRAPHQL_API_BASE } from "../util/http-util";

type SurveySubmitRequest = {
  visitorId: string;
  startTime: Date;
  searchAreaIds: Array<string>;
  budget: number;
  headcount: number;
};
type SurveySubmitResponse = {
  outingId: string;
};

function surveySubmitExecute({req, ctx}: { req: SurveySubmitRequest, ctx: SurveySubmitEncapsulation}): void {
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
  submitSurvey(
    visitorId: "${req.visitorId}",
    startTime: "${req.startTime.toISOString()}",
    searchAreaIds: ${JSON.stringify(req.searchAreaIds)},
    budget: ${req.budget},
    headcount: ${req.budget}) {
    __typename
    ... on SurveySubmitSuccess {
      outing {
        id
      }
    }
    ... on SurveySubmitError {
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
      if (data.__typename === "SurveySubmitError" || data.data === null) {
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

type SurveySubmitNetworkState = NetworkState & {
  data?: SurveySubmitResponse;
};

type SurveySubmitEncapsulation = {
  execute: ({req, ctx}: { req: SurveySubmitRequest, ctx: SurveySubmitEncapsulation}) => void;
  networkState: [SurveySubmitNetworkState, React.Dispatch<React.SetStateAction<SurveySubmitNetworkState>>];
};

export type SurveySubmitCtx = { submitSurvey?: SurveySubmitEncapsulation };
// must be a function so that useState isnt invoked in global scope
export function submitSurvey(): SurveySubmitCtx {
  return {
    submitSurvey: {
      execute: surveySubmitExecute,
      networkState: useState<SurveySubmitNetworkState>({
        loading: false,
      }),
    },
  };
}
