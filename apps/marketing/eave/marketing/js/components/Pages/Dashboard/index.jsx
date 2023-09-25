import React, { useCallback, useEffect, useState } from 'react';
import { useCookies } from 'react-cookie';
import { useSearchParams } from 'react-router-dom';
import useUser from '../../../hooks/useUser.js';
import useTeam from '../../../hooks/useTeam.js';

import { FEATURES, FEATURE_STATES, COOKIE_NAMES, SEARCH_PARAM_NAMES, SEARCH_PARAM_VALUES } from '../../../constants.js';
import ExploreFeatures from '../../ExploreFeatures/index.jsx';
import FeatureSettings from '../../FeatureSettings/index.jsx';
import GitHubFeatureModal from '../../GitHubFeatureModal/index.jsx';
import ErrorPage from '../ErrorPage/index.jsx';
import LoadingPage from '../LoadingPage/index.jsx';
import Page from '../Page/index.jsx';


const Dashboard = () => {
  const [cookies, _, removeCookie] = useCookies([COOKIE_NAMES.FEATURE_MODAL]);
  const [searchParams] = useSearchParams();
  const {
    user,
    getUserAccount
  } = useUser();
  const {
    team,
    getTeam,
    getTeamRepos,
    getTeamFeatureStates,
    updateTeamFeatureState,
  } = useTeam();

  const isLoading =
    user.accountIsLoading
    || team.teamIsLoading
    || team.reposAreLoading
    || team.featureStatesLoading;

  const isErroring =
    user.accountIsErroring
    || team.teamIsErroring
    || team.reposAreErroring
    || team.featureStatesErroring;

  const showFeatureSettings =
    team.inlineCodeDocsState === FEATURE_STATES.ENABLED
    || team.apiDocsState === FEATURE_STATES.ENABLED;

  const [inlineDocsModalIsOpen, setInlineDocsModalIsOpen] = useState(false);

  const openInlineDocsModal = useCallback(() => {
    setInlineDocsModalIsOpen(true);
  }, []);

  const closeInlineDocsModal = useCallback(() => {
    setInlineDocsModalIsOpen(false);
  }, []);

  const handleUpdateFeatureState = useCallback((teamId, teamRepoIds, enabledRepoIds, feature) => {
    updateTeamFeatureState(
      teamId,
      teamRepoIds,
      enabledRepoIds,
      feature,
    );
    closeInlineDocsModal();
  }, []);

  useEffect(() => {
    getUserAccount();
  }, []);

  useEffect(() => {
    const teamId = user.account.team_id;
    if (teamId) {
      getTeam(teamId);
      getTeamRepos(teamId);
    }
  }, [user.account.team_id]);

  useEffect(() => {
    getTeamFeatureStates(team.repos);
  }, [team.repos]);

  useEffect(() => {
    const openFeature = cookies && cookies[COOKIE_NAMES.FEATURE_MODAL];
    if (openFeature) {
      if (openFeature === FEATURES.INLINE_CODE_DOCS) {
        openInlineDocsModal();
      }
      removeCookie(COOKIE_NAMES.FEATURE_MODAL);
    }
  }, [cookies]);

  useEffect(() => {
    const openFeature = searchParams.get(SEARCH_PARAM_NAMES.FEATURE_MODAL);
    if (openFeature === SEARCH_PARAM_VALUES.INLINE_CODE_DOCS) {
      openInlineDocsModal();
    }
  }, [searchParams]);

  if (isLoading) {
    return <LoadingPage />;
  }
  if (isErroring) {
    return <ErrorPage page="dashboard" />
  }
  return (
    <Page>
      <ExploreFeatures onInlineDocsClick={openInlineDocsModal} />
      {showFeatureSettings && (
        <FeatureSettings onInlineDocsClick={openInlineDocsModal} />
      )}
      {inlineDocsModalIsOpen && (
        <GitHubFeatureModal
          feature={FEATURES.INLINE_CODE_DOCS}
          param={SEARCH_PARAM_VALUES.INLINE_CODE_DOCS}
          onClose={closeInlineDocsModal}
          onUpdate={handleUpdateFeatureState}
          open
        />
      )}
    </Page>
  );
};

export default Dashboard;
