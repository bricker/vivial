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

<<<<<<< HEAD
import { FEATURES, FEATURE_STATES, FEATURE_MODAL } from "../../../constants.js";
=======
import { FEATURES, FEATURE_MODAL, FEATURE_STATES } from "../../../constants.js";
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5

const Dashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [cookies, _, removeCookie] = useCookies([FEATURE_MODAL.ID]);
<<<<<<< HEAD
  const { team, getTeam, getTeamRepos, getTeamFeatureStates, updateTeamFeatureState } = useTeam();
  const { user, getUserAccount } = useUser();
  const isLoading = user.accountIsLoading || team.teamIsLoading || team.reposAreLoading || team.featureStatesLoading;
  const isErroring = user.accountIsErroring || team.teamIsErroring || team.reposAreErroring || team.featureStatesErroring;
  const showFeatureSettings = team.inlineCodeDocsState === FEATURE_STATES.ENABLED || team.apiDocsState === FEATURE_STATES.ENABLED;
=======
  const {
    team,
    getTeam,
    getTeamRepos,
    getTeamFeatureStates,
    updateTeamFeatureState,
  } = useTeam();
  const { user, getUserAccount } = useUser();
  const isLoading =
    user.accountIsLoading ||
    team.teamIsLoading ||
    team.reposAreLoading ||
    team.featureStatesLoading;
  const isErroring =
    user.accountIsErroring ||
    team.teamIsErroring ||
    team.reposAreErroring ||
    team.featureStatesErroring;
  const showFeatureSettings =
    team.inlineCodeDocsState === FEATURE_STATES.ENABLED ||
    team.apiDocsState === FEATURE_STATES.ENABLED;
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5
  const [showInlineDocsModal, setShowInlineDocsModal] = useState(false);

  const modalCleanup = () => {
    removeCookie(FEATURE_MODAL.ID);
    setSearchParams({});
  };

  const openInlineDocsModal = useCallback(() => {
<<<<<<< HEAD
    setSearchParams({ [FEATURE_MODAL.ID]: FEATURE_MODAL.TYPES.INLINE_CODE_DOCS });
=======
    setSearchParams({
      [FEATURE_MODAL.ID]: FEATURE_MODAL.TYPES.INLINE_CODE_DOCS,
    });
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5
    setShowInlineDocsModal(true);
  }, []);

  const closeInlineDocsModal = useCallback(() => {
    setShowInlineDocsModal(false);
    modalCleanup();
  }, []);

<<<<<<< HEAD
  const handleFeatureUpdate = useCallback((teamId, teamRepoIds, enabledRepoIds, feature) => {
    updateTeamFeatureState(teamId, teamRepoIds, enabledRepoIds, feature);
    closeInlineDocsModal();
  }, []);
=======
  const handleFeatureUpdate = useCallback(
    (teamId, teamRepoIds, enabledRepoIds, feature) => {
      updateTeamFeatureState(teamId, teamRepoIds, enabledRepoIds, feature);
      closeInlineDocsModal();
    },
    [],
  );
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5

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
<<<<<<< HEAD
      if (featureParam === FEATURE_MODAL.TYPES.INLINE_CODE_DOCS && !showInlineDocsModal) {
=======
      if (
        featureParam === FEATURE_MODAL.TYPES.INLINE_CODE_DOCS &&
        !showInlineDocsModal
      ) {
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5
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
<<<<<<< HEAD
      {showFeatureSettings && <FeatureSettings onInlineDocsClick={openInlineDocsModal} />}
=======
      {showFeatureSettings && (
        <FeatureSettings onInlineDocsClick={openInlineDocsModal} />
      )}
>>>>>>> d035c201bb4a9aaaa40c69f1981c1b022e809ce5
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
