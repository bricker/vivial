import React from 'react';
import { withStyles } from '@material-ui/styles';
import { Link } from 'react-router-dom';

import { FOOTER } from '../../constants.js';
import Copy from '../Copy/index.js';

class Footer extends React.Component {
  render() {
    const { classes } = this.props;
    const year = new Date().getFullYear();
    return (
      <footer className={classes.outerContainer}>
        <Copy className={classes.innerContainer} variant="footnote">
          © {year} Eave Technologies, Inc. All rights reserved.
          <Link className={classes.link} to="/terms">Terms</Link>
          <Link className={classes.link} to="/privacy">Privacy Policy</Link>
        </Copy>
      </footer>
    );
  }
}

const styles = (theme) => ({
  outerContainer: {
    width: '100%',
    zIndex: 10,
  },
  innerContainer: {
    height: FOOTER.mobile.height,
    display: 'flex',
    alignItems: 'center',
    padding: '0px 30px',
    [theme.breakpoints.up('md')]: {
      height: FOOTER.desktop.height,
    },
  },
  link: {
    display: 'inline-block',
    color: 'inherit',
    marginLeft: 24,
  },
});

export default withStyles(styles)(Footer);
