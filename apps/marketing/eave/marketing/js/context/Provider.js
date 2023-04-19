import React, { createContext, useState } from 'react';

import { AUTH_MODAL_STATE } from '../constants.js';

export const AppContext = createContext(null);

const AppContextProvider = ({ children }) => {
  const [modalState, setModalState] = useState({
    isOpen: true,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  const [userState, setUserState] = useState({
    isLoggedIn: true,
    isWhitelisted: false,
  });

  const store = {
    authModal: [modalState, setModalState],
    user: [userState, setUserState],
  };

  return (
    <AppContext.Provider value={store}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContextProvider;
