import { makeStyles } from "@material-ui/styles";
import React from "react";

import { imageUrl } from "../../../util/asset-util.js";
import Copy from "../../Copy/index.jsx";
import PageSection from "../../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  productivityBanner: {
    height: "auto",
    width: "100%",
    marginBottom: 60,
    [theme.breakpoints.up("xl")]: {
      width: "1520px",
    },
  },
  wrapper: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
}));

const ProductivityBanner = ({ title }) => {
  const classes = makeClasses();

  return (
    <div>
      <PageSection>
        <Copy variant="h1">{title}</Copy>
      </PageSection>
      <picture className={classes.wrapper}>
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
    </div>
  );
};

export default ProductivityBanner;
