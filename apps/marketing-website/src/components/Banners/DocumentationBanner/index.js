import React from 'react';
import { withStyles } from '@material-ui/styles';
import { INTEGRATION_LOGOS } from '../../../constants';
import EaveLogo from '../../EaveLogo';
import Copy from '../../Copy';

class DocumentationBanner extends React.Component {
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
        <div className={classes.logos}>
          <EaveLogo className={classes.eaveLogo} />
          <img
            className={classes.confluenceLogo}
            src={INTEGRATION_LOGOS.confluence.src}
            alt={INTEGRATION_LOGOS.confluence.alt}
          />
          <img
            className={classes.driveLogo}
            src={INTEGRATION_LOGOS.drive.src}
            alt={INTEGRATION_LOGOS.drive.alt}
          />
          <img
            className={classes.sharepointLogo}
            src={INTEGRATION_LOGOS.sharepoint.src}
            alt={INTEGRATION_LOGOS.sharepoint.alt}
          />
        </div>
      </section>
    );
  }
}

const styles = (theme) => ({
  section: {
    backgroundColor: theme.palette.background.dark,
    padding: '54px 40px',
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    [theme.breakpoints.up('md')]: {
      padding: '82px 164px',
    },
    [theme.breakpoints.up('lg')]: {
      flexDirection: 'row',
    },
  },
  copy: {
    marginBottom: 37,
    [theme.breakpoints.up('lg')]: {
      width: 457,
      minWidth: 457,
      marginBottom: 0,
      marginRight: 68,
    },
  },
  logos: {
    display: 'flex',
    flexFlow: 'wrap',
    alignItems: 'center',
    width: 300,
    [theme.breakpoints.up('sm')]: {
      width: '100%',
      justifyContent: 'space-between',
    },
  },
  eaveLogo: {
    display: 'inline-block',
    fontSize: 36,
    lineHeight: '36px',
    paddingRight: 42,
    marginBottom: 10,
    [theme.breakpoints.up('sm')]: {
      fontSize: 48,
      lineHeight: '48px',
      marginBottom: 0,
      paddingRight: 0,
    },
    [theme.breakpoints.up('lg')]: {
      display: 'block',
      width: '100%',
      textAlign: 'center',
      marginBottom: 10,
    },
  },
  confluenceLogo: {
    width: 124,
    marginBottom: 4,
    [theme.breakpoints.up('sm')]: {
      width: '182.38px',
      maxWidth: '30%',
      marginBottom: 0,
    },
  },
  driveLogo: {
    width: 113,
    paddingRight: 42,
    [theme.breakpoints.up('sm')]: {
      width: '172.36px',
      maxWidth: '30%',
      paddingRight: 0,
    },
  },
  sharepointLogo: {
    width: 103,
    [theme.breakpoints.up('sm')]: {
      width: '159.33px',
      maxWidth: '30%',
    },
  },
});

export default withStyles(styles)(DocumentationBanner);
