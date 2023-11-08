// @ts-check
import React, { useContext, useEffect } from 'react';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress } from '@material-ui/core';

import useUser from '../../../hooks/useUser.js';
import PageSection from '../../PageSection/index.jsx';
import Page from '../Page/index.jsx';
import Steps from './Steps.jsx';
import Copy from '../../Copy/index.jsx';
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import { AppContext } from '../../../context/Provider.js';
import useTeam from '../../../hooks/useTeam.js';

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

  /** @type {import("../../../context/Provider.js").AppContextProps} */
  const { dashboardNetworkStateCtx: [networkState] } = useContext(AppContext);

  const {
    accountIsLoading,
    accountIsErroring,
  } = networkState;

  const { user, getUserAccount } = useUser();
  const { team } = useTeam();

  useEffect(() => {
    // fetch info
    if (!team && !accountIsLoading) {
      getUserAccount();
    }
  }, [team]);

  return (
    <Page>
      <PageSection wrapperClassName={classes.main}>
        {!team || accountIsLoading ? (
          <div className={classes.loading}>
            {accountIsErroring ? (
              <Copy>something went wrong, please try again</Copy>
            ) : (
              <CircularProgress />
            )}
          </div>
        ) : (
          <Steps />
        )}
      </PageSection>
    </Page>
  );
};

export default Dashboard;
