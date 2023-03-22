import React from 'react';
import { Link } from 'react-router-dom';
import classNames from 'classnames';
import { withStyles } from '@material-ui/styles';

class EaveLogo extends React.Component {
  render() {
    const { classes, className } = this.props;
    const logoClasses = classNames(classes.logo, className);
    return (
      <Link className={logoClasses} to="/">eave</Link>
    );
  }
}

const styles = (theme) => ({
  logo: {
    fontFamily: theme.typography.fontFamily.logo,
    fontSize: 24,
    lineHeight: '24px',
    textDecoration: 'none',
    color: theme.typography.color.dark,
    [theme.breakpoints.up('md')]: {
      fontSize: 40,
      lineHeight: '40px',
    },
  },
});

export default withStyles(styles)(EaveLogo);
