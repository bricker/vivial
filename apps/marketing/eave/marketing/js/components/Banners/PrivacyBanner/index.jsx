import React from 'react';
import { makeStyles } from '@material-ui/styles';

import { FOOTER } from '../../../constants.js';
import PageSection from '../../PageSection/index.jsx';
import Copy from '../../Copy/index.jsx';
import { imageUrl } from '../../../asset-helpers.js';

const makeClasses = makeStyles((theme) => ({
  section: {
    padding: `54px 40px calc(${FOOTER.mobile.heightPx} + 108px)`,
  },
  wrapper: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    justifyContent: 'center',
    [theme.breakpoints.up('md')]: {
      flexDirection: 'row',
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
      marginLeft: 24,
    },
  },
}));

const PrivacyBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <PageSection sectionClassName={classes.section} wrapperClassName={classes.wrapper}>
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
  </PageSection>
  );
};

export default PrivacyBanner;
