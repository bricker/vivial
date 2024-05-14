import Button from "$eave-dashboard/js/components/Button";
import GoogleIcon from "$eave-dashboard/js/components/Icons/GoogleIcon";
import { eaveWindow } from "$eave-dashboard/js/types";
import { imageUrl } from "$eave-dashboard/js/util/asset-util";
import { Typography } from "@mui/material";
import React from "react";
import { makeStyles } from "tss-react/mui";
import Page from "../Page/index";

const makeClasses = makeStyles()((theme) => ({
  container: {
    color: theme.palette.background.contrastText,
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    flexDirection: "column",
    padding: "0px 25px 20px",
    [theme.breakpoints.up("sm")]: {
      padding: "0px 60px 20px",
    },
  },
  logo: {
    height: 120,
    marginBottom: 18,
    [theme.breakpoints.down("sm")]: {
      marginBottom: 24,
      height: 100,
    },
  },
  header: {
    color: "inherit",
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 12,
    textAlign: "center",
    [theme.breakpoints.up("md")]: {
      fontSize: 42,
    },
  },
  subheader: {
    marginBottom: 36,
    textAlign: "center",
    color: "inherit",
    fontSize: 16,
    [theme.breakpoints.up("md")]: {
      fontSize: 18,
    },
  },
  loginButton: {
    color: theme.palette.background.contrastText,
    borderColor: theme.palette.background.contrastText,
    width: "100%",
    padding: "34px 54px",
    marginBottom: 54,
    justifyContent: "center",
    "&:hover": {
      borderColor: theme.palette.background.contrastText,
      backgroundColor: theme.palette.background.light,
    },
    fontSize: 16,
    [theme.breakpoints.up("md")]: {
      fontSize: 20,
    },
  },
  authIcon: {
    width: 30,
    height: 30,
  },
  link: {
    color: "#0092C7",
  },
  disclaimer: {
    color: theme.palette.background.contrastText,
    marginBottom: 60,
    display: "grid",
    textAlign: "center",
    maxWidth: 400,
    "& > a": {
      color: theme.palette.background.contrastText,
    },
    fontSize: 16,
    [theme.breakpoints.up("md")]: {
      fontSize: 18,
    },
  },
  authSwap: {
    color: "inherit",
    fontWeight: 700,
    fontSize: 16,
    [theme.breakpoints.up("md")]: {
      fontSize: 18,
    },
  },
}));

const AuthenticationPage = ({ type }: { type: "signup" | "login" }) => {
  const { classes } = makeClasses();
  // if isLoginMode is false, then we are in sign up mode
  const isLoginMode = type === "login";
  return (
    <Page>
      <section className={classes.container}>
        <img className={classes.logo} src={imageUrl("eave-logo-round.svg")} />
        <Typography variant="h2" className={classes.header}>
          {isLoginMode ? "Log In" : "Create your Free Account"}
        </Typography>
        <Typography variant="subtitle2" className={classes.subheader}>
          {isLoginMode
            ? "Welcome back to Eave!"
            : "Early access is only available via Google. Additional account options coming soon."}
        </Typography>
        <Button
          to={`${eaveWindow.eave.apiBase}/oauth/google/authorize`}
          className={classes.loginButton}
          variant="outlined"
          startIcon={<GoogleIcon className={classes.authIcon} />}
        >
          <>Continue with Google</>
        </Button>
        <Typography className={classes.disclaimer} variant="caption">
          {!isLoginMode && (
            <Typography variant="inherit">
              By clicking “Continue” you agree to Eave's
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
