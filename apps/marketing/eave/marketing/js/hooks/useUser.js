import { useContext } from 'react';

import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user } = useContext(AppContext);
  const [userState, setUserState] = user;

  return {
    userState,
    setUserState,
    isLoggedIn: userState.isLoggedIn,
    logIn: () => {
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
-        console.log('resp', resp);
        setUserState((prevState) => ({ ...prevState, isLoggedIn: true }));
      });
    },
    logOut: () => {
      fetch('/log-out', {
        body: JSON.stringify({ }),
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then(() => {
        // TODO: CLEAR USER INFO AND COOKIES
        setUserState((prevState) => ({ ...prevState, isLoggedIn: false }));
      });
    },
  };
};

export default useUser;
