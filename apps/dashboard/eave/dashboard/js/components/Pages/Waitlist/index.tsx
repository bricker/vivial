import EaveSideBanner from "$eave-dashboard/js/components/EaveSideBanner";
import { textStyles } from "$eave-dashboard/js/theme";
import classNames from "classnames";
import React from "react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  container: {
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
  },

  subtitle: {
    fontSize: 36,
    color: "#535353",
    fontWeight: "normal",
  },
}));

const Waitlist = () => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <h1 className={text.display}> Unparalleled insights coming your way soon. </h1>
        <h2 className={classNames(text.headerII, text.gray)}>
          Unfortunately we don't currently support your tech stack, but we're working on it. You've been put on our
          waitlist and we'll follow up as soon as we can get you started!
        </h2>
      </div>
      <EaveSideBanner subtext="Questions? Comments? Feedback? We'd love to hear from you: info@eave.fyi" />
    </div>
  );
};

export default Waitlist;
