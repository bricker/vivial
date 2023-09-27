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

import { FEATURES, FEATURE_STATES, FEATURE_MODAL } from "../../../constants.js";

const Dashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [cookies, _, removeCookie] = useCookies([FEATURE_MODAL.ID]);
  const { team, getTeam, getTeamRepos, getTeamFeatureStates, updateTeamFeatureState } = useTeam();
  const { user, getUserAccount } = useUser();
  const isLoading = user.accountIsLoading || team.teamIsLoading || team.reposAreLoading || team.featureStatesLoading;
  const isErroring = user.accountIsErroring || team.teamIsErroring || team.reposAreErroring || team.featureStatesErroring;
  const showFeatureSettings = team.inlineCodeDocsState === FEATURE_STATES.ENABLED || team.apiDocsState === FEATURE_STATES.ENABLED;
  const [showInlineDocsModal, setShowInlineDocsModal] = useState(false);

  const modalCleanup = () => {
    removeCookie(FEATURE_MODAL.ID);
    setSearchParams({});
  };

  const openInlineDocsModal = useCallback(() => {
    setSearchParams({ [FEATURE_MODAL.ID]: FEATURE_MODAL.TYPES.INLINE_CODE_DOCS });
    setShowInlineDocsModal(true);
  }, []);

  const closeInlineDocsModal = useCallback(() => {
    setShowInlineDocsModal(false);
    modalCleanup();
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
    const featureModal = cookies && cookies[FEATURE_MODAL.ID];
    if (featureModal) {
      if (featureModal === FEATURE_MODAL.TYPES.INLINE_CODE_DOCS) {
        openInlineDocsModal();
      }
    }
  }, [cookies]);

  useEffect(() => {
    const featureParam = searchParams.get(FEATURE_MODAL.ID);
    if (featureParam) {
      if (featureParam === FEATURE_MODAL.TYPES.INLINE_CODE_DOCS && !showInlineDocsModal) {
        openInlineDocsModal();
      }
    }
  }, [searchParams, showInlineDocsModal]);

  if (isErroring) {
    return <ErrorPage page="dashboard" />;
  }
  if (isLoading) {
    return <LoadingPage />;
  }
  return (
    <Page>
      <ExploreFeatures onInlineDocsClick={openInlineDocsModal} />
      {showFeatureSettings && <FeatureSettings onInlineDocsClick={openInlineDocsModal} />}
      {showInlineDocsModal && (
        <GitHubFeatureModal
          feature={FEATURES.INLINE_CODE_DOCS}
          type={FEATURE_MODAL.TYPES.INLINE_CODE_DOCS}
          onClose={closeInlineDocsModal}
          onUpdate={handleFeatureUpdate}
          open={showInlineDocsModal}
        />
      )}
    </Page>
  );
};

export default Dashboard;
