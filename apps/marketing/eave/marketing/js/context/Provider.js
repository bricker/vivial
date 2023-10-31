// @ts-check
import React, { createContext, useState } from "react";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars
import { AUTH_MODAL_STATE } from "../constants.js";

export const AppContext = createContext(null);

const AppContextProvider = ({ children }) => {
  const [authModal, setAuthModal] = useState({
    isOpen: false,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  const [/** @type {Types.DashboardUser} */ user, setUser] = useState({
    account: {},
    accountIsLoading: true,
    accountIsErroring: false,
  });

  const [/** @type {Types.DashboardTeam} */ team, setTeam] = useState({
    id: {},
    name: "",
    teamIsLoading: true,
    teamIsErroring: false,
    integrations: {},
    repos: [],
    reposAreLoading: true,
    reposAreErroring: false,
    repoCreationInProgress: false,
    repoCreationIsErroring: false,
    inlineCodeDocsEnabled: false,
    apiDocsEnabled: false,
    apiDocs: [],
    apiDocsFetchCount: 0,
    apiDocsLoading: true,
    apiDocsErroring: false,
    featureStatesLoading: true,
    featureStatesErroring: false,
  });

  const ctx = {
    authModalCtx: [authModal, setAuthModal],
    userCtx: [user, setUser],
    teamCtx: [team, setTeam],
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
