import React from 'react'
import { makeStyles } from '@material-ui/styles';

import { HEADER } from '../../../constants.js';
import Page from '../Page/index.js';
import Copy from '../../Copy/index.js';

const makeClasses = makeStyles((theme) => ({
  main: {
    position: 'relative',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
    },
  },
  copy: {
    marginTop: 12,
    maxWidth: 838,
  },
  link: {
    color: 'inherit',
    textDecoration: 'none',
  },
}));

const ThanksPage = () => {
  const classes = makeClasses();

  return (
    <Page>
      <main className={classes.main}>
        <Copy variant="h1" >Thanks for Signing Up!</Copy>
        <Copy className={classes.copy}>You've been successfully added to the waitlist. We’ll send you an email notification as soon as availability opens up and we’re able to grant you access. For inquiries, contact <a className={classes.link} href="mailto:info@eave.fyi">info@eave.fyi</a></Copy>
      </main>
    </Page>
  );
};

export default ThanksPage;
