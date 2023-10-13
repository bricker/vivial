// @ts-check
import { useContext } from "react";
import { DOC_TYPES, FEATURE_STATE_PROPERTY, FEATURE_STATES } from "../constants.js";
import { AppContext } from "../context/Provider.js";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars
import { sortAPIDocuments } from "../util/document-util.js";
import { isHTTPError } from "../util/http-util.js";

const useTeam = () => {
  const { teamCtx } = useContext(AppContext);
  /** @type {[Types.DashboardTeam, (f: (prev: Types.DashboardTeam) => Types.DashboardTeam) => void]} */
  const [team, setTeam] = teamCtx;

  /**
   * Asynchronously fetches team data from the "/dashboard/team" endpoint.
   * Updates the team state with the fetched data, or sets an error flag if the fetch fails.
   * Also manages loading state flags before and after the fetch operation.
   */
  async function getTeam() {
    setTeam((prev) => ({
      ...prev,
      teamIsLoading: true,
      teamIsErroring: false,
    }));
    fetch("/dashboard/team")
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
        setTeam((prev) => ({ ...prev, teamIsErroring: true }));
      })
      .finally(() => {
        setTeam((prev) => ({ ...prev, teamIsLoading: false }));
      });
  }

  /**
   * Asynchronously fetches the team's GitHub repositories from the server.
   * Updates the team state to indicate when repositories are loading, have loaded, or if an error occurred during loading.
   * @async
   * @function
   * @throws {Response} If the HTTP response indicates an error.
   */
  async function getTeamRepos() {
    setTeam((prev) => ({
      ...prev,
      reposAreLoading: true,
      reposAreErroring: false,
    }));
    fetch("/dashboard/team/repos")
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp
          .json()
          .then((/** @type {Types.GetGithubReposResponseBody} */ data) => {
            setTeam((prev) => ({ ...prev, repos: data.repos }));
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
   * The function updates the team's state to reflect the loading status and the enabled features.
   *
   * @async
   * @function getTeamFeatureStates
   * @param {Types.GithubRepo[] | undefined} repos - The Github repositories to check for feature states.
   * @returns {void} Updates the team's state but does not return a value.
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
      if (repo[FEATURE_STATE_PROPERTY.INLINE_CODE_DOCS] === FEATURE_STATES.ENABLED) {
        inlineCodeDocsEnabled = true;
      }
    }
    setTeam((prev) => ({
      ...prev,
      featureStatesLoading: false,
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
   * @param {Types.FeatureStateParams} params - The parameters for updating the feature state.
   * @param {string[]} params.teamRepoIds - The IDs of the team's repositories.
   * @param {string[]} params.enabledRepoIds - The IDs of the repositories where the feature is enabled.
   * @param {string} params.feature - The feature to update.
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
   * The state is updated to indicate the loading status before the fetch request, and upon receiving the response,
   * the state is updated with the fetched documents (sorted), or an error flag is set if the fetch fails.
   * Regardless of success or failure, the fetch count is incremented and the loading status is updated after the fetch.
   * The fetch request is made to the "/dashboard/team/documents" endpoint with a POST method,
   * and the body of the request specifies that the document type is API documentation.
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
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp
          .json()
          .then((/**@type {Types.GetGithubDocumentsResponseBody}*/ data) => {
            setTeam((prev) => ({
              ...prev,
              apiDocs: sortAPIDocuments(data.documents),
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
