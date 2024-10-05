import React from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()((theme) => ({
  outerContainer: {
    marginBottom: theme.header.marginBottom,
    width: "100%",
    zIndex: 100,
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
}));

const Header = () => {
  const { classes } = makeClasses();

  return (
    <header className={classes.outerContainer}>
      <div className={classes.innerContainer}>
        <div className={classes.logoContainer}>
          VIVIAL
        </div>
      </div>
    </header>
  );
};

export default Header;
