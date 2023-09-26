import { makeStyles } from "@material-ui/styles";
import React from "react";

import { INTEGRATION_LOGOS } from "../../../constants.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  wrapper: {
    [theme.breakpoints.up("md")]: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      flexDirection: "row",
    },
  },
  copy: {
    marginBottom: 15,
    [theme.breakpoints.up("sm")]: {
      padding: 0,
    },
    [theme.breakpoints.up("lg")]: {
      width: 409,
      minWidth: 409,
      marginBottom: 0,
    },
  },
  logos: {
    display: "flex",
    width: "100%",
    maxWidth: 374,
    alignItems: "center",
    margin: "0 auto",
    justifyContent: "space-between",
    [theme.breakpoints.up("md")]: {
      maxWidth: 738,
      margin: "0 0 0 24px",
    },
    [theme.breakpoints.up("lg")]: {
      maxWidth: "unset",
      marginLeft: "5%",
    },
  },
  slack: {
    width: 84,
    [theme.breakpoints.up("lg")]: {
      width: 168,
    },
  },
  github: {
    width: 57,
    [theme.breakpoints.up("lg")]: {
      width: 103,
    },
  },
  jira: {
    width: 116,
    [theme.breakpoints.up("lg")]: {
      width: 232,
    },
  },
}));

const IntegrationsBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <PageSection alternateBackground wrapperClassName={classes.wrapper}>
      <div className={classes.copy}>
        <Copy variant="h2">{title}</Copy>
        <Copy variant="pSmall">{subtitle}</Copy>
      </div>
      <div className={classes.logos}>
        <img className={classes.slack} src={INTEGRATION_LOGOS.slack.src} alt={INTEGRATION_LOGOS.slack.alt} />
        <img className={classes.github} src={INTEGRATION_LOGOS.github.src} alt={INTEGRATION_LOGOS.github.alt} />
        <img className={classes.jira} src={INTEGRATION_LOGOS.jira.src} alt={INTEGRATION_LOGOS.jira.alt} />
      </div>
    </PageSection>
  );
};

export default IntegrationsBanner;
