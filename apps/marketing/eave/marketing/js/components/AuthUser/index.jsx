import React, { useEffect } from 'react';
import { CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

import useUser from '../../hooks/useUser';

const makeClasses = makeStyles(() => ({
  loader: {
    width: '100vw',
    height: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));

const AuthUser = ({ children }) => {
  const classes = makeClasses();
  const { userState, checkUserAuthState } = useUser();
  const { authenticated } = userState;

  useEffect(() => {
    if (authenticated === null) {
      checkUserAuthState();
    }
  }, [authenticated]);

  if (authenticated === null) {
    return (
      <div className={classes.loader}>
        <CircularProgress />
      </div>
    );
  }

  return children;
};

export default AuthUser;
