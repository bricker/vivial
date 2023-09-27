import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-helpers.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  // section: {
  //   padding: `54px 40px calc(${theme.footer.height}px + 108px)`,
  // },
  wrapper: {
    display: "flex",
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    [theme.breakpoints.up("md")]: {
      flexDirection: "column",
    },
  },
  copy: {
    [theme.breakpoints.up("md")]: {
      maxWidth: 654,
      marginLeft: 24,
    },
  },
  featureContainer: {
    flex: 1,
  },
  featureImage: {},
}));

const GitHubFeaturesBanner = ({ title, features }) => {
  const classes = makeClasses();

  return (
    <PageSection>
      <Copy variant="h1">{title}</Copy>

      <div className={classes.wrapper}>
        {features.map((feature) => {
          return (
            <div className={classes.featureContainer}>
              <Copy variant="h2">{feature.title}</Copy>
              <Copy variant="p">{feature.subtitle}</Copy>
              {/* image isn't important for a11y, so use empty alt text to show that */}
              <img className={classes.featureImage} src={imageUrl(feature.image)} alt="" />
            </div>
          );
        })}
      </div>
    </PageSection>
  );
};

export default GitHubFeaturesBanner;
