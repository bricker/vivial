import EaveBlueIcon from "$eave-dashboard/js/components/Icons/EaveBlueIcon";
import React from "react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  sidebar: {
    flex: 1,
    borderRadius: 20,
    margin: 16,
    color: "white",
    display: "flex",
    maxWidth: 700,
    backgroundColor: theme.palette.success.main,
    flexDirection: "column",
    overflow: "hidden",
    position: "relative",
  },
  textContainer: {
    paddingLeft: 32,
    paddingRight: 32,
  },
  title: {
    fontSize: 52,
    // border: "2px solid black",
    marginBottom: 16,
    lineHeight: 1.1,
  },
  subtext: {
    width: 256,
    fontSize: 20,
    marginTop: 0,
    // border: "2px solid black",
  },
  logo: {
    position: "absolute",
    bottom: -40,
    right: -20,
    width: 300,
    height: "auto",
  },
}));

export default function SideBanner() {
  const { classes } = useStyles();

  return (
    <div className={classes.sidebar}>
      <div className={classes.textContainer}>
        <h1 className={classes.title}>Eave Technologies</h1>
        <h3 className={classes.subtext}>You're a few clicks away from automated insights.</h3>
      </div>
      <div className={classes.logo}>
        <EaveBlueIcon />
      </div>
    </div>
  );
}
