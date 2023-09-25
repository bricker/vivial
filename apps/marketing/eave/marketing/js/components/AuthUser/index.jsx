import React, { useEffect } from 'react';
import { CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

import useUser from '../../hooks/useUser';

const makeClasses = makeStyles((theme) => ({
  loader: {
    backgroundColor: theme.palette.background.main,
    paddingTop: `calc(${theme.header.height}px + ${theme.header.marginBottom}px)`,
    width: '100vw',
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    [theme.breakpoints.up('md')]: {
      paddingTop: `calc(${theme.header.md.height}px + ${theme.header.md.marginBottom}px)`,
    }
  },
}));

const AuthUser = ({ children }) => {
  const classes = makeClasses();
  const { user, checkUserAuth } = useUser();
  const { isAuthenticated } = user;

  useEffect(() => {
    if (isAuthenticated === null) {
      checkUserAuth();
    }
  }, [isAuthenticated]);

  if (isAuthenticated === null) {
    return (
      <div className={classes.loader}>
        <CircularProgress />
      </div>
    );
  }

  return children;
};

export default AuthUser;
