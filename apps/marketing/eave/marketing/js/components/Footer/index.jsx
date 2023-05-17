import React from 'react';
import { makeStyles } from '@material-ui/styles';
import { Link } from 'react-router-dom';

import Copy from '../Copy/index.jsx';

const makeClasses = makeStyles((theme) => ({
  outerContainer: {
    width: '100%',
    zIndex: 10,
  },
  innerContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'flex-start',
    padding: '0px 30px 24px 40px',
    gap: '10px 23px',
    maxWidth: 1440,
    margin: '0 auto',
    [theme.breakpoints.up('md')]: {
      padding: '0px 46px 46px',
    },
  },
  copyRight: {
    display: 'block',
    width: '100%',
    [theme.breakpoints.up('md')]: {
      display: 'inline',
      width: 'auto',
    },
  },
  link: {
    display: 'inline-block',
    color: 'inherit',
  },
}));

const Footer = () => {
  const classes = makeClasses();
  const year = new Date().getFullYear();

  return (
    <footer className={classes.outerContainer}>
      <Copy className={classes.innerContainer} variant="footnote">
        <span className={classes.copyRight} >© {year} Eave Technologies, Inc. All rights reserved.</span>
        <Link className={classes.link} to="/terms">Terms</Link>
        <Link className={classes.link} to="/privacy">Privacy Policy</Link>
      </Copy>
    </footer>
  );
};

export default Footer;
