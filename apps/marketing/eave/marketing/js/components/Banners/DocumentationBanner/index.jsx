import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-helpers.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  section: {
    padding: "54px 40px 0",
    [theme.breakpoints.up("md")]: {
      padding: "54px 40px",
    },
  },
  wrapper: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "space-between",
    [theme.breakpoints.up("md")]: {
      flexDirection: "row",
    },
  },
  copy: {
    marginBottom: 37,
    [theme.breakpoints.up("lg")]: {
      width: 457,
      minWidth: 457,
      marginBottom: 0,
      marginRight: 68,
    },
  },
  img: {
    maxWidth: "100%",
    marginBottom: "-5px",
    [theme.breakpoints.up("md")]: {
      marginBottom: 0,
    },
  },
}));

const DocumentationBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <PageSection alternateBackground id="eave-integrations-banner" wrapperClassName={classes.wrapper} sectionClassName={classes.section}>
      <div className={classes.copy}>
        <Copy variant="h2">{title}</Copy>
        <Copy variant="pSmall">{subtitle}</Copy>
      </div>
      <picture>
        <source media="(min-width: 600px)" sizes="1266px" srcSet={`${imageUrl("confluence-mock.png")} 1266w`} />
        <source media="(max-width: 599px)" sizes="714px" srcSet={`${imageUrl("confluence-mock-mobile.png")} 714w`} />
        <img className={classes.img} src={imageUrl("confluence-mock-mobile.png")} alt="Confluence documentation written by Eave." />
      </picture>
    </PageSection>
  );
};

export default DocumentationBanner;
