import { useContext } from 'react';
import { useCookies } from 'react-cookie';
import { useNavigate } from 'react-router-dom';

import { AppContext } from '../context/Provider.js';

const useUser = () => {
  const { user } = useContext(AppContext);
  const [userState, setUserState] = user;
  const [cookies] = useCookies(['ev_access_token']);
  const navigate = useNavigate();

  return {
    userState,
    setUserState,
    isUserAuth: cookies.ev_access_token,
    getUserInfo: () => {
      fetch('/dashboard/me/team', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((resp) => {
        setUserState((prevState) => ({ ...prevState, teamInfo: resp.body }));
      // eslint-disable-next-line no-console
      }).catch((err) => console.log(err));
    },
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
    logOut: () => navigate('/dashboard/logout'),
  };
};

export default useUser;
