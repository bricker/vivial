import React, { createContext, useState } from 'react';

import { AUTH_MODAL_STATE } from '../constants.js';

export const AppContext = createContext(null);

const AppContextProvider = ({ children }) => {
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  const [userState, setUserState] = useState({
    teamInfo: {
      account: {
        id: 'bee0a7fe-7765-4ca6-b8f7-58b170c89f95',
        auth_provider: 'google',
        access_token: '[...]',
      },
      team: {
        id: '10875b71-d57f-4707-8688-2c3e2e7b30f2',
        name: "Bryan's Team",
        document_platform: null,
      },
      integrations: {
        github: null,
        slack: null,
        atlassian: {
          id: '25f452c6-ca91-4e63-b367-f982c3ff51ab',
          team_id: '10875b71-d57f-4707-8688-2c3e2e7b30f2',
          atlassian_cloud_id: '00ce9a4a-899a-4529-866c-eb6feb0e9e06',
          confluence_space: null,
          available_confluence_spaces: [
            {
              key: '~63a5faccb790087ed70fc684',
              name: 'Bryan Ricker',
            },
            {
              key: 'ED',
              name: 'Eave Dev',
            },
          ],
          oauth_token_encoded: '[...]',
        },
      },
    },
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
