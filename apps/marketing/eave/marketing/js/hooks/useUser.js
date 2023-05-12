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
        console.error('Error during authcheck', err);
      });
    },
    // gets user info
    getUserInfo: () => {
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        if (resp.ok === false) {
          setErrorState('failed to fetch team info');
        } else {
          resp.json().then((data) => {
            setUserState((prevState) => ({ ...prevState, teamInfo: data }));
          });
        }
        // eslint-disable-next-line no-console
      }).catch((err) => {
        console.error('error fetching user info', err);
        return setErrorState('failed to fetch team info');
      });
    },
    // updates current selected confluene space
    updateConfluenceSpace: (key) => {
      fetch('/dashboard/me/team/integrations/atlassian/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          atlassian_integration: {
            confluence_space_key: key,
          },
        }),
      }).then((resp) => {
        // just logging this for now, will update on follow up
        if (resp.ok === false) {
          setErrorState('failed to fetch team info');
        } else {
          resp.json().then((data) => {
            setUserState((prevState) => ({ ...prevState, teamInfo: data }));
          });
        }
      // eslint-disable-next-line no-console
      }).catch((err) => {
        console.error('error setting up space', err);
      });
    },
    // logs user out
    logOut: () => window.location.assign('/dashboard/logout'),
  };
};

export default useUser;
