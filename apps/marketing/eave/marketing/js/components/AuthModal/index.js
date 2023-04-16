import React from 'react';
import { Dialog, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import { Link } from 'react-router-dom';

import useAuthModal from '../../hooks/useAuthModal.js';
import Copy from '../Copy/index.js';
import CloseIcon from '../Icons/CloseIcon.js';
import Button from '../Button/index.js';
import useUser from '../../hooks/useUser.js';

const makeClasses = makeStyles((theme) => ({
  container: {
    minWidth: 546,
    fontFamily: theme.typography.fontFamily.main,
    color: theme.typography.color.dark,
    padding: '70px 60px 36px',
    boxSizing: 'border-box',
    position: 'relative',
    textAlign: 'center',
  },
  closeButton: {
    position: 'absolute',
    top: 21,
    right: 21,
  },
  subheader: {
    marginBottom: 42,
  },
  disclaimer: {
    margin: '39px auto 0px',
    maxWidth: 374,
  },
}));

const AuthModal = () => {
  const classes = makeClasses();
  const { isOpen, isLoginMode, isSignupMode, closeModal } = useAuthModal();
  const { logIn } = useUser();

  return (
    <Dialog open={isOpen}>
      <section className={classes.container}>
        <IconButton onClick={closeModal} className={classes.closeButton}>
         <CloseIcon />
        </IconButton>
        <Copy variant="h2">{isLoginMode ? 'Log In' : 'Get Free Early Access'}</Copy>
        <Copy variant="pSmall" className={classes.subheader}>{isLoginMode ? 'Access your free Beta account' : 'Early access is available via Google and Slack sign up only. Additional account options coming soon.'}</Copy>
        <Button onClick={logIn}>Continue with Google</Button>
        <Button onClick={logIn}>Continue with Slack</Button>
        {isSignupMode && (
          <Copy className={classes.disclaimer} variant="pXSmall">By clicking “Continue with Google” or “Continue with Slack”, you agree to Eave’s <Link onClick={closeModal} to="/terms">TOS</Link>  and Privacy Policy.</Copy>
        )}
      </section>
    </Dialog>
  );
};

export default AuthModal;
