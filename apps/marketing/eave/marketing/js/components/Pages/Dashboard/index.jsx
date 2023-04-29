import React, { useState } from 'react';
import { makeStyles } from '@material-ui/styles';
import { StepContent, StepLabel, Step, Stepper, Select, FormControl, InputLabel, MenuItem, useMediaQuery } from '@material-ui/core';

import { HEADER, INTEGRATION_LOGOS } from '../../../constants.js';
import Copy from '../../Copy/index.js';
import Page from '../Page/index.jsx';
import Button from '../../Button/index.js';
import PurpleCheckIcon from '../../Icons/PurpleCheckIcon.jsx';
import ChatboxIcon from '../../Icons/ChatboxIcon.jsx';
import ConfluenceIcon from '../../Icons/ConfluenceIcon.jsx';

const makeClasses = makeStyles((theme) => ({
  main: {
    position: 'relative',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
    },
  },
  copy: {
    maxWidth: 838,
  },
  button: {
    marginTop: 12,
    width: 150,
    [theme.breakpoints.up('md')]: {
      width: 166,
    },
  },
  step: {
    width: 25,
    height: 25,
    border: '1px solid black',
    borderRadius: '50%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    [theme.breakpoints.up('md')]: {
      width: 39,
      height: 39,
    },
  },
  purpleCheck: {
    width: 23,
    height: 23,
    [theme.breakpoints.up('md')]: {
      width: 27,
      height: 27,
    },
  },
  header: {
    marginBottom: 0,
  },
  content: {
    marginLeft: 16,
    paddingLeft: 18,
    marginTop: 0,
    [theme.breakpoints.up('md')]: {
      marginLeft: 22,
      paddingLeft: 27,
    },
  },
  stepper: {
    padding: 0,
    '& .MuiStepConnector-vertical': {
      marginLeft: 16,
      [theme.breakpoints.up('md')]: {
        marginLeft: 22,
      },
    },
    '& .MuiStepLabel-vertical': {
      marginBottom: 22,
      marginTop: 22,
    },
    '& .MuiStepLabel-completed $header': {
      color: theme.typography.color.innactive,
    },
  },
  select: {
    width: 275,
    marginTop: 12,
    [theme.breakpoints.up('md')]: {
      width: 418,
    },
  },
  footer: {
    maxWidth: 883,
    padding: '26px 34px',
    marginTop: 28,
    marginBottom: 24,
    backgroundColor: theme.palette.background.secondary,
    display: 'flex',
    [theme.breakpoints.up('md')]: {
      padding: 24,
      marginTop: 92,
    },
  },
  chatIcon: {
    paddingRight: 28,
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'block',
    },
  },
  connectButton: {
    width: 166,
    color: theme.typography.color.dark,
    marginTop: 22,
    marginRight: 20,
    border: `1px solid ${theme.typography.color.dark}`,
    height: 60,
    position: 'relative',
  },
  connected: {
    position: 'absolute',
    top: 5,
    left: 5,
    width: 14,
  },
  githubButtonLogo: {
    maxWidth: 116,
  },
  slackButtonLogo: {
    maxWidth: 88,
  },
  jiraButtonLogo: {
    maxWidth: 128,
  },
}));

function stepIcon(props) {
  const classes = makeClasses();

  return (
    <div className={classes.step}>
      {props.completed && <PurpleCheckIcon className={classes.purpleCheck} />}
    </div>
  );
}

const Dashboard = () => {
  const classes = makeClasses();
  const [confluenceSpace, setConfluenceSpace] = useState('');
  const [step, setStep] = useState(0);
  const isDesktop = useMediaQuery((theme) => theme.breakpoints.up('md'));

  const handleChange = (event) => {
    setConfluenceSpace(event.target.value);
    setStep(2);
  };

  return (
    <Page simpleHeader>
      <main className={classes.main}>
        <Copy variant="h1">Welcome to Eave Early Access</Copy>
        <Copy className={classes.copy}>You’re on your way to better documentation. To get started using Eave, complete the below steps.</Copy>
        <Stepper orientation="vertical" activeStep={step} classes={{
          vertical: classes.stepper,
        }}>
          <Step>
            <StepLabel StepIconComponent={stepIcon}>
              <Copy variant="h3" className={classes.header}>
                {isDesktop ? (
                  <span>
                    Step 1: Connect to your <ConfluenceIcon /> Confluence Account
                  </span>
                ) : (
                  <span>
                    Step 1: Connect to <ConfluenceIcon /> Confluence
                  </span>
                )}

              </Copy>
            </StepLabel>
            <StepContent className={classes.content}>
              <Copy variant="pSmall">This will allow Eave to automatically generate documentation in Confluence.</Copy>
              <Button lg className={classes.button} onClick={() => setStep(1)}>
                Connect
              </Button>
            </StepContent>
          </Step>
          <Step>
            <StepLabel StepIconComponent={stepIcon}>
              <Copy variant="h3" className={classes.header}>Step 2: Select your Confluence Space</Copy>
            </StepLabel>
            <StepContent className={classes.content}>
              <Copy variant="pSmall">This will allow Eave to automatically generate documentation in Confluence.</Copy>
              <div>
                <FormControl variant='outlined' className={classes.select}>
                  <InputLabel id="space-selector-label">Eave Megastar Beta Team</InputLabel>
                  <Select
                    labelId="space-selector-label"
                    id="space-selector"
                    value={confluenceSpace}
                    onChange={handleChange}
                  >
                    <MenuItem value="">
                      None
                    </MenuItem>
                    <MenuItem value={10}>Twenty</MenuItem>
                    <MenuItem value={21}>Twenty one</MenuItem>
                    <MenuItem value={22}>Twenty one and a half</MenuItem>
                  </Select>
                </FormControl>
              </div>
            </StepContent>
          </Step>
          <Step>
            <StepLabel StepIconComponent={stepIcon}>
              <Copy variant="h3" className={classes.header}>Step 3: Integrate your business tools</Copy>
            </StepLabel>
            <StepContent className={classes.content}>
              <Copy variant="pSmall" className={classes.copy}>Select the tools where Eave can pull information from and be tagged to created documentation. Note Jira is automatically granted permissions via the Confluence connection.</Copy>
              <Button
                className={classes.connectButton}
                variant="outlined"
                startIcon={<PurpleCheckIcon className={classes.connected} />}
                lg
              >
                <img
                  className={classes.githubButtonLogo}
                  src={INTEGRATION_LOGOS.githubInline.src}
                  alt={INTEGRATION_LOGOS.githubInline.alt}
                />
              </Button>
              <Button
                className={classes.connectButton}
                variant="outlined"
                startIcon={<PurpleCheckIcon className={classes.connected} />}
                lg
              >
                <img
                  className={classes.slackButtonLogo}
                  src={INTEGRATION_LOGOS.slack.src}
                  alt={INTEGRATION_LOGOS.slack.alt}
                />
              </Button>
              <Button
                className={classes.connectButton}
                variant="outlined"
                startIcon={<PurpleCheckIcon className={classes.connected} />}
                lg
              >
                <img
                  className={classes.jiraButtonLogo}
                  src={INTEGRATION_LOGOS.jira.src}
                  alt={INTEGRATION_LOGOS.jira.alt}
                />
              </Button>
            </StepContent>
          </Step>
        </Stepper>
        <section className={classes.footer}>
          <div className={classes.chatIcon}>
            <ChatboxIcon />
          </div>
          <div className={classes.footerCopy}>
            <Copy variant="footnote" bold>A Message from the Eave Team</Copy>
            <Copy variant="footnote">
              Please note we’re currently in development and have many more integrations on the way. We’d love to hear your feedback on the current experience as well as any requests you may have. You can fill out this feedback form <a href="" target='_blank   '>here</a>, or reach out to us directly at <a href="mailto:info@eave.fyi">info@eave.fyi</a>
            </Copy>
            </div>
        </section>
      </main>
    </Page>
  );
};

export default Dashboard;
