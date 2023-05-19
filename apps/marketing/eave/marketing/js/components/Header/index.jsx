import React, { useState } from 'react';
import { makeStyles } from '@material-ui/styles';
import { IconButton, Drawer } from '@material-ui/core';

import { HEADER, AUTH_MODAL_STATE, FEEDBACK_URL } from '../../constants.js';
import useAuthModal from '../../hooks/useAuthModal.js';
import useUser from '../../hooks/useUser.js';
import HamburgerIcon from '../Icons/HamburgerIcon.js';
import CloseIcon from '../Icons/CloseIcon.js';
import Button from '../Button/index.jsx';
import EaveLogo from '../EaveLogo/index.jsx';

const makeClasses = makeStyles((theme) => ({
  outterContainer: {
    position: 'absolute',
    top: '0',
    width: '100%',
    zIndex: 100,
  },
  innerContainer: {
    height: HEADER.mobile.height,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0px 16px',
    maxWidth: 1440,
    margin: '0 auto',
    [theme.breakpoints.up('md')]: {
      height: HEADER.desktop.height,
      padding: '0px 46px',
    },
  },
  logoContainer: {
    paddingLeft: 10,
    [theme.breakpoints.up('md')]: {
      paddingLeft: 0,
    },
  },
  menuIconBtn: {
    padding: 0,
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
  mobileMenu: {
    width: '100vw',
    height: '100vh',
    backgroundColor: theme.palette.background.main,
  },
  mobileNav: {
    padding: '30px 26px',
  },
  mobileNavItem: {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    fontSize: 32,
    lineHeight: '37.5px',
    fontWeight: 400,
    display: 'block',
    padding: 0,
    margin: '0 0 12px',
    border: 'none',
    appearance: 'none',
    cursor: 'pointer',
    background: 'none',
  },
  ctaContainer: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'block',
      fontSize: 32,
    },
  },
  inlineButton: {
    display: 'inline-block',
    color: theme.typography.color.main,
    padding: 0,
    margin: '0 32px 0 0',
    border: 'none',
    appearance: 'none',
    cursor: 'pointer',
    background: 'none',
    fontSize: 16,
    lineHeight: '21px',
    fontWeight: 400,
    textDecoration: 'none',
  },
}));

const Header = ({ simpleHeader }) => {
  const classes = makeClasses();
  const [drawerIsOpen, setDrawerIsOpen] = useState(false);
  const { openModal } = useAuthModal();
  const { userState, logOut } = useUser();
  const { authenticated } = userState;

  const TopButtons = authenticated ? (
    <>
      <a className={classes.inlineButton} href={FEEDBACK_URL} target="_blank" rel="noreferrer">
        Send Feedback
      </a>
      <button className={classes.inlineButton} onClick={logOut}>
        Log Out
      </button>
    </>

  ) : (
    <>
      <button className={classes.inlineButton} onClick={ () => openModal(AUTH_MODAL_STATE.LOGIN) }>
        Log In
      </button>
      <Button onClick={ () => openModal(AUTH_MODAL_STATE.SIGNUP) }>
        Get Early Access
      </Button>
    </>
  );

  const navButtons = authenticated ? (
    <>
      <a className={classes.mobileNavItem} href={FEEDBACK_URL} target="_blank" rel="noreferrer">
        Send Feedback
      </a>
      <button className={classes.mobileNavItem} onClick={logOut}>
        Log Out
      </button>
    </>

  ) : (
    <>
      <button className={classes.mobileNavItem} onClick={ () => openModal(AUTH_MODAL_STATE.LOGIN) }>
        Log In
      </button>
      <button className={classes.mobileNavItem} onClick={ () => openModal(AUTH_MODAL_STATE.SIGNUP) }>
        Get Early Access
      </button>
    </>
  );

  return (
    <header className={classes.outterContainer}>
      <div className={classes.innerContainer}>
        <div className={classes.logoContainer}>
          <EaveLogo />
        </div>
        {!simpleHeader && (
          <>
            <div className={classes.ctaContainer}>
              {TopButtons}
            </div>
            <IconButton
              classes={{ root: classes.menuIconBtn }}
              onClick={() => setDrawerIsOpen(true)}
            >
              <HamburgerIcon />
            </IconButton>
            <Drawer open={drawerIsOpen} anchor="right" transitionDuration={600}>
              <div className={classes.mobileMenu}>
                <div className={classes.innerContainer}>
                  <div className={classes.logoContainer}>
                    <EaveLogo />
                  </div>
                  <IconButton
                    classes={{ root: classes.menuIconBtn }}
                    onClick={() => setDrawerIsOpen(false)}
                  >
                    <CloseIcon />
                  </IconButton>
                </div>
                <nav className={classes.mobileNav}>
                  {navButtons}
                </nav>
              </div>
            </Drawer>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;
