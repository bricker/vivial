import React, { createContext, useState } from 'react';

import { AUTH_MODAL_STATE } from '../constants.js';

export const AppContext = createContext(null);


// TODO: update modal and error to use ctx verbiage


const AppContextProvider = ({ children }) => {
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  const [user, setUser] = useState({
    isAuthenticated: null,
    authIsErroring: false,
    account: {},
    accountIsLoading: true,
    accountIsErroring: false,
  });

  const [team, setTeam] = useState({
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


    // TODO: won't need this
    accessibleRepos: [],
    accessibleReposAreLoading: true,
    accessibleReposAreErroring: false,





    apiDocuments: [],
    featureStates: {},
    featureStatesAreLoading: true,
  });

  const [errorState, setErrorState] = useState({
    error: null,
  });

  const ctx = {
    authModal: [modalState, setModalState],


    userCtx: [user, setUser],
    teamCtx: [team, setTeam],


    error: [errorState, setErrorState],
  };

  return (
    <AppContext.Provider value={ctx}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContextProvider;
