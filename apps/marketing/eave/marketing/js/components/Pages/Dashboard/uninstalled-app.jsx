// @ts-check
import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
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
    [theme.breakpoints.down("sm")]: {
      lineHeight: "34px",
    },
    [theme.breakpoints.up("sm")]: {
      fontSize: 36,
    },
    marginBottom: 12,
  },
  subtitle: {
    maxWidth: 580,
    textAlign: "center",
    fontSize: 16,
    [theme.breakpoints.down("sm")]: {
      lineHeight: "21px",
    },
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
  installFlowContainerDesktop: {
    display: "flex",
    flexDirection: "row",
    marginBottom: 90,
    [theme.breakpoints.down("sm")]: {
      display: "none",
    },
  },
  installFlowContainerMobile: {
    display: "none",
    [theme.breakpoints.down("sm")]: {
      display: "grid",
      gridTemplateAreas: `'b1 b1 b1 . . b2 b2 b2'
        'b1 b1 b1 a1 a1 b2 b2 b2'
        'b1 b1 b1 . . b2 b2 b2'
        '. . . . . . a2 .'
        '. . . . . . a2 .'
        'b4 b4 b4 . . b3 b3 b3'
        'b4 b4 b4 a3 a3 b3 b3 b3'
        'b4 b4 b4 . . b3 b3 b3'`,
      gap: 20,
      marginBottom: 72,
    },
  },
  gridAreaBox1: {
    gridArea: "b1",
  },
  gridAreaBox2: {
    gridArea: "b2",
  },
  gridAreaBox3: {
    gridArea: "b3",
  },
  gridAreaBox4: {
    gridArea: "b4",
  },
  gridAreaArrow1: {
    gridArea: "a1",
  },
  gridAreaArrow2: {
    gridArea: "a2",
  },
  gridAreaArrow3: {
    gridArea: "a3",
  },
  installItemContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    maxWidth: 180,
    textAlign: "center",
    flex: 80,
  },
  installItemImage: {
    height: 54,
    width: 54,
    marginBottom: 6,
  },
  installFlowArrowImage: {
    width: 45,
    height: 45,
    [theme.breakpoints.up("sm")]: {
      width: 68,
    },
  },
  featureSubheader: {
    fontSize: 18,
    marginBottom: 24,
  },
  rotate90cw: {
    rotate: "90deg",
  },
  rotate180cw: {
    rotate: "180deg",
  },
  featureContainer: {
    display: "flex",
    flexDirection: "row",
    alignItems: "top",
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
  languageListBase: {
    textAlign: "left",
    margin: "3px 0px 0px 0px",
  },
  languageListGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gridAutoRows: "1fr",
    gridColumnGap: 5,
    gridRowGap: 5,
  },
}));

const featureText = {
  /** @type {Types.FeatureDescriptionContent} */
  apiDocs: {
    title: "API Documentation",
    subtitle:
      "Eave finds APIs, writes industry standard documentation, and keeps it updated.",
    supportSubheader: "Express REST APIs that are written in",
    languages: ["JavaScript", "TypeScript"],
  },
  /** @type {Types.FeatureDescriptionContent} */
  codeDocs: {
    title: "Inline Code Documentation",
    subtitle:
      "Eave adds inline function documentation to your code on every merge.",
    supportSubheader: null,
    languages: [
      "C",
      "Java",
      "JavaScript",
      "C++",
      "PHP",
      "TypeScript",
      "Go",
      "Kotlin",
      "Rust",
      "C#",
      "Swift",
      "Ruby",
    ],
  },
};

const UninstalledGithubAppDash = () => {
  const classes = makeClasses();
  /** @type {Types.GlobalEave} */
  // @ts-ignore
  const _globalEave = window;
  const githubOauthUrl = `${_globalEave.eave.apiBase}/oauth/github/authorize`;

  const arrowDesktopClasses = classNames(classes.installFlowArrowImage);

  const Step = ({
    /** @type {string} */ src,
    /** @type {string} */ text,
    extraClasses = {},
  }) => {
    return (
      <div className={classNames(classes.installItemContainer, extraClasses)}>
        <img src={imageUrl(src)} className={classes.installItemImage} />
        <Typography className={classes.caption}>{text}</Typography>
      </div>
    );
  };

  const FeatureDescription = ({
    /** @type {Types.FeatureDescriptionContent} */ content,
  }) => {
    const listClasses = classNames(
      classes.languageListBase,
      content.languages.length > 3 && classes.languageListGrid,
    );
    return (
      <div className={classes.featureDescriptionBlock}>
        <img className={classes.featureLockIcon} src={imageUrl("lock.svg")} />
        <Typography className={classes.featureDescriptionHeader}>
          {content.title}
        </Typography>
        <Typography className={classes.caption}>{content.subtitle}</Typography>
        <Typography className={classes.caption}>
          <br />
          Currently supports:
          <br />
          {content.supportSubheader !== null && content.supportSubheader}
        </Typography>
        <ul className={listClasses}>
          {content.languages.map((lang) => {
            return (
              <li key={lang} className={classes.caption}>
                {lang}
              </li>
            );
          })}
        </ul>
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
      <div className={classes.installFlowContainerDesktop}>
        <Step src="github-icon.svg" text="Add the Eave App to GitHub" />
        <img src={imageUrl("arrow.svg")} className={arrowDesktopClasses} />
        <Step
          src="eave-logo-round.svg"
          text="Eave Detects Documentation Needs"
        />
        <img src={imageUrl("arrow.svg")} className={arrowDesktopClasses} />
        <Step
          src="pr-merge-circle-icon.svg"
          text="Eave Adds Docs to your Codebase in a PR"
        />
        <img src={imageUrl("arrow.svg")} className={arrowDesktopClasses} />
        <Step
          src="code-block-circle-icon.svg"
          text="Your Docs Always Up to Date"
        />
      </div>
      <div className={classes.installFlowContainerMobile}>
        <Step
          extraClasses={classes.gridAreaBox1}
          src="github-icon.svg"
          text="Add the Eave App to GitHub"
        />
        <img
          src={imageUrl("arrow.svg")}
          className={classNames(
            classes.installFlowArrowImage,
            classes.gridAreaArrow1,
          )}
        />
        <Step
          extraClasses={classes.gridAreaBox2}
          src="eave-logo-round.svg"
          text="Eave Detects Documentation Needs"
        />
        <img
          src={imageUrl("arrow.svg")}
          className={classNames(
            classes.installFlowArrowImage,
            classes.rotate90cw,
            classes.gridAreaArrow2,
          )}
        />
        <Step
          extraClasses={classes.gridAreaBox3}
          src="code-block-circle-icon.svg"
          text="Your Docs Always Up to Date"
        />
        <img
          src={imageUrl("arrow.svg")}
          className={classNames(
            classes.installFlowArrowImage,
            classes.rotate180cw,
            classes.gridAreaArrow3,
          )}
        />
        <Step
          extraClasses={classes.gridAreaBox4}
          src="pr-merge-circle-icon.svg"
          text="Eave Adds Docs to your Codebase in a PR"
        />
      </div>
      <Typography className={classes.featureSubheader}>
        ✨ Add App to Access Features ✨
      </Typography>
      <div className={classes.featureContainer}>
        <FeatureDescription content={featureText.apiDocs} />
        <FeatureDescription content={featureText.codeDocs} />
      </div>
    </div>
  );
};

export default UninstalledGithubAppDash;
