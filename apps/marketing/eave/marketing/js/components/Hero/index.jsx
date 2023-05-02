import React from 'react';
import { makeStyles } from '@material-ui/styles';
import { IconButton } from '@material-ui/core';

import { HEADER } from '../../constants.js';
import DownIcon from '../Icons/DownIcon.js';
import Affiliates from '../Affiliates/index.js';
import Button from '../Button/index.js';
import Copy from '../Copy/index.js';
import useAuthModal from '../../hooks/useAuthModal.js';

const makeClasses = makeStyles((theme) => ({
  section: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px`,
    [theme.breakpoints.up('md')]: {
      minHeight: '100vh',
      padding: '0px 164px',
    },
  },
  title: {
    marginBottom: 26,
    [theme.breakpoints.up('sm')]: {
      maxWidth: 850,
    },
  },
  subtitle: {
    marginBottom: 32,
    [theme.breakpoints.up('sm')]: {
      maxWidth: 840,
    },
  },
  cta: {
    marginBottom: 46,
  },
  downIcon: {
    position: 'absolute',
    bottom: 27,
    left: 0,
    display: 'flex',
    justifyContent: 'center',
    width: '100%',
    [theme.breakpoints.up('md')]: {
      bottom: 55,
    },
  },
  iconBtn: {
    '&:hover': {
      backgroundColor: 'transparent',
    },
  },
}));

const Hero = ({ title, subtitle, cta }) => {
  const classes = makeClasses();

  const { openModal } = useAuthModal();

  const handleGoToNextSection = () => {
    const integrations = document.getElementById('eave-integrations-banner');
    integrations.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className={classes.section}>
      <Copy className={classes.title} variant="h1">
        {title}
      </Copy>
      <Copy className={classes.subtitle} variant="p">
        {subtitle}
      </Copy>
      <div className={classes.cta}>
        <Button lg onClick={() => openModal(AUTH_MODAL_STATE.SIGNUP)}>
          {cta}
        </Button>
      </div>
      <Affiliates />
      <div className={classes.downIcon}>
        <IconButton
          classes={{ root: classes.iconBtn }}
          onClick={handleGoToNextSection}
        >
          <DownIcon />
        </IconButton>
      </div>
    </section>
  );
};

export default Hero;
