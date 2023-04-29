import React from 'react';
import { makeStyles } from '@material-ui/styles';

import Header from '../../Header/index.js';
import Footer from '../../Footer/index.js';
import AuthModal from '../../AuthModal/index.jsx';

const makeClasses = makeStyles((theme) => ({
  container: {
    position: 'relative',
    minHeight: '100vh',
    fontFamily: theme.typography.fontFamily.main,
    color: theme.typography.color.main,
    backgroundColor: theme.palette.background.main,
  },
}));

const Page = ({ children, simpleHeader }) => {
  const classes = makeClasses();
  return (
    <div className={classes.container}>
      <Header simpleHeader={simpleHeader} />
      {children}
      <Footer />
      <AuthModal />
    </div>
  );
};

export default Page;
