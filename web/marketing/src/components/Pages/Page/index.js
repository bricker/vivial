import React from 'react';
import { withStyles } from '@material-ui/styles';
import Header from '../../Header';
import Footer from '../../Footer';

class Page extends React.Component {
  render() {
    const { classes, children } = this.props;
    return (
      <div className={classes.container}>
        <Header />
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
