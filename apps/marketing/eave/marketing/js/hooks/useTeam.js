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
import { isHTTPError, isUnauthorized, logUserOut } from "../util/http-util.js";

/** @returns {{team: Types.DashboardTeam, getTeam: any, getTeamRepos: any, getTeamAPIDocs: any, getTeamFeatureStates: any, updateTeamFeatureState: any}} */
const useTeam = () => {
  const { teamCtx } = useContext(AppContext);
  /** @type {[Types.DashboardTeam, (f: (prev: Types.DashboardTeam) => Types.DashboardTeam) => void]} */
  const [team, setTeam] = teamCtx;

  /**
   * Asynchronously fetches team data from the "/dashboard/team" endpoint using a POST request.
   * Updates the team state with the fetched data, including team ID, name, and integrations.
   * Handles HTTP errors by setting the 'teamIsErroring' state to true.
   * Regardless of success or failure, sets 'teamIsLoading' state to false upon completion.
   */
  async function getTeam() {
    setTeam((prev) => ({
      ...prev,
      teamIsLoading: true,
      teamIsErroring: false,
    }));
    fetch("/dashboard/team", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
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

  /**
   * Asynchronously fetches the team's repositories from the server and updates the team state accordingly.
   * If the request is successful, the team's repositories are updated and a flag is set to indicate a successful request.
   * If the request fails, an error flag is set.
   * Regardless of the request outcome, the loading flag is reset at the end.
   */
  async function getTeamRepos() {
    setTeam((prev) => ({
      ...prev,
      reposAreLoading: true,
      reposAreErroring: false,
    }));
    fetch("/dashboard/team/repos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }

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

  /**
   * Asynchronously retrieves the feature states for a team based on the provided Github repositories.
   * It checks if API documentation and inline code documentation are enabled for each repository.
   * Updates the team's state with the loading status, success status, and the enabled features.
   *
   * @async
   * @function getTeamFeatureStates
   * @param {Types.GithubRepo[] | undefined} repos - The Github repositories to check for feature states.
   * @returns {void}
   */
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

  /**
   * Asynchronously updates the state of a feature for a team's repositories.
   * It sets the feature state to either enabled or disabled based on the provided parameters.
   * It also handles the loading and error states during the update process.
   *
   * @async
   * @function updateTeamFeatureState
   * @param {Types.FeatureStateParams} params - An object containing the parameters for the feature state update.
   * @param {string[]} params.teamRepoIds - An array of repository IDs associated with the team.
   * @param {string[]} params.enabledRepoIds - An array of repository IDs where the feature is enabled.
   * @param {string} params.feature - The feature to update the state for.
   * @throws {HTTPError} If the HTTP request fails.
   */
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
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
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

  /**
   * Asynchronously fetches API documentation from the server and updates the team state accordingly.
   * The state is initially set to loading, then updated with the fetched documents if the request is successful.
   * If the request fails, the state is updated to reflect the error.
   * Regardless of success or failure, the fetch count is incremented and the loading state is reset at the end.
   * The documents are sorted before being set in the state.
   * The state also keeps track of whether a request has succeeded at least once to continue showing the table even if a subsequent request fails.
   */
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
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
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
