import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-helpers.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles(() => ({
  productivityBanner: {
    height: "auto",
    width: "100%",
    marginBottom: 30,
  },
}));

const ProductivityBanner = ({ title }) => {
  const classes = makeClasses();

  return (
    <>
      <PageSection>
        <Copy variant="h1">{title}</Copy>
      </PageSection>
      <picture>
        {/* TODO: get this width from somewhere; constants (weher the heck is sm and md defined for theme?) */}
        <source
          media="(max-width:650px)"
          srcSet={imageUrl("productivity-banner-design-vertical-3x.png")}
        />
        <img
          className={classes.productivityBanner}
          src={imageUrl("productivity-banner-design-horizontal-3x.png")}
          alt="Colorful lines intersecting each letter of the Eave logo, company logos for integration platforms ride the lines."
        />
      </picture>
    </>
  );
};

export default ProductivityBanner;
