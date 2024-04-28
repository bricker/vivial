import { imageUrl } from "$eave-dashboard/js/util/asset-util";
import React from "react";
import { Link } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()((theme) => ({
  logoContainer: {
    display: "inline-block",
    lineHeight: 0,
    width: 66,
    [theme.breakpoints.up("md")]: {
      width: 88,
    },
  },
  logo: {
    width: "100%",
  },
}));

const EaveLogo = () => {
  const { classes } = makeClasses();
  return (
    <Link className={classes.logoContainer} to="/">
      <img className={classes.logo} src={imageUrl("eave-logo-beta.png")} />
    </Link>
  );
};

export default EaveLogo;
