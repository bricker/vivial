// @ts-check
import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import { imageUrl } from "../../../util/asset-util.js";
import Button from "../../Button/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  container: {
    padding: 30,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    // @ts-ignore
    color: theme.palette.background.contrastText,
  },
  title: {
    textAlign: "center",
    fontSize: 28,
    [theme.breakpoints.up("sm")]: {
      fontSize: 36,
    },
    marginBottom: 12,
  },
  subtitle: {
    maxWidth: 580,
    textAlign: "center",
    fontSize: 16,
    [theme.breakpoints.up("sm")]: {
      fontSize: 18,
    },
    marginBottom: 36,
  },
  caption: {
    fontSize: 14,
    [theme.breakpoints.up("sm")]: {
      fontSize: 16,
    },
  },
  ctaBtn: {
    color: theme.palette.secondary.contrastText,
    padding: "12px 90px",
    borderRadius: "20px",
    fontSize: 24,
    [theme.breakpoints.up("sm")]: {
      fontSize: 32,
      padding: "12px 120px",
    },
    marginBottom: 42,
  },
  installFlowContainer: {
    display: "flex",
    flexDirection: "row",
    marginBottom: 90,
  },
  installItemContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    maxWidth: 180,
    textAlign: "center",
  },
  installItemImage: {
    height: 54,
    width: 54,
    marginBottom: 6,
  },
  installFlowArrowImage: {
    width: 68,
    height: "auto",
    position: "relative",
    bottom: 24,
  },
  featureSubheader: {
    fontSize: 18,
    marginBottom: 24,
  },
  featureContainer: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 72,
    [theme.breakpoints.down("sm")]: {
      flexDirection: "column",
      marginBottom: 36,
    },
  },
  featureDescriptionBlock: {
    padding: "0px 24px 24px 24px",
    margin: 18,
    maxWidth: 368,
    borderStyle: "solid",
    borderWidth: "2px",
    // @ts-ignore
    borderColor: theme.palette.disabled.dark,
    // @ts-ignore
    color: theme.palette.disabled.dark,
    display: "flex",
    flexDirection: "column",
  },
  featureLockIcon: {
    height: 35,
    alignSelf: "center",
    position: "relative",
    bottom: 23,
  },
  featureDescriptionHeader: {
    fontSize: 20,
    fontWeight: 700,
    [theme.breakpoints.up("sm")]: {
      fontSize: 22,
    },
    textAlign: "center",
    marginBottom: 12,
  },
}));

const featureText = {
  apiDocs: {
    title: "API Documentation",
    subtitle:
      "Eave finds APIs, writes industry standard documentation, and keeps it updated.",
    // TODO: currently supports section.. need <li> in grid (or flex)
  },
  codeDocs: {
    title: "Inline Code Documentation",
    subtitle:
      "Eave adds inline function documentation to your code on every merge.",
    // TODO: supports section
  },
};

const UninstalledGithubAppDash = () => {
  // TODO: mobile layout changes

  const classes = makeClasses();
  /** @type {Types.GlobalEave} */
  // @ts-ignore
  const _globalEave = window;

  const githubOauthUrl = `${_globalEave.eave.apiBase}/oauth/github/authorize`;

  const Step = ({ /** @type {string} */ src, /** @type {string} */ text }) => {
    return (
      <div className={classes.installItemContainer}>
        <img src={imageUrl(src)} className={classes.installItemImage} />
        <Typography className={classes.caption}>{text}</Typography>
      </div>
    );
  };

  const FeatureDescription = ({
    /** @type {string} */ title,
    /** @type {string} */ subtitle,
  }) => {
    return (
      <div className={classes.featureDescriptionBlock}>
        <img className={classes.featureLockIcon} src={imageUrl("lock.svg")} />
        <Typography className={classes.featureDescriptionHeader}>
          {title}
        </Typography>
        <Typography className={classes.caption}>{subtitle}</Typography>
        <Typography className={classes.caption}>
          Currently supports:
          <br />
          TODO lang list etc
        </Typography>
      </div>
    );
  };

  return (
    <div className={classes.container}>
      <Typography className={classes.title}>
        Welcome to Better Documentation
      </Typography>
      <Typography className={classes.subtitle}>
        The only thing you need to do is click the button below to add the Eave
        GitHub app, and Eave will do the rest.
      </Typography>
      <Button to={githubOauthUrl} className={classes.ctaBtn} color="secondary">
        Add App
      </Button>
      <div className={classes.installFlowContainer}>
        <Step src="github-icon.svg" text="Add the Eave App to GitHub" />
        <img
          src={imageUrl("arrow.svg")}
          className={classes.installFlowArrowImage}
        />
        <Step
          src="eave-logo-round.svg"
          text="Eave Detects Documentation Needs"
        />
        <img
          src={imageUrl("arrow.svg")}
          className={classes.installFlowArrowImage}
        />
        <Step
          src="pr-merge-circle-icon.svg"
          text="Eave Adds Docs to your Codebase in a PR"
        />
        <img
          src={imageUrl("arrow.svg")}
          className={classes.installFlowArrowImage}
        />
        <Step src="code-block-circle-icon.svg" text="Your Docs Always Up to Date" />
      </div>
      <Typography className={classes.featureSubheader}>
        ✨ Add App to Access Features ✨
      </Typography>
      <div className={classes.featureContainer}>
        <FeatureDescription
          title={featureText.apiDocs.title}
          subtitle={featureText.apiDocs.subtitle}
        />
        <FeatureDescription
          title={featureText.codeDocs.title}
          subtitle={featureText.codeDocs.subtitle}
        />
      </div>
    </div>
  );
};

export default UninstalledGithubAppDash;
