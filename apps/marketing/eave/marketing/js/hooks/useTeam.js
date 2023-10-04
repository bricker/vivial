import { useContext } from "react";
import { FEATURES, FEATURE_STATES } from "../constants.js";
import { AppContext } from "../context/Provider.js";
import { isHTTPError } from "../util/http-util.js";

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
    let inlineCodeDocsState = FEATURE_STATES.DISABLED;
    let apiDocsState = FEATURE_STATES.DISABLED;
    let architectureDocsState = FEATURE_STATES.DISABLED;
    for (const repo of repos) {
      if (repo[FEATURES.API_DOCS] === FEATURE_STATES.ENABLED) {
        apiDocsState = FEATURE_STATES.ENABLED;
      }
      if (repo[FEATURES.INLINE_CODE_DOCS] === FEATURE_STATES.ENABLED) {
        inlineCodeDocsState = FEATURE_STATES.ENABLED;
      }
      if (repo[FEATURES.ARCHITECTURE_DOCS] === FEATURE_STATES.ENABLED) {
        architectureDocsState = FEATURE_STATES.ENABLED;
      }
    }
    setTeam((prev) => ({
      ...prev,
      featureStatesLoading: false,
      inlineCodeDocsState,
      apiDocsState,
      architectureDocsState,
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

  return {
    team,
    getTeam,
    getTeamRepos,
    getTeamFeatureStates,
    updateTeamFeatureState,
  };
};

export default useTeam;
