import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { AUTH_MODAL_STATE } from '../../constants.js';
import Button from '../Button/index.jsx';
import PageSection from '../PageSection/index.jsx';
import Copy from '../Copy/index.jsx';
import useAuthModal from '../../hooks/useAuthModal.js';

const makeClasses = makeStyles((theme) => ({
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
      <Button lg onClick={() => openModal(AUTH_MODAL_STATE.SIGNUP)}>
        {cta}
      </Button>
    </PageSection>
  );
};

export default Hero;
