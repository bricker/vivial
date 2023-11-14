import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-util.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  container: {
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
    // Allow the gh feature container image to grow w/ the window width up to
    // the point where PageSection limits the page content width (1115px).
    // This image maxWidth determines the width of the flexbox containers.
    // We want each gh feature to have a max width of ~1/3 of the available content width
    // (i.e. not overflow the page or the margins), so subtract the PageSection.padding[Horizontal] * 2 (108px)
    // and the featureContainer.marginRight * 2 (160px) from the minimum of window width (100vw)
    // and PageSection.maxWidth (1115px), then divide by the number of gh features we display (3).
    // That gives the width a flexbox container should have to take up 1/3 of the available content space,
    // up to the point where the content space stops growing with the browser view width.
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

      <div className={classes.container}>
        {features.map((feature) => (
          <div key={feature.title} className={classes.featureContainer}>
            <Copy variant="h2" bold={true}>
              {feature.title}
            </Copy>
            <Copy variant="pSmall" className={classes.featureSubtitle}>
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
