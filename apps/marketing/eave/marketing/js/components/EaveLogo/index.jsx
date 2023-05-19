import React from 'react';
import { Link } from 'react-router-dom';
import classNames from 'classnames';
import { makeStyles } from '@material-ui/styles';

const makeClasses = makeStyles((theme) => ({
  logoWrapper: {
    fontFamily: "'Pattaya', sans-serif",
    fontSize: 24,
    lineHeight: '24px',
    textDecoration: 'none',
    color: theme.typography.color.dark,
    width: 52,
    display: 'inline-block',
    [theme.breakpoints.up('md')]: {
      fontSize: 40,
      lineHeight: '40px',
      width: 78,
    },
  },
  beta: {
    fontSize: 12,
    fontWeight: 700,
    display: 'block',
    lineHeight: 0,
    textAlign: 'right',
    [theme.breakpoints.up('md')]: {
      fontSize: 16,
    },
  },
}));

const EaveLogo = ({ className }) => {
  const classes = makeClasses();
  const logoClasses = classNames(classes.logoWrapper, className);

  return (
    <Link className={logoClasses} to="/">
      eave
      <span className={classes.beta}>Beta</span>
    </Link>
  );
};

export default EaveLogo;
