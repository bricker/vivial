import React from 'react';
import { withStyles } from '@material-ui/styles';
import classNames from 'classnames';

class Copy extends React.Component {
  render() {
    const {
      children, classes, className, variant,
    } = this.props;
    const h1Class = classNames(classes.h1, className);
    const h2Class = classNames(classes.h2, className);
    const h3Class = classNames(classes.h3, className);
    const footnoteClass = classNames(classes.footnote, className);
    const pSmallClass = classNames(classes.pSmall, className);
    const pXSmallClass = classNames(classes.pXSmall, className);
    const pClass = classNames(classes.p, className);

    if (variant === 'h1') {
      return <h1 className={h1Class}>{children}</h1>;
    }
    if (variant === 'h2') {
      return <h2 className={h2Class}>{children}</h2>;
    }
    if (variant === 'h3') {
      return <h3 className={h3Class}>{children}</h3>;
    }
    if (variant === 'footnote') {
      return <p className={footnoteClass}>{children}</p>;
    }
    if (variant === 'pSmall') {
      return <p className={pSmallClass}>{children}</p>;
    }
    if (variant === 'pXSmall') {
      return <p className={pXSmallClass}>{children}</p>;
    }
    return <p className={pClass}>{children}</p>;
  }
}

const styles = (theme) => ({
  h1: {
    fontSize: 32,
    lineHeight: '38px',
    fontWeight: 400,
    margin: 0,
    color: theme.typography.color.dark,
    [theme.breakpoints.up('sm')]: {
      fontSize: 54,
      lineHeight: '70px',
    },
  },
  h2: {
    fontSize: 24,
    lineHeight: '31px',
    fontWeight: 400,
    margin: '0 0 12px',
    color: theme.typography.color.dark,
    [theme.breakpoints.up('sm')]: {
      fontSize: 32,
      lineHeight: '42px',
    },
  },
  footnote: {
    fontSize: 14,
    lineHeight: '18px',
    margin: 0,
    [theme.breakpoints.up('sm')]: {
      fontSize: 16,
      lineHeight: '21px',
    },
  },
  pSmall: {
    fontSize: 16,
    lineHeight: '21px',
    fontWeight: 400,
    margin: 0,
    [theme.breakpoints.up('sm')]: {
      fontSize: 18,
      lineHeight: '23px',
    },
  },
  pXSmall: {
    fontSize: 16,
    lineHeight: '19px',
    fontWeight: 400,
    margin: 0,
  },
  p: {
    fontSize: 16,
    lineHeight: '21px',
    fontWeight: 400,
    margin: 0,
    [theme.breakpoints.up('sm')]: {
      fontSize: 24,
      lineHeight: '31px',
    },
  },
});

export default withStyles(styles)(Copy);
