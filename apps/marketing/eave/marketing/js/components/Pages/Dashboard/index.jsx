import React, { useCallback, useEffect, useState } from 'react';
import useUser from '../../../hooks/useUser.js';
import useTeam from '../../../hooks/useTeam.js';

import { FEATURES } from '../../../constants.js';
import ExploreFeatures from '../../ExploreFeatures/index.jsx';
import GitHubFeatureModal from '../../GitHubFeatureModal/index.jsx';
import ErrorPage from '../ErrorPage/index.jsx';
import LoadingPage from '../LoadingPage/index.jsx';
import Page from '../Page/index.jsx';


const Dashboard = () => {
  const {
    user,
    getUserAccount
  } = useUser();

  const {
    team,
    getTeam,
    getTeamRepos,
    getTeamFeatureStates,
    updateTeamFeatureState
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
    if (team.repos.length) {
      getTeamFeatureStates(team.repos);
    }
  }, [team.repos]);

  if (isLoading) {
    return <LoadingPage />;
  }
  if (isErroring) {
    return <ErrorPage page="dashboard" />
  }
  return (
    <Page>
      <ExploreFeatures onInlineDocsClick={openInlineDocsModal} />
      <GitHubFeatureModal
        feature={FEATURES.INLINE_CODE_DOCS}
        open={inlineDocsModalIsOpen}
        onClose={closeInlineDocsModal}
        onUpdate={handleUpdateFeatureState}
      />
    </Page>
  );
};

export default Dashboard;
