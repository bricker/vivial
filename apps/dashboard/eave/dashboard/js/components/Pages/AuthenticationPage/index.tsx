import Button from "$eave-dashboard/js/components/Button";
import EaveSideBanner, { BannerStyle } from "$eave-dashboard/js/components/EaveSideBanner";
import GoogleIcon from "$eave-dashboard/js/components/Icons/GoogleIcon";
import { eaveWindow } from "$eave-dashboard/js/types";
import { Typography } from "@mui/material";
import React from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()((theme) => ({
  container: {
    display: "flex",
    flexDirection: "row",
    backgroundColor: "#EEEEEE",
  },
  textBoxContainer: {
    flex: 2,
    width: "100vw",
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  textBox: {
    backgroundColor: "#FDFDFD",
    borderRadius: 20,
    width: "70%",
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    flexDirection: "column",
    padding: "0px 25px 20px",
    [theme.breakpoints.up("sm")]: {
      padding: "0px 60px 20px",
    },
  },
  header: {
    color: "#585858",
    marginTop: 60,
    marginBottom: 24,
    textAlign: "center",
  },
  subheader: {
    color: "#7D7D7D",
    marginBottom: 8,
    textAlign: "center",
  },
  loginButton: {
    color: "#0000008A",
    borderColor: "#EEEEEE",
    borderRadius: 10,
    fontWeight: "bold",
    padding: "16px 64px",
    marginBottom: 16,
    justifyContent: "center",
    "&:hover": {
      boxShadow: "0px 0px 3px 0px #00000015",
    },
    boxShadow: "0px 2px 3px 0px #0000002B",
  },
  authIcon: {
    width: 24,
    height: 24,
  },
  link: {
    color: "#0092C7",
  },
  disclaimer: {
    color: "#7D7D7D",
    marginBottom: 60,
    display: "grid",
    textAlign: "center",
    maxWidth: 400,
  },
}));

const AuthenticationPage = ({ type }: { type: "signup" | "login" }) => {
  const { classes } = makeClasses();
  // if isLoginMode is false, then we are in sign up mode
  const isLoginMode = type === "login";
  return (
    <div className={classes.container}>
      <div className={classes.textBoxContainer}>
        <section className={classes.textBox}>
          <Typography variant="h4" className={classes.header}>
            Insights with Eave. No credit cards, <span style={{ color: "black" }}>no commitments.</span>
          </Typography>
          <Typography variant="subtitle2" className={classes.subheader}>
            Join using your work email
          </Typography>
          <Button
            to={`${eaveWindow.eavedash.apiBase}/oauth/google/authorize`}
            className={classes.loginButton}
            variant="outlined"
            startIcon={<GoogleIcon className={classes.authIcon} />}
          >
            Continue with Google
          </Button>
          <Typography className={classes.disclaimer} variant="caption">
            {!isLoginMode && (
              <Typography variant="inherit">By clicking “Continue” above, you agree to Eave's</Typography>
            )}
            <Typography variant="inherit">
              {" "}
              <a className={classes.link} href="https://www.eave.fyi/terms" rel="noreferrer" target="_blank">
                TOS
              </a>{" "}
              and{" "}
              <a className={classes.link} href="https://www.eave.fyi/privacy" rel="noreferrer" target="_blank">
                Privacy Policy.
              </a>
            </Typography>
          </Typography>
        </section>
      </div>
      <EaveSideBanner
        style={BannerStyle.FULL}
        subtext="Create an account today and get your free AI feature report in minutes."
      />
    </div>
  );
};

export default AuthenticationPage;
