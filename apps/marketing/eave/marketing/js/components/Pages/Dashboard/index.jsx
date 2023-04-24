import React, { useState } from 'react';
import { makeStyles } from '@material-ui/styles';
import { StepContent, StepLabel, Step, Stepper, Select, FormControl, InputLabel, MenuItem } from '@material-ui/core';

import { HEADER, INTEGRATION_LOGOS } from '../../../constants.js';
import Copy from '../../Copy/index.js';
import Page from '../Page/index.jsx';
import Button from '../../Button/index.js';
import PurpleCheckIcon from '../../Icons/PurpleCheckIcon.jsx';
import ChatboxIcon from '../../Icons/ChatboxIcon.jsx';

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
  },
  step: {
    width: 39,
    height: 39,
    border: '1px solid black',
    borderRadius: '50%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  purpleCheck: {
    width: 27,
    height: 27,
  },
  header: {
    marginBottom: 0,
  },
  confluenceLogo: {
    maxWidth: 137,
  },
  content: {
    marginLeft: 22,
    paddingLeft: 27,
    marginTop: 0,
  },
  stepper: {
    '& .MuiStepConnector-vertical': {
      marginLeft: 22,
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
    width: 418,
    marginTop: 12,
  },
  footer: {
    maxWidth: 883,
    padding: 24,
    marginTop: 92,
    marginBottom: 24,
    backgroundColor: theme.palette.background.secondary,
  },
  connectButton: {
    width: 166,
    color: theme.typography.color.dark,
    marginTop: 22,
    marginRight: 20,
    border: `1px solid ${theme.typography.color.dark}`,
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
                Step 1: Connect to your{' '}
                <img
                  className={classes.confluenceLogo}
                  src={INTEGRATION_LOGOS.confluence.src}
                  alt={INTEGRATION_LOGOS.confluence.alt}
                />
                {' '}Account
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
          <ChatboxIcon />
          <Copy variant="footnote" bold>A Message from the Eave Team</Copy>
          <Copy variant="footnote">
            Please note we’re currently in development and have many more integrations on the way. We’d love to hear your feedback on the current experience as well as any requests you may have. You can fill out this feedback form <a href="" target='_blank   '>here</a>, or reach out to us directly at <a href="mailto:info@eave.fyi">info@eave.fyi</a>
          </Copy>
        </section>
      </main>
    </Page>
  );
};

export default Dashboard;
