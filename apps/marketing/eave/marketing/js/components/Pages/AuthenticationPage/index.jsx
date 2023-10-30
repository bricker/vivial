import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import { imageUrl } from "../../../util/asset-util.js";
import Button from "../../Button/index.jsx";
import GoogleIcon from "../../Icons/GoogleIcon.jsx";
import Page from "../Page/index.jsx";

const makeClasses = makeStyles((theme) => ({
  container: {
    color: theme.palette.background.contrastText,
    width: "100vw",
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    flexDirection: "column",
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 24,
    [theme.breakpoints.up("sm")]: {
      width: 150,
      height: 150,
      marginBottom: 18,
    },
  },
  header: {
    color: "inherit",
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 12,
    [theme.breakpoints.up("md")]: {
      fontSize: 48,
    },
  },
  subheader: {
    marginBottom: 36,
    textAlign: "center",
    color: "inherit",
  },
  loginButton: {
    color: theme.palette.background.contrastText,
    borderColor: theme.palette.background.contrastText,
    width: "100%",
    padding: "18px 54px",
    marginBottom: 54,
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
  link: {
    color: "#0092C7",
  },
  disclaimer: {
    color: theme.palette.background.contrastText,
    marginBottom: 72,
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
  },
}));

const AuthenticationPage = ({ type }) => {
  const classes = makeClasses();
  // if isLoginMode is false, then we are in sign up mode
  const isLoginMode = type === "login";
  return (
    <Page simpleHeader={true} footer={false}>
      <section className={classes.container}>
        <img
          className={classes.logo}
          src={imageUrl("eave-logo-round-3x.png")}
        />
        <Typography variant="h2" className={classes.header}>
          {isLoginMode ? "Log In" : "Create your Free Account"}
        </Typography>
        <Typography variant="subtitle2" className={classes.subheader}>
          {isLoginMode ? (
            "Welcome back to Eave!"
          ) : (
            <>
              Early access is available via Google sign up only.
              <br />
              Additional account options coming soon.
            </>
          )}
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
            <a
              className={classes.link}
              href="/terms"
              rel="noreferrer"
              target="_blank"
            >
              TOS
            </a>{" "}
            and{" "}
            <a
              className={classes.link}
              href="/privacy"
              rel="noreferrer"
              target="_blank"
            >
              Privacy Policy.
            </a>
          </Typography>
        </Typography>
        <Typography className={classes.authSwap} variant="caption">
          {isLoginMode ? "New to Eave? " : "Already have an account? "}
          <a className={classes.link} href={isLoginMode ? "/signup" : "/login"}>
            {isLoginMode ? "Create a free account" : "Log in"}
          </a>
        </Typography>
      </section>
    </Page>
  );
};

export default AuthenticationPage;
