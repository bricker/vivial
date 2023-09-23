import React, { useCallback, useEffect, useState } from 'react';
import useUser from '../../../hooks/useUser.js';
import useTeam from '../../../hooks/useTeam.js';

import ExploreFeatures from '../../ExploreFeatures/index.jsx';
import GitHubFeatureModal from '../../GitHubFeatureModal/index.jsx';
import ErrorPage from '../ErrorPage/index.jsx';
import LoadingPage from '../LoadingPage/index.jsx';
import Page from '../Page/index.jsx';

const Dashboard = () => {
  const { user, getUserAccount } = useUser();
  const { team, getTeam, getTeamRepos, getTeamFeatureStates, getTeamAccessibleRepos } = useTeam();
  const teamId = user.account.team_id;

  const isLoading =
    user.accountIsLoading
    || team.teamIsLoading
    || team.reposAreLoading
    || team.featureStatesAreLoading
    || team.accessibleReposAreLoading;

  const isErroring =
    user.accountIsErroring
    || team.teamIsErroring
    || team.reposAreErroring
    || team.accessibleReposAreErroring;

  const [inlineDocsModalIsOpen, setInlineDocsModalIsOpen] = useState(true); // TODO: false

  const inlineDocsEnabledRepoIds = team.repos
    .filter(repo => repo.inline_code_documentation_state === "enabled")
    .map(repo => repo.id);

  const openInlineDocsModal = useCallback(() => {
    setInlineDocsModalIsOpen(true);
  }, []);

  const closeInlineDocsModal = useCallback(() => {
    setInlineDocsModalIsOpen(false);
  }, []);

  const turnOnInlineDocsFeature = useCallback((teamId, repoIds) => {
    console.log('turnOnInlineDocsFeature()');
    console.log(teamId);
    console.log(repoIds);
    // closeInlineDocsModal();
  }, []);

  useEffect(() => {
    getUserAccount();
  }, []);

  useEffect(() => {
    if (teamId) {
      getTeam(teamId);
      getTeamRepos(teamId);
      getTeamAccessibleRepos(teamId);
    }
  }, [teamId]);

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
        title="Inline Code Documentation"
        open={inlineDocsModalIsOpen}
        onClose={closeInlineDocsModal}
        onTurnOn={turnOnInlineDocsFeature}
        enabledRepoIds={inlineDocsEnabledRepoIds}
      >
        <p>Automate inline code documentation within your GitHub files.</p>
        <p>As changes are made to the codebase, Eave will automatically generate inline documentation via a pull request for your team's review.</p>
      </GitHubFeatureModal>
    </Page>
  );
};

export default Dashboard;
