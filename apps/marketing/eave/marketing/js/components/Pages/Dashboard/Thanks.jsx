import React from 'react';
import { makeStyles } from '@material-ui/styles';

import Copy from '../../Copy/index.jsx';

const makeClasses = makeStyles(() => ({
  copy: {
    marginTop: 12,
    maxWidth: 838,
  },
  link: {
    color: 'inherit',
    textDecoration: 'none',
  },
}));

const Thanks = () => {
  const classes = makeClasses();

  return (
      <section className={classes.main}>
        <Copy variant="h1" >Thanks for Signing Up!</Copy>
        <Copy className={classes.copy}>You've been successfully added to the waitlist. We’ll send you an email notification as soon as availability opens up and we’re able to grant you access. For inquiries, contact <a className={classes.link} href="mailto:info@eave.fyi">info@eave.fyi</a></Copy>
      </section>
  );
};

export default Thanks;
