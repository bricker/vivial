import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React from "react";
import { imageUrl } from "../../../util/asset-util.js";
import Button from "../../Button/index.jsx";
import GoogleIcon from "../../Icons/GoogleIcon.jsx";
import Page from "../Page/index.jsx";

const makeClasses = makeStyles((theme) => ({
  container: {
    color: theme.palette.background.contrastText,
    width: "100vw",
    // height: "100%",
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    flexDirection: "column",
  },
  logo: {
    width: 100,
    height: 100,
    [theme.breakpoints.up("sm")]: {
      width: 150,
      height: 150,
    },
  },
  paddingBottom: {
    padding: "70px 25px",
    [theme.breakpoints.up("sm")]: {
      padding: "70px 60px",
    },
  },
  header: {
    color: "inherit",
    // color: theme.palette.tertiary.main,
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 22,
    [theme.breakpoints.up("md")]: {
      fontSize: 48,
      marginBottom: 28,
    },
  },
  subheader: {
    marginBottom: 30,
    color: "inherit",
  },
  loginButton: {
    color: theme.palette.background.contrastText,
    borderColor: theme.palette.background.contrastText,
    width: "100%",
    maxWidth: 240,
    marginTop: 12,
    justifyContent: "center",
    "&:hover": {
      borderColor: theme.palette.background.contrastText,
      backgroundColor: theme.palette.background.light,
    },
  },
  icon: {
    width: 30,
    height: 30,
  },
  disclaimer: {
    color: theme.palette.background.contrastText,
    margin: "39px auto 0px",
    display: "grid",
    textAlign: "center",
    maxWidth: 374,
    "& > a": {
      color: theme.palette.background.contrastText,
    },
  },
  authSwap: {
    color: "inherit",
    fontWeight: 700,
    font: "Roboto",
    fontSize: 16,
    padding: "70px 25px",
    [theme.breakpoints.up("sm")]: {
      fontSize: 20,
      padding: "70px 60px",
    },
  },
}));

const AuthenticationPage = ({ type }) => {
  const classes = makeClasses();
  // if !isLoginMode, then we are in sign up mode
  const isLoginMode = type === "login";
  const sectionClassList = classNames(
    classes.container,
    isLoginMode && classes.paddingBottom,
  );
  return (
    <Page simpleHeader={true} footer={false}>
      <section className={sectionClassList}>
        <img
          className={classes.logo}
          src={imageUrl("eave-logo-round-3x.png")}
        />
        <Typography variant="h2" className={classes.header}>
          {isLoginMode ? "Log In" : "Create your Free Account"}
        </Typography>
        <Typography variant="subtitle2" className={classes.subheader}>
          {isLoginMode
            ? "Welcome back to Eave!"
            : "Early access is available via Google sign up only. Additional account options coming soon."}
        </Typography>
        <Button
          to={`${window.eave.apiBase}/oauth/google/authorize`}
          className={classes.loginButton}
          variant="outlined"
          startIcon={<GoogleIcon className={classes.icon} />}
        >
          Continue with Google
        </Button>
        <Typography className={classes.disclaimer} variant="caption">
          {!isLoginMode && (
            <Typography variant="inherit">
              By clicking “Continue” above you agree to Eave's
            </Typography>
          )}
          <Typography variant="inherit">
            <a href="/terms" rel="noreferrer" target="_blank">
              TOS
            </a>{" "}
            and{" "}
            <a href="/privacy" rel="noreferrer" target="_blank">
              Privacy Policy.
            </a>
          </Typography>
        </Typography>
        <Typography className={classes.authSwap} variant="caption">
          {isLoginMode ? "New to Eave? " : "Already have an account? "}
          <a href={isLoginMode ? "/signup" : "/login"}>
            {isLoginMode ? "Create a free account" : "Log in"}
          </a>
        </Typography>
      </section>
    </Page>
  );
};

export default AuthenticationPage;
