import React from 'react';
import { Link } from 'react-router-dom';
import { Button as MaterialButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import classNames from 'classnames';

const makeClasses = makeStyles((theme) => ({
  root: {
    height: 50,
    padding: '0px 16px',
    fontSize: 16,
    fontWeight: 700,
    color: theme.typography.color.light,
    textTransform: 'none',
    borderRadius: 10,
  },
  large: {
    height: 60,
    width: '100%',
    fontSize: 18,
    [theme.breakpoints.up('sm')]: {
      height: 70,
      width: 213,
      fontSize: 20,
    },
  },
  link: {
    color: theme.typography.color.light,
    textDecoration: 'none',
  },
}));

const Button = ({
  children,
  className,
  lg,
  color,
  variant,
  to,
  ...rest
}) => {
  const classes = makeClasses();

  const sizeClass = lg ? classes.large : '';
  const rootClass = classNames(classes.root, className, sizeClass);
  const btn = (
    <MaterialButton
      classes={{ root: rootClass }}
      color={color || 'primary'}
      variant={variant || 'contained'}
      {...rest}
    >
      {children}
    </MaterialButton>
  );

  if (to) {
    return (
      <Link className={classes.link} to={to}>
        {btn}
      </Link>
    );
  }

  return btn;
};

export default Button;
