import { useContext } from 'react';

import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user } = useContext(AppContext);
  const [userState, setUserState] = user;

  return {
    userState,
    setUserState,
    isLoggedIn: userState.isLoggedIn,
    logIn: () => setUserState((prevState) => ({ ...prevState, isLoggedIn: true })),
    logOut: () => setUserState((prevState) => ({ ...prevState, isLoggedIn: false })),
  };
};

export default useUser;
