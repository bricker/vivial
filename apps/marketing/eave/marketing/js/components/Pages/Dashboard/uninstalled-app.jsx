// @ts-check
import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import { imageUrl } from "../../../util/asset-util.js";
import Button from "../../Button/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  container: {
    display: "flex",
    flexDirection: "column",
  },
  title: {
    fontSize: 28,
    fontWeight: 400,
    [theme.breakpoints.up("sm")]: {
      fontSize: 36,
    },
  },
  subtitle: {
    fontSize: 16,
    fontWeight: 400,
    [theme.breakpoints.up("sm")]: {
      fontSize: 18,
    },
  },
  ctaBtn: {
    padding: "18px 54px",
  },
  installFlowContainer: {
    display: "flex",
    flexDirection: "row",
  },
  installItemContainer: {
    display: "flex",
    flexDirection: "column",
  },
  featureContainer: {
    display: "flex",
    flexDirection: "row",
  },
  feature: {
    borderWidth: 1,
    borderColor: "gray",
    color: "gray",
  },
}));

const featureText = {
  apiDocs: {
    title: "API Documentation",
    subtitle:
      "Eave finds APIs, writes industry standard documentation, and keeps it updated.",
    // TODO: currently supports section.. need <li> in grid
  },
  codeDocs: {
    title: "Inline Code Documentation",
    subtitle:
      "Eave adds inline function documentation to your code on every merge.",
    // TODO: supports section
  },
};

const UninstalledGithubAppDash = () => {
  const classes = makeClasses();
  /** @type {Types.GlobalEave} */
  // @ts-ignore
  const _globalEave = window;

  const githubOauthUrl = `${_globalEave.eave.apiBase}/oauth/github/authorize`;

  const Step = ({ /** @type {string} */ src, /** @type {string} */ text }) => {
    return (
      <div className={classes.installItemContainer}>
        <img src={imageUrl(src)} />
        <Typography className="">{text}</Typography>
      </div>
    );
  };

  const FeatureDescription = ({
    /** @type {string} */ title,
    /** @type {string} */ subtitle,
  }) => {
    return (
      <div className={classes.feature}>
        <img src={imageUrl("lock")} /> {/* TODO */}
        <Typography>{title}</Typography>
        <Typography>{subtitle}</Typography>
        <Typography>
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
      <Button
        to={githubOauthUrl}
        className={classes.ctaBtn}
        color="secondary"
      >
        Add App
      </Button>
      <div className={classes.installFlowContainer}>
        <Step src="eave-logo-round-3x.png" text="Add the Eave App to GitHub" />
        <img src={imageUrl("arrow")} /> {/*TODO*/}
        <Step
          src="eave-logo-round-3x.png"
          text="Eave Detects Documentation Needs"
        />
        <img src={imageUrl("arrow")} />
        <Step
          src="eave-logo-round-3x.png"
          text="Eave Adds Docs to your Codebase in a PR"
        />
        <img src={imageUrl("arrow")} />
        <Step src="eave-logo-round-3x.png" text="Your Docs Always Up to Date" />
      </div>
      <Typography>✨ Add App to Access Features ✨</Typography>
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
