import { useContext, useState } from "react";
import { AppContext } from "../context/AppContext";
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

function surveySubmitExecute(req: SurveySubmitRequest): void {
  const { submitSurvey } = useContext(AppContext);
  const [, setNetworkState] = submitSurvey!.networkState;

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
    searchAreaIds: ${req.searchAreaIds}, 
    budget: ${req.budget}, 
    headcount: ${req.budget}) {
    __typename
    ... on SurveySubmitSuccess {
      outing {
        id
      }
    }
    ... on SurveySubmitError {
      error_code
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
      if (data.__typename === "SurveySubmitError" || data.data === undefined) {
        throw new Error(data?.data?.error_code || "INTERNAL_SERVER_ERROR");
      }

      setNetworkState((prev) => ({
        ...prev,
        data: { outingId: data.data.outing.id },
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
  execute: (req: SurveySubmitRequest) => void;
  networkState: [SurveySubmitNetworkState, React.Dispatch<React.SetStateAction<SurveySubmitNetworkState>>];
};

export type SurveySubmitCtx = { submitSurvey?: SurveySubmitEncapsulation };
// must be a function so that useState isnt invoked in global scope
export const submitSurvey = () => ({
  submitSurvey: {
    execute: surveySubmitExecute,
    networkState: useState<SurveySubmitNetworkState>({
      loading: false,
    }),
  },
});
