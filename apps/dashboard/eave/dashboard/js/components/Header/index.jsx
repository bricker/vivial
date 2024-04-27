// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../types.js"; // eslint-disable-line no-unused-vars
import EaveLogo from "../EaveLogo/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  outerContainer: {
    marginBottom: theme["header"].marginBottom,
    width: "100%",
    zIndex: 100,
  },
  innerContainer: {
    height: theme["header"].height,
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    padding: "16px",
    maxWidth: 1440,
    margin: "0 auto",
    [theme.breakpoints.up("md")]: {
      height: theme["header"].md.height,
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
}));

const Header = () => {
  const classes = makeClasses();

  return (
    <header className={classes.outerContainer}>
      <div className={classes.innerContainer}>
        <div className={classes.logoContainer}>
          <EaveLogo />
        </div>
      </div>
    </header>
  );
};

export default Header;
