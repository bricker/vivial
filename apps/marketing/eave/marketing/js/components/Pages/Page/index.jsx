import React from 'react';
import { makeStyles } from '@material-ui/styles';

import Header from '../../Header/index.jsx';
import Footer from '../../Footer/index.jsx';
import AuthModal from '../../AuthModal/index.jsx';

const makeClasses = makeStyles((theme) => ({
  container: {
    backgroundColor: theme.palette.background.main,
    fontFamily: theme.typography.fontFamily,
    position: 'relative',
    minHeight: '100vh',
  },
}));

const Page = ({ children, simpleHeader, hideFooter }) => {
  const classes = makeClasses();
  return (
    <div className={classes.container}>
      <Header simpleHeader={simpleHeader} />
      {children}
      {!hideFooter && <Footer />}
      <AuthModal />
    </div>
  );
};

export default Page;
