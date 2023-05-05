import React, { createContext, useState } from 'react';

import { AUTH_MODAL_STATE } from '../constants.js';

export const AppContext = createContext(null);

const AppContextProvider = ({ children }) => {
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  const [userState, setUserState] = useState({
    authenticated: null,
    teamInfo: null,
  });

  const [errorState, setErrorState] = useState({
    error: null,
  });

  const store = {
    authModal: [modalState, setModalState],
    user: [userState, setUserState],
    error: [errorState, setErrorState],
  };

  return (
    <AppContext.Provider value={store}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContextProvider;
