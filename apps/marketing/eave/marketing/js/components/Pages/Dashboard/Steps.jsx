import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  StepContent,
  StepLabel,
  Step,
  Stepper,
  Select,
  FormControl,
  InputLabel,
  MenuItem,
  useMediaQuery,
} from '@material-ui/core';
import classNames from 'classnames';

import { HEADER, INTEGRATION_LOGOS } from '../../../constants.js';
import useUser from '../../../hooks/useUser.js';
import Copy from '../../Copy/index.jsx';
import Button from '../../Button/index.jsx';
import PurpleCheckIcon from '../../Icons/PurpleCheckIcon.jsx';
import ConfluenceIcon from '../../Icons/ConfluenceIcon.jsx';
import DownIcon from '../../Icons/DownIcon.js';
import Footnote from './Footnote.jsx';
import StepIcon from './StepIcon.jsx';

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
  header: {
    marginBottom: 0,
  },
  clickable: {
    cursor: 'pointer',
  },
  downIcon: {
    marginLeft: 16,
    width: 16,
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
    '& .MuiFormLabel-filled': {
      background: theme.palette.background.main,
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

const Steps = () => {
  const classes = makeClasses();
  const isDesktop = useMediaQuery((theme) => theme.breakpoints.up('md'));
  const { userState, updateConfluenceSpace } = useUser();
  const { teamInfo } = userState;
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (teamInfo?.integrations.atlassian) {
      // if user has not selected a conflunece space
      if (!teamInfo?.integrations.atlassian.confluence_space_key) {
        setStep(1);
      // confluence integration happens by default, if user has not linked their github or slack
      } else if (!teamInfo?.integrations.github || !teamInfo?.integrations.slack) {
        setStep(2);
      // user has linked all so we can just show a completed stepper
      } else {
        setStep(3);
      }
    }
  }, [teamInfo]);

  const isStep2Clickable = step > 1 && teamInfo?.integrations?.atlassian?.confluence_space_key.length > 0;

  const handleSpaceUpdate = (event) => {
    updateConfluenceSpace(event.target.value);
  };

  const handleStepClick = () => {
    if (isStep2Clickable) {
      setStep(1);
    }
  };

  return (
    <section>
      <Copy variant="h1">Welcome to Eave Early Access</Copy>
      <Copy className={classes.copy}>You’re on your way to better documentation. To get started using Eave, complete the below steps.</Copy>
      <Stepper orientation="vertical" activeStep={step} classes={{
        vertical: classes.stepper,
      }}>
        <Step>
          <StepLabel StepIconComponent={StepIcon}>
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
            <Button lg className={classes.button} to={`${window.eave.apiBase}/oauth/atlassian/authorize`}>
              Connect
            </Button>
          </StepContent>
        </Step>
        <Step>
          <StepLabel StepIconComponent={StepIcon} onClick={handleStepClick}>
            <Copy variant="h3" className={classNames(classes.header, { [classes.clickable]: isStep2Clickable })} >
              Step 2: Select your Confluence Space
              {isStep2Clickable && <DownIcon className={classes.downIcon} />}
            </Copy>
          </StepLabel>
          <StepContent className={classes.content}>
            <Copy variant="pSmall">This will allow Eave to automatically generate documentation in Confluence.</Copy>
            <div>
              <FormControl variant='outlined' className={classes.select}>
                <InputLabel id="space-selector-label">Eave Megastar Beta Team</InputLabel>
                <Select
                  labelId="space-selector-label"
                  id="space-selector"
                  value={teamInfo?.integrations?.atlassian?.confluence_space_key || ''}
                  onChange={handleSpaceUpdate}
                >
                  <MenuItem value="">
                    None
                  </MenuItem>
                  {teamInfo?.integrations?.atlassian?.available_confluence_spaces.map((space) => {
                    return (
                      <MenuItem value={space.key} key={space.key}>{space.name}</MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </div>
          </StepContent>
        </Step>
        <Step>
          <StepLabel StepIconComponent={StepIcon}>
            <Copy variant="h3" className={classes.header}>Step 3: Integrate your business tools</Copy>
          </StepLabel>
          <StepContent className={classes.content}>
            <Copy variant="pSmall" className={classes.copy}>Select the tools where Eave can pull information from and be tagged to created documentation. Note Jira is automatically granted permissions via the Confluence connection.</Copy>
            <Button
              className={classes.connectButton}
              variant="outlined"
              startIcon={teamInfo?.integrations.github && <PurpleCheckIcon className={classes.connected} />}
              disabled={!!teamInfo?.integrations.github}
              to={`${window.eave.apiBase}/oauth/github/authorize`}
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
              startIcon={teamInfo?.integrations.slack && <PurpleCheckIcon className={classes.connected} />}
              disabled={!!teamInfo?.integrations.slack}
              to={`${window.eave.apiBase}/oauth/slack/authorize`}
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
              startIcon={teamInfo?.integrations.atlassian && <PurpleCheckIcon className={classes.connected} />}
              disabled={!!teamInfo?.integrations.atlassian}
              to={`${window.eave.apiBase}/oauth/atlassian/authorize`}
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
      <Footnote />
    </section>
  );
};

export default Steps;
