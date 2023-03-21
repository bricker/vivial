import React from 'react';
import { withStyles } from '@material-ui/styles';
import { AFFILIATE_LOGOS } from '../../constants';
import Copy from '../Copy';

class Affiliates extends React.Component {
  render() {
    const { classes } = this.props;
    const { className } = this.props;
    return (
      <div className={className}>
        <Copy className={classes.footnote} variant="footnote">
          Trusted by employees from
        </Copy>
        <div className={classes.logos}>
          <img
            className={classes.amazonLogo}
            src={AFFILIATE_LOGOS.amazon.src}
            alt={AFFILIATE_LOGOS.amazon.alt}
          />
          <img
            className={classes.paypalLogo}
            src={AFFILIATE_LOGOS.paypal.src}
            alt={AFFILIATE_LOGOS.paypal.alt}
          />
          <img
            className={classes.disneyLogo}
            src={AFFILIATE_LOGOS.disney.src}
            alt={AFFILIATE_LOGOS.disney.alt}
          />
          <img
            className={classes.honeyLogo}
            src={AFFILIATE_LOGOS.honey.src}
            alt={AFFILIATE_LOGOS.honey.alt}
          />
        </div>
      </div>
    );
  }
}

const styles = (theme) => ({
  footnote: {
    marginBottom: 10,
    [theme.breakpoints.up('sm')]: {
      marginBottom: 12,
    },
  },
  logos: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 15,
    [theme.breakpoints.up('sm')]: {
      marginBottom: 21,
      maxWidth: 543,
    },
  },
  amazonLogo: {
    position: 'relative',
    top: '5px',
    width: '52.62px',
    [theme.breakpoints.up('sm')]: {
      width: '96px',
    },
  },
  paypalLogo: {
    width: '64.13px',
    [theme.breakpoints.up('sm')]: {
      width: '117px',
    },
  },
  disneyLogo: {
    width: '53.92px;',
    [theme.breakpoints.up('sm')]: {
      width: '98.36px',
    },
  },
  honeyLogo: {
    width: '58px',
    [theme.breakpoints.up('sm')]: {
      width: '109px',
    },
  },
});

export default withStyles(styles)(Affiliates);
