import React from 'react';
import { withStyles } from '@material-ui/styles';
import ConnectIcon from '../Icons/ConnectIcon';
import DocumentIcon from '../Icons/DocumentIcon';
import SyncIcon from '../Icons/SyncIcon';
import Copy from '../Copy';

class HowItWorks extends React.Component {
  render() {
    const { classes, copy } = this.props;
    return (
      <section className={classes.section}>
        <div className={classes.infoBlock}>
          <div className={classes.connectIcon}>
            <ConnectIcon />
          </div>
          <Copy className={classes.infoCopy} variant="h3">
            {copy.connect}
          </Copy>
        </div>
        <div className={classes.infoBlock}>
          <div className={classes.syncIcon}>
            <SyncIcon />
          </div>
          <Copy className={classes.infoCopy} variant="h3">
            {copy.sync}
          </Copy>
        </div>
        <div className={classes.infoBlock}>
          <div className={classes.documentIcon}>
            <DocumentIcon />
          </div>
          <Copy className={classes.infoCopy} variant="h3">
            {copy.document}
          </Copy>
        </div>
      </section>
    );
  }
}

const styles = (theme) => ({
  section: {
    padding: '60px 30px 100px',
    backgroundColor: theme.palette.primary.main,
    [theme.breakpoints.up('sm')]: {
      padding: '62px 0 130px',
    },
  },
  infoBlock: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginBottom: 60,
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      flexDirection: 'row',
      justifyContent: 'center',
      maxWidth: 680,
      width: '100%',
      margin: '0 auto',
      padding: '34px 0',
      borderBottom: '1px dashed white',
      '&:last-of-type': {
        borderBottom: 'none',
      },
    },
  },
  infoCopy: {
    color: 'white',
    textAlign: 'center',
    width: 272,
    marginTop: 16,
    [theme.breakpoints.up('sm')]: {
      marginTop: 'unset',
      width: 380,
      paddingLeft: 40,
      textAlign: 'left',
    },
  },
  connectIcon: {
    width: 160,
    color: 'white',
  },
  syncIcon: {
    width: 160,
    color: 'white',
  },
  documentIcon: {
    width: 140,
    padding: '0 10px',
    color: 'white',
  },
});

export default withStyles(styles)(HowItWorks);
