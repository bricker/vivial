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
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        console.log('response', resp);
        if (resp.ok === false) {
          setErrorState('failed to fetch team info');
        } else {
          setUserState((prevState) => ({ ...prevState, teamInfo: resp.body }));
        }
        // eslint-disable-next-line no-console
      }).catch((err) => {
        console.log(err);
        return setErrorState('failed to fetch team info');
      });
    },
    // updates current selected confluene space
    updateConfluenceSpace: () => {
      fetch('/dashboard/me/team/integrations/atlassian/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        // just logging this for now, will update on follow up
        console.log(resp);
      // eslint-disable-next-line no-console
      }).catch((err) => console.log(err));
    },
    // logs user out
    logOut: () => navigate('/dashboard/logout'),
  };
};

export default useUser;
