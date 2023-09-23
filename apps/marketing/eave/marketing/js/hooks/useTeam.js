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




  // TODO: Fetch real data from Github App.
  async function getTeamAccessibleRepos(teamId) {
    setTeam((prev) => ({ ...prev, accessibleReposAreLoading: true, accessibleReposAreErroring: false}));
    const accessibleRepos = [
      {id: '1234', name: "Transactional Third Party"},
      {id: '5678', name: "Payments Point of Sales"},
      {id: '9101', name: "Returns"},
      {id: '1213', name: "Sales Tax"},
    ];
    setTeam((prev) => ({ ...prev, accessibleRepos, accessibleReposAreLoading: false}));
  };





  async function getTeamFeatureStates(repos) {
    setTeam((prev) => ({...prev, featureStatesAreLoading: true}));
    const featureStates = {
      [FEATURES.API_DOCS]: FEATURE_STATES.DISABLED,
      [FEATURES.INLINE_CODE_DOCS]: FEATURE_STATES.DISABLED,
      [FEATURES.ARCHITECTURE_DOCS]: FEATURE_STATES.DISABLED,
    }
    for (const repo of repos) {
      if (repo[`${FEATURES.API_DOCS}_state`] === FEATURE_STATES.ENABLED) {
        states[FEATURES.API_DOCS] = FEATURE_STATES.ENABLED;
      }
      if (repo[`${FEATURES.INLINE_CODE_DOCS}_state`] === FEATURE_STATES.ENABLED) {
        states[FEATURES.INLINE_CODE_DOCS] = FEATURE_STATES.ENABLED;
      }
      if (repo[`${FEATURES.ARCHITECTURE_DOCS}_state`] === FEATURE_STATES.ENABLED) {
        states[FEATURES.ARCHITECTURE_DOCS] = FEATURE_STATES.ENABLED;
      }
    }
    setTeam((prev) => ({...prev, featureStates, featureStatesAreLoading: false }));
  }

  return {
    team,
    getTeam,
    getTeamRepos,
    getTeamFeatureStates,
    getTeamAccessibleRepos,
  };
};

export default useTeam;
