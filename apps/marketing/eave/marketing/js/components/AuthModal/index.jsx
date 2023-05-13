import React from 'react';
import { Dialog, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import classNames from 'classnames';

import useAuthModal from '../../hooks/useAuthModal.js';
import Copy from '../Copy/index.jsx';
import CloseIcon from '../Icons/CloseIcon.js';
import Button from '../Button/index.jsx';
import GoogleIcon from '../Icons/GoogleIcon.jsx';
import SlackIcon from '../Icons/SlackIcon.jsx';

const makeClasses = makeStyles((theme) => ({
  container: {
    maxWidth: 546,
    color: theme.typography.color.dark,
    padding: '70px 25px 36px',
    boxSizing: 'border-box',
    position: 'relative',
    textAlign: 'center',
    [theme.breakpoints.up('sm')]: {
      padding: '70px 60px 36px',
    },
  },
  paddingBottom: {
    padding: '70px 25px',
    [theme.breakpoints.up('sm')]: {
      padding: '70px 60px',
    },
  },
  closeButton: {
    position: 'absolute',
    top: 21,
    right: 21,
    padding: 0,
  },
  subheader: {
    marginBottom: 30,
  },
  loginButton: {
    maxWidth: 323,
    width: '100%',
    color: theme.typography.color.dark,
    marginTop: 12,
    justifyContent: 'flex-start',
    paddingLeft: 30,
    border: `1px solid ${theme.typography.color.dark}`,
  },
  icon: {
    width: 30,
    height: 30,
  },
  disclaimer: {
    margin: '39px auto 0px',
    maxWidth: 374,
  },
}));

const AuthModal = () => {
  const classes = makeClasses();
  const { isOpen, isLoginMode, isSignupMode, closeModal } = useAuthModal();
  const sectionClassList = classNames(classes.container, isLoginMode && classes.paddingBottom);

  return (
    <Dialog open={isOpen}>
      <section className={sectionClassList}>
        <IconButton onClick={closeModal} className={classes.closeButton}>
          <CloseIcon />
        </IconButton>
        <Copy variant="h2">{isLoginMode ? 'Log In' : 'Get Free Early Access'}</Copy>
        <Copy variant="pSmall" className={classes.subheader}>{isLoginMode ? 'Access your free Beta account' : 'Early access is available via Google and Slack sign up only. Additional account options coming soon.'}</Copy>
        <Button
          to={`${window.eave.apiBase}/oauth/google/authorize`}
          className={classes.loginButton}
          variant="outlined"
          startIcon={<GoogleIcon className={classes.icon} />}
          lg
        >
          Continue with Google
        </Button>
        <Button
          to={`${window.eave.apiBase}/oauth/slack/authorize`}
          className={classes.loginButton}
          variant="outlined"
          startIcon={<SlackIcon className={classes.icon} />}
          lg
        >
          Continue with Slack
        </Button>
        {isSignupMode && (
          <Copy className={classes.disclaimer} variant="footnote">
            By clicking “Continue with Google” or “Continue with Slack”, you agree to Eave’s{' '}
            <a
              href="/terms"
              rel="noreferrer"
              target="_blank"
            >
                TOS
            </a> and{' '}
            <a
              href="/privacy"
              rel="noreferrer"
              target="_blank"
            >
                Privacy Policy.
            </a>
          </Copy>
        )}
      </section>
    </Dialog>
  );
};

export default AuthModal;
