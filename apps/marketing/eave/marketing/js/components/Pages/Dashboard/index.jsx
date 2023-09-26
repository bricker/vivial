import React, { useCallback, useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useSearchParams } from "react-router-dom";
import useTeam from "../../../hooks/useTeam.js";
import useUser from "../../../hooks/useUser.js";

import ExploreFeatures from "../../ExploreFeatures/index.jsx";
import FeatureSettings from "../../FeatureSettings/index.jsx";
import GitHubFeatureModal from "../../GitHubFeatureModal/index.jsx";
import ErrorPage from "../ErrorPage/index.jsx";
import LoadingPage from "../LoadingPage/index.jsx";
import Page from "../Page/index.jsx";

import { COOKIE_NAMES, FEATURES, FEATURE_STATES, SEARCH_PARAM_NAMES, SEARCH_PARAM_VALUES } from "../../../constants.js";

const Dashboard = () => {
  const [searchParams] = useSearchParams();
  const [cookies, _, removeCookie] = useCookies([COOKIE_NAMES.FEATURE_MODAL]);
  const { team, getTeam, getTeamRepos, getTeamFeatureStates, updateTeamFeatureState } = useTeam();
  const { user, getUserAccount } = useUser();

  const isLoading = user.accountIsLoading || team.teamIsLoading || team.reposAreLoading || team.featureStatesLoading;

  const isErroring = user.accountIsErroring || team.teamIsErroring || team.reposAreErroring || team.featureStatesErroring;

  const showFeatureSettings = team.inlineCodeDocsState === FEATURE_STATES.ENABLED || team.apiDocsState === FEATURE_STATES.ENABLED;

  const [showInlineDocsModal, setShowInlineDocsModal] = useState(false);

  const openInlineDocsModal = useCallback(() => {
    setShowInlineDocsModal(true);
  }, []);

  const closeInlineDocsModal = useCallback(() => {
    setShowInlineDocsModal(false);
  }, []);

  const handleFeatureUpdate = useCallback((teamId, teamRepoIds, enabledRepoIds, feature) => {
    updateTeamFeatureState(teamId, teamRepoIds, enabledRepoIds, feature);
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
    return <ErrorPage page="dashboard" />;
  }
  return (
    <Page>
      <ExploreFeatures onInlineDocsClick={openInlineDocsModal} />
      {showFeatureSettings && <FeatureSettings onInlineDocsClick={openInlineDocsModal} />}
      {showInlineDocsModal && <GitHubFeatureModal feature={FEATURES.INLINE_CODE_DOCS} param={SEARCH_PARAM_VALUES.INLINE_CODE_DOCS} onClose={closeInlineDocsModal} onUpdate={handleFeatureUpdate} open />}
    </Page>
  );
};

export default Dashboard;
