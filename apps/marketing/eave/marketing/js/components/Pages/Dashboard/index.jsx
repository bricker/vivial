/* eslint-disable no-nested-ternary */
import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress } from '@material-ui/core';

import useUser from '../../../hooks/useUser.js';
import PageSection from '../../PageSection/index.jsx';
import Page from '../Page/index.jsx';
import Thanks from './Thanks.jsx';
import Steps from './Steps.jsx';
import Copy from '../../Copy/index.jsx';

const makeClasses = makeStyles(() => ({
  main: {
    minHeight: '80vh',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '80vh',
  },
}));

const Dashboard = () => {
  const classes = makeClasses();
  const { userState, loadingGetUserInfo, getUserInfo, getUserError } = useUser();
  const { teamInfo } = userState;

  useEffect(() => {
    // fetch info
    if (!teamInfo && !loadingGetUserInfo) {
      getUserInfo();
    }
  }, [teamInfo]);

  return (
    <Page>
      <PageSection wrapperClassName={classes.main} topSection>
        {!teamInfo || loadingGetUserInfo ? (
          <div className={classes.loading}>
            {getUserError ? (
              <Copy>something went wrong please try again</Copy>
            ) : (
              <CircularProgress />
            )}
          </div>
        ) : teamInfo.team.beta_whitelisted === false ? (
          <Thanks />
        ) : (
          <Steps />
        )}
      </PageSection>
    </Page>
  );
};

export default Dashboard;
