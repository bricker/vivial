import React from 'react';
import { Link } from 'react-router-dom';
import { Button as MaterialButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import classNames from 'classnames';

const makeClasses = makeStyles(() => ({
  root: {
    width: 172,
    height: 50,
    textTransform: 'none',
    borderRadius: '10px',
    fontSize: 16,
  },
  disabled: {
    backgroundColor: '#808182 !important',
    color: '#FFFFFF !important',
  },
  link: {
    textDecoration: 'none',
  },
}));

const Button = ({
  color = "primary",
  variant = "contained",
  children,
  className,
  target,
  to,
  ...rest
}) => {
  const classes = makeClasses();
  const rootClass = classNames(classes.root, className);

  const button = (
    <MaterialButton
      classes={{
        root: rootClass,
        disabled: classes.disabled
      }}
      color={color}
      variant={variant}
      {...rest}
    >
      {children}
    </MaterialButton>
  );

  if (to) {
    return (
      <Link className={classes.link} to={to} target={target}>
        {button}
      </Link>
    );
  }

  return button;
};

export default Button;
