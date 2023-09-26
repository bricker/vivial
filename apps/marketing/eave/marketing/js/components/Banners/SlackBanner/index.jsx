import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React from "react";

import { imageUrl } from "../../../util/asset-helpers.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  wrapper: {
    display: "grid",
    gridGap: "37px 0px",
    gridTemplateAreas: `
      'upperCopy'
      'img'
      'lowerCopy'
    `,
    [theme.breakpoints.up("md")]: {
      gridTemplateColumns: "1fr 458px",
      gridGap: "0px 26px",
      gridTemplateAreas: `
        'img upperCopy'
        'img lowerCopy'
      `,
    },
  },
  copy: {
    padding: "0 40px",
    [theme.breakpoints.up("md")]: {
      padding: 0,
    },
    [theme.breakpoints.up("lg")]: {
      display: "flex",
      flexDirection: "column",
    },
  },
  upperCopy: {
    gridArea: "upperCopy",
    [theme.breakpoints.up("lg")]: {
      justifyContent: "flex-end",
      paddingBottom: 26,
    },
  },
  lowerCopy: {
    gridArea: "lowerCopy",
    [theme.breakpoints.up("lg")]: {
      justifyContent: "flex-start",
      paddingTop: 26,
    },
  },
  imgWrapper: {
    gridArea: "img",
    lineHeight: "0px",
    padding: "0px 16px",
    [theme.breakpoints.up("sm")]: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
    },
    [theme.breakpoints.up("md")]: {
      padding: 0,
    },
  },
  img: {
    width: "100%",
  },
}));

const SlackBanner = ({ titles, subtitles }) => {
  const classes = makeClasses();
  const upperCopyClasses = classNames(classes.copy, classes.upperCopy);
  const lowerCopyClasses = classNames(classes.copy, classes.lowerCopy);

  return (
    <PageSection wrapperClassName={classes.wrapper}>
      <picture className={classes.imgWrapper}>
        <source media="(min-width: 600px)" sizes="1266px" srcSet={`${imageUrl("eave-slack-2x.png")} 1266w`} />
        <source media="(max-width: 599px)" sizes="714px" srcSet={`${imageUrl("eave-slack-small-2x.png")} 714w`} />
        <img className={classes.img} src={imageUrl("eave-slack-small-2x.png")} alt="Slack conversation between team members and Eave." />
      </picture>
      <div className={upperCopyClasses}>
        <Copy variant="h2">{titles[0]}</Copy>
        <Copy variant="pSmall">{subtitles[0]}</Copy>
      </div>
      <div className={lowerCopyClasses}>
        <Copy variant="h2">{titles[1]}</Copy>
        <Copy variant="pSmall">{subtitles[1]}</Copy>
      </div>
    </PageSection>
  );
};

export default SlackBanner;
