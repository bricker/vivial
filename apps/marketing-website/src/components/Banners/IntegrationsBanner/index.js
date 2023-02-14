import React from 'react';
import { withStyles } from '@material-ui/styles';
import { INTEGRATION_LOGOS } from '../../../constants';
import Copy from '../../Copy';

class IntegrationsBanner extends React.Component {
  render() {
    const { classes, title, subtitle } = this.props;
    return (
      <section id="eave-integrations-banner" className={classes.section}>
        <div className={classes.copy}>
          <Copy variant="h2">
            {title}
          </Copy>
          <Copy variant="pSmall">
            {subtitle}
          </Copy>
        </div>

        {/* Desktop Only */}
        <div className={classes.desktopLogos}>
          <div className={classes.desktopLogoRow}>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.slack.src} alt={INTEGRATION_LOGOS.slack.alt} width="130.56px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.gmail.src} alt={INTEGRATION_LOGOS.gmail.alt} width="122px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.notion.src} alt={INTEGRATION_LOGOS.notion.alt} width="114.48px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.teams.src} alt={INTEGRATION_LOGOS.teams.alt} width="163px" />
            </div>
          </div>
          <div className={classes.desktopLogoRow}>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.github.src} alt={INTEGRATION_LOGOS.github.alt} width="58.66px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.outlook.src} alt={INTEGRATION_LOGOS.outlook.alt} width="179.76px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.figma.src} alt={INTEGRATION_LOGOS.figma.alt} width="92.72px" />
            </div>
            <div className={classes.desktopLogoWrapper}>
              <img className={classes.desktopLogo} src={INTEGRATION_LOGOS.jira.src} alt={INTEGRATION_LOGOS.jira.alt} width="154px" />
            </div>
          </div>
        </div>

        {/* Mobile Only */}
        <div className={classes.mobileLogos}>
          <div className={classes.mobileSlideTrack}>
            {[1, 2].map((x) => (
              <React.Fragment key={x}>
                <div className={classes.mobileSlide}>
                  <img src={INTEGRATION_LOGOS.slack.src} alt={INTEGRATION_LOGOS.slack.alt} height="25.83px" width="101.84px" style={{ marginBottom: '11.85px' }} />
                  <img src={INTEGRATION_LOGOS.github.src} alt={INTEGRATION_LOGOS.github.alt} height="37.63px" width="45.75px" />
                </div>
                <div className={classes.mobileSlide}>
                  <img src={INTEGRATION_LOGOS.gmail.src} alt={INTEGRATION_LOGOS.gmail.alt} height="21.84px" width="95.16px" style={{ marginBottom: '21.07px' }} />
                  <img src={INTEGRATION_LOGOS.outlook.src} alt={INTEGRATION_LOGOS.outlook.alt} height="25.09px" width="140.21px" />
                </div>
                <div className={classes.mobileSlide}>
                  <img src={INTEGRATION_LOGOS.notion.src} alt={INTEGRATION_LOGOS.notion.alt} height="49.44px" width="89.29px" style={{ marginBottom: '2.99px' }} />
                  <img src={INTEGRATION_LOGOS.figma.src} alt={INTEGRATION_LOGOS.figma.alt} height="36.16px" width="72.32px" />
                </div>
                <div className={classes.mobileSlide}>
                  <img src={INTEGRATION_LOGOS.teams.src} alt={INTEGRATION_LOGOS.teams.alt} height="29.64px" width="127.14px" style={{ marginBottom: '18.72px' }} />
                  <img src={INTEGRATION_LOGOS.jira.src} alt={INTEGRATION_LOGOS.jira.alt} height="18.72px" width="120.12px" />
                </div>
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>
    );
  }
}

const styles = (theme) => ({
  section: {
    backgroundColor: theme.palette.background.dark,
    padding: '54px 0',
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '54px 40px',
    },
    [theme.breakpoints.up('md')]: {
      padding: '82px 164px',
    },
    [theme.breakpoints.up('lg')]: {
      flexDirection: 'row',
    },
  },
  copy: {
    padding: '0 40px',
    marginBottom: 15,
    [theme.breakpoints.up('sm')]: {
      padding: 0,
    },
    [theme.breakpoints.up('lg')]: {
      width: 409,
      minWidth: 409,
      marginBottom: 0,
    },
  },
  desktopLogos: {
    display: 'none',
    [theme.breakpoints.up('sm')]: {
      display: 'block',
      width: '100%',
    },
  },
  desktopLogoRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  desktopLogoWrapper: {
    textAlign: 'center',
    width: '25%',
    paddingRight: 20,
    [theme.breakpoints.up('lg')]: {
      paddingRight: 0,
      paddingLeft: 20,
    },
  },
  desktopLogo: {
    maxWidth: '100%',
    height: 'auto',
  },
  mobileLogos: {
    overflow: 'hidden',
    position: 'relative',
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      display: 'none',
    },
  },
  mobileSlideTrack: {
    animation: 'scroll 14s linear infinite',
    display: 'flex',
    width: 'calc(141px * 8)',
  },
  mobileSlide: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: 89,
    width: 141,
    flexDirection: 'column',
  },
  '@global': {
    '@keyframes scroll': {
      '0%': { transform: 'translateX(0)' },
      '100%': { transform: 'translateX(calc(-141px * 4))' },
    },
  },
});

export default withStyles(styles)(IntegrationsBanner);
