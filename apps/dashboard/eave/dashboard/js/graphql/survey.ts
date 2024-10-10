import { useContext, useState } from "react";
import { AppContext } from "../context/AppContext";
import { NetworkState } from "../types";
import { GRAPHQL_API_BASE, isHTTPError } from "../util/http-util";

type SurveySubmitRequest = {}; // TODO:
type SurveySubmitResponse = {};

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
      query: `
        {
          launchesPast(limit: 10) {
            id
            mission_name
          }
        }
      `, // TODO: real gql. load from somewhere?
    }),
  })
    .then((resp) => {
      if (isHTTPError(resp)) {
        // TODO: proper error from response? does gql even return http error codes properly?
        throw new Error(`${resp.status} ERROR`);
      } else {
        return resp.json();
      }
    })
    .then((data) => {
      setNetworkState((prev) => ({
        ...prev,
        data: data.data,
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
export const submitSurvey: SurveySubmitCtx = {
  submitSurvey: {
    execute: surveySubmitExecute,
    networkState: useState<SurveySubmitNetworkState>({
      loading: false,
    }),
  },
};
