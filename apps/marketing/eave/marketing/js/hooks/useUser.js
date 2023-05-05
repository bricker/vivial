import { useContext } from 'react';
import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user, error } = useContext(AppContext);
  const [userState, setUserState] = user;
  const [, setErrorState] = error;

  return {
    userState,
    setUserState,
    checkUserAuthState: () => {
      fetch('/authcheck', {
        method: 'GET',
      }).then((resp) => {
        resp.json().then((data) => {
          setUserState((prevState) => ({ ...prevState, authenticated: data.authenticated === true }));
        });
      }).catch((err) => {
        console.warn('Error during authcheck', err);
      });
    },
    // gets user info
    getUserInfo: () => {
      console.log('getting user info...');
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        console.log('user info response', resp);
        if (resp.ok === false) {
          setErrorState('failed to fetch team info');
        } else {
          setUserState((prevState) => ({ ...prevState, teamInfo: resp.body }));
        }
        // eslint-disable-next-line no-console
      }).catch((err) => {
        console.log('error fetching user info', err);
        return setErrorState('failed to fetch team info');
      });
    },
    // updates current selected confluene space
    updateConfluenceSpace: (key) => {
      console.log('about to update user space');
      fetch('/dashboard/me/team/integrations/atlassian/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          atlassian_integration: {
            confluence_space_key: key,
          },
        },
      }).then((resp) => {
        // just logging this for now, will update on follow up
        console.log('user space resp', resp);
        if (resp.ok === false) {
          setErrorState('failed to fetch team info');
        } else {
          setUserState((prevState) => ({ ...prevState, teamInfo: resp.body }));
        }
      // eslint-disable-next-line no-console
      }).catch((err) => {
        console.log('error setting up space', err);
      });
    },
    // logs user out
    logOut: () => window.location.assign('/dashboard/logout'),
  };
};

export default useUser;
