import { useContext, useState } from 'react';
import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user } = useContext(AppContext);
  const [userState, setUserState] = user;
  const [getUserError, setGetUserError] = useState(null);
  const [updateConfluenceError, setUpdateConfluenceError] = useState(null);
  const [loadingGetUserInfo, setLoadingGetUserInfo] = useState(false);
  const [loadingAvailableSpaces, setLoadingAvailableSpaces] = useState(false);
  const [loadingUpdateConfluenceSpace, setLoadingUpdateConfluenceSpace] = useState(false);

  return {
    userState,
    setUserState,
    loadingGetUserInfo,
    loadingAvailableSpaces,
    loadingUpdateConfluenceSpace,
    getUserError,
    updateConfluenceError,
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
      setLoadingGetUserInfo(true);
      setGetUserError(null);
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        if (resp.ok === false) {
          setGetUserError('failed to fetch team info');
        } else {
          resp.json().then((data) => {
            setUserState((prevState) => ({ ...prevState, teamInfo: data }));
          });
        }
        // eslint-disable-next-line no-console
      }).catch((err) => {
        console.error('error fetching user info', err);
        return setGetUserError('failed to fetch team info');
      }).finally(() => {
        setLoadingGetUserInfo(false);
      });
    },
    getAvailableSpaces: () => {
      setLoadingAvailableSpaces(true);
      fetch('/dashboard/me/team/destinations/confluence/spaces/query', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        if (resp.ok === false) {
          console.error('failed to fetch available spaces');
        } else {
          resp.json().then((data) => {
            setUserState((prevState) => ({ ...prevState, availableSpaces: data.confluence_spaces }));
          });
        }
        // eslint-disable-next-line no-console
      }).catch((err) => {
        console.error('failed to fetch available spaces', err);
      }).finally(() => {
        setLoadingAvailableSpaces(false);
      });
    },
    // updates current selected confluence space
    updateConfluenceSpace: (key, forgeAppInstallationId, onComplete) => {
      setLoadingUpdateConfluenceSpace(true);
      setUpdateConfluenceError(null);
      fetch('/dashboard/me/team/destinations/confluence/upsert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          confluence_destination: {
            space_key: key,
          },
        }),
      }).then((resp) => {
        // just logging this for now, will update on follow up
        if (resp.ok === false) {
          setUpdateConfluenceError('failed to fetch team info');
        } else {
          resp.json().then((data) => {
            setUserState((prevState) => ({ ...prevState, teamInfo: data }));
          });
          onComplete?.();
        }
      // eslint-disable-next-line no-console
      }).catch((err) => {
        console.error('error setting up space', err);
        return setUpdateConfluenceError('error setting up space');
      }).finally(() => {
        setLoadingUpdateConfluenceSpace(false);
      });
    },
    // logs user out
    logOut: () => window.location.assign('/dashboard/logout'),
  };
};

export default useUser;
