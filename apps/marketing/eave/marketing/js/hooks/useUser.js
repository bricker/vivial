import { useContext } from 'react';
import { useCookies } from 'react-cookie';
import { useNavigate } from 'react-router-dom';

import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user, error } = useContext(AppContext);
  const [userState, setUserState] = user;
  const [, setErrorState] = error;
  const [cookies] = useCookies(['ev_access_token']);
  const navigate = useNavigate();

  return {
    userState,
    setUserState,
    isUserAuth: cookies.ev_access_token,
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
      // eslint-disable-next-line no-console
      }).catch((err) => {
        console.log('error setting up space', err);
      });
    },
    // logs user out
    logOut: () => navigate('/dashboard/logout'),
  };
};

export default useUser;
