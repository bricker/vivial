import React from 'react';
import { Dialog, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

import useLoginModal from '../../hooks/useLoginModal.js';
import Copy from '../Copy/index.js';
import CloseIcon from '../Icons/CloseIcon.js';

const makeClasses = makeStyles((theme) => ({
  container: {
    minWidth: 546,
    fontFamily: theme.typography.fontFamily.main,
    fontColor: theme.typography.color.dark,
    padding: 21,
    boxSizing: 'borderBox'
  },
}));

const AuthModal = () => {
  const { isOpen, isLoginMode, isSignupMode } = useLoginModal();
  const classes = makeClasses();

  return (
    <Dialog open={isOpen}>
      <section className={classes.container}>
        <span>
          <CloseIcon className={classes.closeButton}/>
        </span>
        <Copy variant="h2">{isLoginMode ? 'Log In' : 'Get Free Early Access'}</Copy>
        <Copy variant="psmall">{isLoginMode ? 'Access your free Beta account' : 'Early access is available via Google sign up only. Additional account options coming soon.'}</Copy>
        <button>Continue with Google</button>
        <button>Continue with Slack</button>
        {isSignupMode &&(
          <Copy>By clicking on “Continue with Google”, you agree to Eave’s TOS and Privacy Policy.</Copy>
        )}
      </section>

    </Dialog>
  );
};

export default AuthModal;
