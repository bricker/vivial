import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-util.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  wrapper: {
    display: "flex",
    alignItems: "flex-start",
    flexDirection: "column",
    justifyContent: "space-between",
    [theme.breakpoints.up("md")]: {
      flexDirection: "row",
    },
  },
  featureContainer: {
    flexGrow: 1,
    flexBasis: 150,
    marginRight: 80,
  },
  featureSubtitle: {
    marginBottom: 41,
  },
  featureImage: {
    // widthFn = (maxWidth) => (maxWidth - PageSection.padding*2 - featureContainer.margin*2) / numberOfFeatures
    // min( widthFn(viewportWidth), widthFn(PageSection.maxWidth) )
    maxWidth: "min((100vw - 108px - 160px) / 3, 282px)",
    minWidth: 150,
    [theme.breakpoints.down("sm")]: {
      minWidth: 328,
      marginBottom: 75,
    },
  },
  titleImage: {
    maxWidth: 355,
    [theme.breakpoints.down("sm")]: {
      order: -1,
      marginBottom: 28,
      maxWidth: "50%",
    },
    [theme.breakpoints.up("lg")]: {
      marginRight: -140,
    },
  },
  titleContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    justifyContent: "spacing-between",
    marginBottom: 85,
    [theme.breakpoints.up("md")]: {
      flexDirection: "row",
      alignItems: "flex-end",
    },
  },
  heroBufferPadding: {
    paddingTop: 300,
    [theme.breakpoints.only("md")]: {
      paddingTop: 200,
    },
  },
}));

const GitHubFeaturesBanner = ({ title, features }) => {
  const classes = makeClasses();

  return (
    <PageSection sectionClassName={classes.heroBufferPadding}>
      <div className={classes.titleContainer}>
        <Copy variant="h1" className={classes.titleCopy}>
          {title}
        </Copy>
        <img
          className={classes.titleImage}
          src={imageUrl("eave-github-logos-3x.png")}
          alt="Eave and GitHub logos side-by-side"
        />
      </div>

      <div className={classes.wrapper}>
        {features.map((feature, i) => (
          <div key={i} className={classes.featureContainer}>
            <Copy variant="h2" bold={true}>
              {feature.title}
            </Copy>
            <Copy variant="p" className={classes.featureSubtitle}>
              {feature.subtitle}
            </Copy>
            {/* image isn't important for a11y, so use empty alt text to show that */}
            <img
              className={classes.featureImage}
              src={imageUrl(feature.image)}
              alt=""
            />
          </div>
        ))}
      </div>
    </PageSection>
  );
};

export default GitHubFeaturesBanner;
