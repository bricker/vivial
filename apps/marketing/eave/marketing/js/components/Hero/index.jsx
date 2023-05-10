import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { HEADER, AUTH_MODAL_STATE } from '../../constants.js';
import Button from '../Button/index.jsx';
import Copy from '../Copy/index.jsx';
import useAuthModal from '../../hooks/useAuthModal.js';

const makeClasses = makeStyles((theme) => ({
  section: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
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
}));

const Hero = ({ title, subtitle, cta }) => {
  const classes = makeClasses();

  const { openModal } = useAuthModal();

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
    </section>
  );
};

export default Hero;
