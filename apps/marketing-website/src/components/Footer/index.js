import React from 'react';
import { withStyles } from '@material-ui/styles';
import { FOOTER } from '../../constants';
import Copy from '../Copy';

class Footer extends React.Component {
  render() {
    const { classes } = this.props;
    const year = new Date().getFullYear();
    return (
      <footer className={classes.outerContainer}>
        <Copy className={classes.innerContainer} variant="footnote">
          © {year} Eave, Inc. All rights reserved.
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
});

export default withStyles(styles)(Footer);
