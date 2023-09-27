import { Drawer, IconButton } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React, { useState } from "react";
import { Link } from "react-router-dom";

import { AUTH_MODAL_STATE, FEEDBACK_URL } from "../../constants.js";
import useAuthModal from "../../hooks/useAuthModal.js";
import useUser from "../../hooks/useUser.js";
import Button from "../Button/index.jsx";
import EaveLogo from "../EaveLogo/index.jsx";
import CloseIcon from "../Icons/CloseIcon.js";
import HamburgerIcon from "../Icons/HamburgerIcon.js";

const makeClasses = makeStyles((theme) => ({
  outterContainer: {
    marginBottom: theme.header.marginBottom,
    width: "100%",
    zIndex: 100,
    [theme.breakpoints.up("md")]: {
      marginBottom: theme.header.md.marginBottom,
    },
  },
  innerContainer: {
    height: theme.header.height,
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    padding: "16px",
    maxWidth: 1440,
    margin: "0 auto",
    [theme.breakpoints.up("md")]: {
      height: theme.header.md.height,
      alignItems: "center",
      padding: "0px 46px",
    },
  },
  logoContainer: {
    paddingLeft: 10,
    lineHeight: 0,
    [theme.breakpoints.up("md")]: {
      paddingLeft: 0,
    },
  },
  menuIconBtn: {
    padding: 0,
    [theme.breakpoints.up("md")]: {
      display: "none",
    },
  },
  mobileMenu: {
    backgroundColor: theme.palette.background.main,
    width: "100vw",
    height: "100vh",
  },
  mobileNav: {
    padding: "0px 25px",
  },
  mobileNavItem: {
    color: theme.palette.background.contrastText,
    textDecoration: "none",
    fontSize: 32,
    lineHeight: "37.5px",
    fontWeight: 400,
    display: "block",
    padding: 0,
    margin: "0 0 32px",
    border: "none",
    appearance: "none",
    cursor: "pointer",
    background: "none",
  },
  ctaContainer: {
    display: "none",
    [theme.breakpoints.up("md")]: {
      display: "block",
      fontSize: 32,
    },
  },
  button: {
    fontWeight: 700,
  },
  inlineButton: {
    color: theme.palette.background.contrastText,
    display: "inline-block",
    padding: "0px 32px",
    border: "none",
    appearance: "none",
    cursor: "pointer",
    background: "none",
    fontSize: 16,
    lineHeight: "21px",
    fontWeight: 700,
    textDecoration: "none",
  },
}));

const Header = ({ simpleHeader }) => {
  const classes = makeClasses();
  const [drawerIsOpen, setDrawerIsOpen] = useState(false);
  const { openModal } = useAuthModal();
  const { user, logUserOut } = useUser();
  const { isAuthenticated } = user;

  const TopButtons = isAuthenticated ? (
    <>
      <a
        className={classes.inlineButton}
        href={FEEDBACK_URL}
        target="_blank"
        rel="noreferrer"
      >
        Send Feedback
      </a>
      <button className={classes.inlineButton} onClick={logUserOut}>
        Log Out
      </button>
    </>
  ) : (
    <>
      <button
        className={classes.inlineButton}
        onClick={() => openModal(AUTH_MODAL_STATE.LOGIN)}
      >
        Log In
      </button>
      <Button
        className={classes.button}
        onClick={() => openModal(AUTH_MODAL_STATE.SIGNUP)}
      >
        Sign Up
      </Button>
    </>
  );

  const navButtons = isAuthenticated ? (
    <>
      <Link className={classes.mobileNavItem} to="/dashboard">
        Dashboard
      </Link>
      <a
        className={classes.mobileNavItem}
        href={FEEDBACK_URL}
        target="_blank"
        rel="noreferrer"
      >
        Send Feedback
      </a>
      <button className={classes.mobileNavItem} onClick={logUserOut}>
        Log Out
      </button>
    </>
  ) : (
    <>
      <button
        className={classes.mobileNavItem}
        onClick={() => openModal(AUTH_MODAL_STATE.LOGIN)}
      >
        Log In
      </button>
      <button
        className={classes.mobileNavItem}
        onClick={() => openModal(AUTH_MODAL_STATE.SIGNUP)}
      >
        Sign Up
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
            <div className={classes.ctaContainer}>{TopButtons}</div>
            <IconButton
              classes={{ root: classes.menuIconBtn }}
              onClick={() => setDrawerIsOpen(true)}
            >
              <HamburgerIcon />
            </IconButton>
            <Drawer open={drawerIsOpen} anchor="right" transitionDuration={600}>
              <div className={classes.mobileMenu}>
                <div className={classes.outterContainer}>
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
                </div>
                <nav className={classes.mobileNav}>{navButtons}</nav>
              </div>
            </Drawer>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;
