import { useContext } from 'react';
import { AppContext } from '../context/Provider.js';

import { FEATURES, FEATURE_STATES } from '../constants.js';

const useTeam = () => {
  const { teamCtx } = useContext(AppContext);
  const [team, setTeam] = teamCtx;

  async function getTeam(teamId) {
    setTeam((prev) => ({...prev, teamIsLoading: true, teamIsErroring: false}));
    fetch(`dashboard/team/${teamId}`)
      .then((resp) => {
        resp.json().then((data) => {
          setTeam((prev) => ({
            ...prev,
            id: data.team?.id,
            name: data.team?.name,
            integrations: data.integrations,
          }));
        });
      }).catch(() => {
        setTeam((prev) => ({...prev, teamIsErroring: true}));
      }).finally(() => {
        setTeam((prev) => ({...prev, teamIsLoading: false}));
      });
  }

  async function getTeamRepos(teamId) {
    setTeam((prev) => ({...prev, reposAreLoading: true, reposAreErroring: false}));
    fetch(`dashboard/team/repos/${teamId}`)
      .then((resp) => {
        resp.json().then((data) => {
          setTeam((prev) => ({...prev, repos: data.repos}));
        });
      }).catch(() => {
        setTeam((prev) => ({...prev, reposAreErroring: true}));
      }).finally(() => {
        setTeam((prev) => ({...prev, reposAreLoading: false}));
      });
  }

  async function getTeamFeatureStates(repos) {
    setTeam((prev) => ({...prev, featureStatesLoading: true}));
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

  async function updateTeamFeatureState(teamId, teamRepoIds, enabledRepoIds, feature) {
    setTeam((prev) => ({...prev, featureStatesLoading: true, featureStatesErroring: false}));
    const repoUpdates = teamRepoIds.map((repoId) => {
      const state = enabledRepoIds.includes(repoId) ? FEATURE_STATES.ENABLED : FEATURE_STATES.DISABLED;
      return ({
        external_repo_id: repoId,
        new_values: {
          [feature]: state,
        }
      });
    });
    fetch('/dashboard/team/repos/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        team_id: teamId,
        repos: repoUpdates,
      }),
    })
    .then(() => {
      getTeamRepos(teamId);
    })
    .catch(() => {
      setTeam((prev) => ({...prev, featureStatesErroring: true}));
    })
    .finally(() => {
      setTeam((prev) => ({...prev, featureStatesLoading: false}));
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
