import React from 'react';
import { withStyles } from '@material-ui/styles';

import Header from '../../Header/index.js';
import Footer from '../../Footer/index.js';

class Page extends React.Component {
  render() {
    const { classes, children, simpleHeader } = this.props;

    return (
      <div className={classes.container}>
        <Header simpleHeader={simpleHeader} />
        {children}
        <Footer />
      </div>
    );
  }
}

const styles = (theme) => ({
  container: {
    position: 'relative',
    minHeight: '100vh',
    fontFamily: theme.typography.fontFamily.main,
    color: theme.typography.color.main,
    backgroundColor: theme.palette.background.main,
  },
});

export default withStyles(styles)(Page);
