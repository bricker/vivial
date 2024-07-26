import React from "react";
import { makeStyles } from "tss-react/mui";
import EaveSideBanner from "$eave-dashboard/js/components/EaveSideBanner";

const useStyles = makeStyles()(() => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
  content: {
    flex: 2,
    overflow: "auto",
    height: "100vh",
    paddingTop: 64,
    paddingLeft: 64,
    paddingRight: 64,
    // Currently not including padding in 2/3 size.
    boxSizing: "border-box",
  },
  title: {
    fontSize: 64,
    lineHeight: 1.1,
  },
  subtitle: {
    fontSize: 36,
    color: "#535353",
    fontWeight: "normal",
  },
}));

const Waitlist = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.main}>
      <div className={classes.content}>
        <h1 className={classes.title}> Unparalleled insights coming your way soon. </h1>
        <h2 className={classes.subtitle}>
          Unfortunately we don’t currently support your tech stack, but we’re working on it. You’ve been put on our
          waitlist and we’ll follow up as soon as we can get you started!
        </h2>
      </div>
      <EaveSideBanner />
    </div>
  );
};

export default Waitlist;
