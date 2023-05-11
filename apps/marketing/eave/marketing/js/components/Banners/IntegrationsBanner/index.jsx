import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { INTEGRATION_LOGOS } from '../../../constants.js';
import Copy from '../../Copy/index.jsx';

const makeClasses = makeStyles((theme) => ({
  section: {
    backgroundColor: theme.palette.background.dark,
    padding: '54px 40px',
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '54px 40px',
    },
    [theme.breakpoints.up('md')]: {
      padding: '82px 164px',
    },
    [theme.breakpoints.up('lg')]: {
      flexDirection: 'row',
    },
  },
  copy: {
    marginBottom: 15,
    [theme.breakpoints.up('sm')]: {
      padding: 0,
    },
    [theme.breakpoints.up('lg')]: {
      width: 409,
      minWidth: 409,
      marginBottom: 0,
    },
  },
  logos: {
    display: 'flex',
    width: '100%',
    maxWidth: 374,
    alignItems: 'center',
    margin: '0 auto',
    justifyContent: 'space-between',
    [theme.breakpoints.up('md')]: {
      maxWidth: 738,
    },
    [theme.breakpoints.up('lg')]: {
      maxWidth: 'unset',
      marginLeft: '5%',
    },
  },
  slack: {
    width: 84,
    [theme.breakpoints.up('md')]: {
      width: 168,
    },
  },
  github: {
    width: 57,
    [theme.breakpoints.up('md')]: {
      width: 103,
    },
  },
  jira: {
    width: 116,
    [theme.breakpoints.up('md')]: {
      width: 232,
    },
  },
}));

const IntegrationsBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <section id="eave-integrations-banner" className={classes.section}>
      <div className={classes.copy}>
        <Copy variant="h2">
          {title}
        </Copy>
        <Copy variant="pSmall">
          {subtitle}
        </Copy>
      </div>
      <div className={classes.logos}>
        <img className={classes.slack} src={INTEGRATION_LOGOS.slack.src} alt={INTEGRATION_LOGOS.slack.alt} />
        <img className={classes.github} src={INTEGRATION_LOGOS.github.src} alt={INTEGRATION_LOGOS.github.alt} />
        <img className={classes.jira} src={INTEGRATION_LOGOS.jira.src} alt={INTEGRATION_LOGOS.jira.alt} />
      </div>
  </section>
  );
};

export default IntegrationsBanner;
