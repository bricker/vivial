/* eslint-disable no-nested-ternary */
import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress } from '@material-ui/core';

import { HEADER } from '../../../constants.js';
import useUser from '../../../hooks/useUser.js';
import Page from '../Page/index.jsx';
import Thanks from './Thanks.jsx';
import Steps from './Steps.jsx';

const makeClasses = makeStyles((theme) => ({
  main: {
    position: 'relative',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
    },
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
  },
}));

const Dashboard = () => {
  const classes = makeClasses();
  const { userState, loadingGetUserInfo, getUserInfo } = useUser();
  const { teamInfo } = userState;

  useEffect(() => {
    // fetch info
    if (!teamInfo && !loadingGetUserInfo) {
      getUserInfo();
    }
  }, [teamInfo]);

  return (
    <Page>
      <main className={classes.main}>
        {!teamInfo || loadingGetUserInfo ? (
          <div className={classes.loading}>
            <CircularProgress />
          </div>
        ) : teamInfo.team.beta_whitelisted === false ? (
          <Thanks />
        ) : (
          <Steps />
        )}
      </main>
    </Page>
  );
};

export default Dashboard;
