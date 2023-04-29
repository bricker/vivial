import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@material-ui/core';
import { withStyles } from '@material-ui/styles';
import classNames from 'classnames';

class ButtonWrapper extends React.Component {
  render() {
    const {
      children,
      classes,
      className,
      lg,
      color,
      variant,
      onClick,
      type,
      to,
    } = this.props;
    const sizeClass = lg ? classes.large : '';
    const rootClass = classNames(classes.root, className, sizeClass);
    const btn = (
      <Button
        classes={{ root: rootClass }}
        color={color || 'primary'}
        variant={variant || 'contained'}
        onClick={onClick}
        type={type}
      >
        {children}
      </Button>
    );

    if (to) {
      return (
        <Link className={classes.link} to={to}>
          {btn}
        </Link>
      );
    }

    return btn;
  }
}

const styles = (theme) => ({
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
});

export default withStyles(styles)(ButtonWrapper);
