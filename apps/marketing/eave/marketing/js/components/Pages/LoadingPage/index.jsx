import React from 'react';
import { CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import Page from '../Page/index.jsx';

const makeClasses = makeStyles(() => ({
  loader: {
    position: 'absolute',
    top: 0,
    width: '100vw',
    height: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}));

const LoadingPage = () => {
  const classes = makeClasses();
  return (
    <Page hideFooter>
      <div className={classes.loader}>
        <CircularProgress />
      </div>
    </Page>
  );
};

export default LoadingPage;
