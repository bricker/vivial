import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { FOOTER } from '../../../constants.js';
import Copy from '../../Copy/index.jsx';
import { imageUrl } from '../../../asset-helpers.js';

const makeClasses = makeStyles((theme) => ({
  section: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: `54px 40px calc(${FOOTER.mobile.heightPx} + 108px)`,
    [theme.breakpoints.up('md')]: {
      flexDirection: 'row',
      justifyContent: 'center',
      padding: `109px 164px calc(${FOOTER.mobile.heightPx} + 109px)`,
    },
  },
  privacyIcon: {
    height: 173,
    width: '156.33px',
    marginBottom: 30,
    [theme.breakpoints.up('md')]: {
      marginRight: 26,
      marginBottom: 0,
    },
  },
  copy: {
    [theme.breakpoints.up('md')]: {
      maxWidth: 654,
    },
  },
}));

const PrivacyBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <section className={classes.section}>
    <img
      className={classes.privacyIcon}
      src={imageUrl('privacy-icons-3x.png')}
      alt="Lock icon symbolizing privacy"
    />
    <div className={classes.copy}>
      <Copy variant="h2">
        {title}
      </Copy>
      <Copy variant="pSmall">
        {subtitle}
      </Copy>
    </div>
  </section>
  );
};

export default PrivacyBanner;
