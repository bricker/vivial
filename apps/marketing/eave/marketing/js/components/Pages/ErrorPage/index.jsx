import React from 'react';
import { makeStyles } from '@material-ui/styles';
import Page from '../Page/index.jsx';

const makeClasses = makeStyles((theme) => ({
  error: {
    color: theme.palette.error.main,
    padding: 60,
    textAlign: 'center',
    fontSize: '32px',
  },
}));

const ErrorPage = ({ page }) => {
  const classes = makeClasses();
  return (
    <Page>
      <div className={classes.error}>
        ERROR: Unable to fetch {page}.
      </div>
    </Page>
  );
};

export default ErrorPage;
