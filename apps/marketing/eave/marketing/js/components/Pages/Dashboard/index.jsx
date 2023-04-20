import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { HEADER } from '../../../constants.js';
import Copy from '../../Copy/index.js';
import Page from '../Page/index.jsx';

const makeClasses = makeStyles((theme) => ({
  main: {
    position: 'relative',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
    },
  },
}));

const Dashboard = () => {
  const classes = makeClasses();

  return (
    <Page simpleHeader>
      <main className={classes.main}>
        <Copy variant="h1">Welcome to Eave Early Access</Copy>
      </main>
    </Page>
  );
};

export default Dashboard;
