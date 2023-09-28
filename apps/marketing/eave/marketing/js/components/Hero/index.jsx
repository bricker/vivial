import { makeStyles } from "@material-ui/styles";
import React from "react";

import { AUTH_MODAL_STATE } from "../../constants.js";
import useAuthModal from "../../hooks/useAuthModal.js";
import Button from "../Button/index.jsx";
import Copy from "../Copy/index.jsx";
import PageSection from "../PageSection/index.jsx";

const makeClasses = makeStyles((theme) => ({
  title: {
    marginBottom: 26,
    [theme.breakpoints.up("sm")]: {
      maxWidth: 850,
    },
  },
  subtitle: {
    marginBottom: 32,
    [theme.breakpoints.up("sm")]: {
      maxWidth: 840,
    },
  },
  button: {
    width: 250,
    height: 60,
    fontWeight: 700,
  },
}));

const Hero = ({ title, subtitle, cta }) => {
  const classes = makeClasses();
  const { openModal } = useAuthModal();

  return (
    <PageSection topSection>
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
    </PageSection>
  );
};

export default Hero;
