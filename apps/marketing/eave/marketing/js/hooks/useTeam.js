import { useContext } from "react";
import { DOC_TYPES, FEATURES, FEATURE_STATES } from "../constants.js";
import { AppContext } from "../context/Provider.js";
import { isHTTPError } from "../util/http-util.js";
import { sortAPIDocuments } from "../util/document-util.js";

const useTeam = () => {
  const { teamCtx } = useContext(AppContext);
  const [team, setTeam] = teamCtx;

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
        resp.json().then((data) => {
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
        resp.json().then((data) => {
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

  async function getTeamFeatureStates(repos) {
    setTeam((prev) => ({ ...prev, featureStatesLoading: true }));
    let inlineCodeDocsEnabled = false;
    let apiDocsEnabled = false;
    for (const repo of repos) {
      if (repo[FEATURES.API_DOCS] === FEATURE_STATES.ENABLED) {
        apiDocsEnabled = true;
      }
      if (repo[FEATURES.INLINE_CODE_DOCS] === FEATURE_STATES.ENABLED) {
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

  async function updateTeamFeatureState({
    teamRepoIds,
    enabledRepoIds,
    feature,
  }) {
    setTeam((prev) => ({
      ...prev,
      featureStatesLoading: true,
      featureStatesErroring: false,
    }));
    const repos = teamRepoIds.map((repoId) => {
      const state = enabledRepoIds.includes(repoId)
        ? FEATURE_STATES.ENABLED
        : FEATURE_STATES.DISABLED;
      return {
        external_repo_id: repoId,
        new_values: {
          [feature]: state,
        },
      };
    });
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
    fetch('/dashboard/team/documents', {
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
        resp.json().then((data) => {
          setTeam((prev) => ({
            ...prev,
            apiDocs: sortAPIDocuments(data.documents),
          }));
        });
      })
      .catch((e) => {
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
