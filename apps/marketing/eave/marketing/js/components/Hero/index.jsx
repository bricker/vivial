import { makeStyles } from "@material-ui/styles";
import React from "react";

import horizontalBgImage from "../../../static/images/hero-background-horizontal-4x.png";
import tabletBgImage from "../../../static/images/hero-background-tablet-3x.png";
import verticalBgImage from "../../../static/images/hero-background-vertical-3x.png";
import { AUTH_MODAL_STATE } from "../../constants.js";
import useAuthModal from "../../hooks/useAuthModal.js";
import Button from "../Button/index.jsx";
import Copy from "../Copy/index.jsx";
import PageSection from "../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  title: {
    marginBottom: 26,
    order: 1,
    [theme.breakpoints.up("sm")]: {
      maxWidth: 850,
    },
  },
  subtitle: {
    marginBottom: 32,
    order: 3,
    [theme.breakpoints.up("sm")]: {
      maxWidth: 840,
    },
  },
  button: {
    width: 250,
    height: 60,
    fontWeight: 700,
    order: 4,
    [theme.breakpoints.down("sm")]: {
      order: 2,
      marginBottom: 32,
    },
  },
  wrapper: {
    display: "flex",
    flexDirection: "column",
  },
  bgImage: {
    width: "100%",
    height: "100%",
    position: "absolute",
    top: 0,
    zIndex: -1,
    backgroundImage: `url(${horizontalBgImage})`,
    backgroundRepeat: "no-repeat",
    backgroundSize: "contain",
    backgroundPosition: "center top",
    [theme.breakpoints.between(
      theme.breakpoints.values.xs,
      theme.breakpoints.values.thin,
    )]: {
      backgroundImage: `url(${verticalBgImage})`,
    },
    [theme.breakpoints.between(
      theme.breakpoints.values.thin,
      theme.breakpoints.values.md,
    )]: {
      backgroundImage: `url(${tabletBgImage})`,
    },
    [theme.breakpoints.up("xl")]: {
      backgroundSize: "auto 1800px",
    },
  },
}));

const Hero = ({ title, subtitle, cta }) => {
  const classes = makeClasses();
  const { openModal } = useAuthModal();

  return (
    <>
      <div className={classes.bgImage}></div>
      <PageSection topSection>
        <div className={classes.wrapper}>
          <Copy className={classes.title} variant="h1">
            {title}
          </Copy>
          <Copy className={classes.subtitle} variant="p">
            {subtitle}
          </Copy>
          <Button
            className={classes.button}
            onClick={() => openModal(AUTH_MODAL_STATE.SIGNUP)}
          >
            {cta}
          </Button>
        </div>
      </PageSection>
    </>
  );
};

export default Hero;
