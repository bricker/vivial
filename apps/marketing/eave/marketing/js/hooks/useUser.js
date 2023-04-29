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
      fetch('/log-in', {
        body: JSON.stringify({ }),
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then(() => {
        // TODO: SET INFO COMING FROM API TO THE USER OBJECT
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
