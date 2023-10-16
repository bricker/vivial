// @ts-check
import { useContext } from "react";
import {
  DOC_TYPES,
  FEATURE_STATE_PROPERTY,
  FEATURE_STATES,
} from "../constants.js";
import { AppContext } from "../context/Provider.js";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars
import { sortAPIDocuments } from "../util/document-util.js";
import { isHTTPError } from "../util/http-util.js";

/** @returns {{team: Types.DashboardTeam, getTeam: any, getTeamRepos: any, getTeamAPIDocs: any, getTeamFeatureStates: any, updateTeamFeatureState: any}} */
const useTeam = () => {
  const { teamCtx } = useContext(AppContext);
  /** @type {[Types.DashboardTeam, (f: (prev: Types.DashboardTeam) => Types.DashboardTeam) => void]} */
  const [team, setTeam] = teamCtx;

  async function getTeam() {
    setTeam((prev) => ({
      ...prev,
      teamIsLoading: true,
      teamIsErroring: false,
    }));
    fetch("/dashboard/team", { method: "POST" })
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp.json().then((/** @type {Types.GetTeamResponseBody} */ data) => {
          setTeam((prev) => ({
            ...prev,
            id: data.team?.id,
            name: data.team?.name,
            integrations: data.integrations,
          }));
        });
      })
      .catch(() => {
        setTeam((prev) => ({
          ...prev,
          teamIsErroring: true,
          teamRequestHasSucceededAtLeastOnce: true, // continue to show the table even if a subsequent request failed.
        }));
      })
      .finally(() => {
        setTeam((prev) => ({ ...prev, teamIsLoading: false }));
      });
  }

  async function getTeamRepos() {
    setTeam((prev) => ({
      ...prev,
      reposAreLoading: true,
      reposAreErroring: false,
    }));
    fetch("/dashboard/team/repos", { method: "POST" })
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp
          .json()
          .then((/** @type {Types.GetGithubReposResponseBody} */ data) => {
            setTeam((prev) => ({
              ...prev,
              repos: data.repos,
              reposRequestHasSucceededAtLeastOnce: true, // continue to show the table even if a subsequent request failed.
            }));
          });
      })
      .catch(() => {
        setTeam((prev) => ({ ...prev, reposAreErroring: true }));
      })
      .finally(() => {
        setTeam((prev) => ({ ...prev, reposAreLoading: false }));
      });
  }

  async function getTeamFeatureStates(
    /**@type {Types.GithubRepo[] | undefined}*/ repos,
  ) {
    if (!repos) {
      return;
    }
    setTeam((prev) => ({ ...prev, featureStatesLoading: true }));
    let inlineCodeDocsEnabled = false;
    let apiDocsEnabled = false;
    for (const repo of repos) {
      if (repo[FEATURE_STATE_PROPERTY.API_DOCS] === FEATURE_STATES.ENABLED) {
        apiDocsEnabled = true;
      }
      if (
        repo[FEATURE_STATE_PROPERTY.INLINE_CODE_DOCS] === FEATURE_STATES.ENABLED
      ) {
        inlineCodeDocsEnabled = true;
      }
    }
    setTeam((prev) => ({
      ...prev,
      featureStatesLoading: false,
      featureStatesRequestHasSucceededAtLeastOnce: true,
      inlineCodeDocsEnabled,
      apiDocsEnabled,
    }));
  }

  async function updateTeamFeatureState(
    /**@type {Types.FeatureStateParams} */ {
      teamRepoIds,
      enabledRepoIds,
      feature,
    },
  ) {
    setTeam((prev) => ({
      ...prev,
      featureStatesLoading: true,
      featureStatesErroring: false,
    }));
    /** @type {Types.GithubRepoUpdateInput[]} */
    const repos = teamRepoIds.map(
      /** @type {(repoId: string) => Types.GithubRepoUpdateInput} */ (
        repoId,
      ) => {
        const state = enabledRepoIds.includes(repoId)
          ? FEATURE_STATES.ENABLED
          : FEATURE_STATES.DISABLED;

        return {
          id: repoId,
          new_values: {
            [feature]: state,
          },
        };
      },
    );
    fetch("/dashboard/team/repos/update", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ repos }),
    })
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        getTeamRepos();
      })
      .catch(() => {
        setTeam((prev) => ({ ...prev, featureStatesErroring: true }));
      })
      .finally(() => {
        setTeam((prev) => ({ ...prev, featureStatesLoading: false }));
      });
  }

  async function getTeamAPIDocs() {
    setTeam((prev) => ({
      ...prev,
      apiDocsLoading: true,
      apiDocsErroring: false,
    }));
    fetch("/dashboard/team/documents", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ document_type: DOC_TYPES.API_DOC }),
    })
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp
          .json()
          .then((/**@type {Types.GetGithubDocumentsResponseBody}*/ data) => {
            setTeam((prev) => ({
              ...prev,
              apiDocs: sortAPIDocuments(data.documents),
              apiDocsRequestHasSucceededAtLeastOnce: true, // continue to show the table even if a subsequent request failed.
            }));
          });
      })
      .catch(() => {
        setTeam((prev) => ({ ...prev, apiDocsErroring: true }));
      })
      .finally(() => {
        setTeam((prev) => ({
          ...prev,
          apiDocsFetchCount: prev.apiDocsFetchCount + 1,
          apiDocsLoading: false,
        }));
      });
  }

  return {
    team,
    getTeam,
    getTeamRepos,
    getTeamAPIDocs,
    getTeamFeatureStates,
    updateTeamFeatureState,
  };
};

export default useTeam;
