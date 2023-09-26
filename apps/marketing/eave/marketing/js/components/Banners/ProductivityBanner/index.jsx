import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-helpers.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  productivityBanner: {
    // TODO: change image on mobile layout
    height: "auto",
    width: "100%",
    marginBottom: 30,
    // [theme.breakpoints.up("md")]: {
    //   marginRight: 26,
    //   marginBottom: 0,
    // },
  },
  title: {
    // marginBottom: 65,
    // fontFamily: "DM Sans",
    [theme.breakpoints.up("sm")]: {
      maxWidth: 850,
    },
  },
}));

const ProductivityBanner = ({ title }) => {
  const classes = makeClasses();

  return (
    <>
      <PageSection>
        <Copy className={classes.title} variant="h1">
          {title}
        </Copy>
      </PageSection>
      <img className={classes.productivityBanner} src={imageUrl("productivity-banner-design-3x.png")} alt="Colorful lines intersecting each letter of the Eave logo, company logos for integration platforms ride the lines." />
    </>
  );
};

export default ProductivityBanner;
