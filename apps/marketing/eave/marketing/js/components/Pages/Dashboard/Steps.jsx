import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  StepContent,
  StepLabel,
  Step,
  Stepper,
  Select,
  FormControl,
  MenuItem,
  useMediaQuery,
  CircularProgress,
  InputLabel,
} from '@material-ui/core';
import classNames from 'classnames';

import { HEADER, INTEGRATION_LOGOS } from '../../../constants.js';
import useUser from '../../../hooks/useUser.js';
import Copy from '../../Copy/index.jsx';
import Button from '../../Button/index.jsx';
import PurpleCheckIcon from '../../Icons/PurpleCheckIcon.jsx';
import ConfluenceIcon from '../../Icons/ConfluenceIcon.jsx';
import AtlassianIcon from '../../Icons/AtlassianIcon.jsx';
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
    '& .MuiStepLabel-completed svg': {
      opacity: 0.7,
    },
  },
  selectWrapper: {
    display: 'flex',
    flexDirection: 'column',
    [theme.breakpoints.up('sm')]: {
      flexDirection: 'row',
    },
  },
  select: {
    width: 275,
    marginTop: 12,
    [theme.breakpoints.up('sm')]: {
      width: 418,
    },
  },
  error: {
    color: 'red',
    marginTop: 12,
  },
  submit: {
    width: 275,
    height: 56,
    marginTop: 12,
    [theme.breakpoints.up('sm')]: {
      width: 166,
      marginLeft: 30,
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
  atlassian: {
    width: 95,
    [theme.breakpoints.up('sm')]: {
      width: 144,
    },
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
  completed: {
    opacity: 0.5,
  },
}));

const Steps = () => {
  const classes = makeClasses();
  const isDesktop = useMediaQuery((theme) => theme.breakpoints.up('md'));
  const { userState, updateConfluenceSpace, loadingUpdateConfluenceSpace, updateConfluenceError } = useUser();
  const { teamInfo } = userState;
  const [step, setStep] = useState(2);
  const [space, setSpace] = useState('');
  const [editingSpace, setEditingSpace] = useState(false);
  // placeholder until flow is integrated
  const [appInstalled, setAppInstalled] = useState(true);

  useEffect(() => {
    if (!appInstalled) {
      setStep(0);
    } else if (!teamInfo?.integrations.atlassian) {
      setStep(1);
      // if user has not selected a conflunece space
    } else if (!teamInfo?.integrations.atlassian.confluence_space_key || editingSpace) {
      setStep(2);
    // confluence integration happens by default, if user has not linked their github or slack
    } else if (!teamInfo?.integrations.github || !teamInfo?.integrations.slack) {
      setStep(3);
    // user has linked all so we can just show a completed stepper
    } else {
      setStep(4);
    }
  }, [teamInfo, appInstalled, space]);

  const isStep3Clickable = step > 2 && teamInfo?.integrations?.atlassian?.confluence_space_key.length > 0;

  const handleSpaceUpdate = () => {
    updateConfluenceSpace(space, () => setEditingSpace(false));
  };

  const handleSelectChange = (event) => {
    setSpace(event.target.value);
  };

  const handleStepClick = () => {
    if (isStep3Clickable) {
      setSpace(teamInfo?.integrations.atlassian.confluence_space_key);
      setEditingSpace(true);
      setStep(2);
    }
  };

  console.log('space', space);
  console.log(teamInfo?.integrations.atlassian.confluence_space_key);
  console.log('editingSpace', editingSpace)

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
              Step 1: Add Eave to <AtlassianIcon className={classes.atlassian} />
            </Copy>
          </StepLabel>
          <StepContent className={classes.content}>
            <Copy variant="pSmall">Add Eave, and then come back to this page to complete setup.</Copy>
            <Button
              lg
              className={classes.button}
              onClick={() => setAppInstalled(true)}
              target="_blank"
              href="https://developer.atlassian.com/console/install/e3c57ac8-296e-4392-b128-4330b1ab2883/?signature=9e7204e3d1f2898b576427da60ab2182353879b1173469f1b59e0e9cab271d5439c0ff55d59dab60621d9c871125afe79fac266aa532eb29778a2d751bbe0508&product=confluence&product=jira"
            >
              Add App
            </Button>
          </StepContent>
        </Step>
        <Step>
          <StepLabel StepIconComponent={StepIcon}>
            <Copy variant="h3" className={classes.header}>
              {isDesktop ? (
                <span>
                  Step 2: Connect to your <ConfluenceIcon /> Confluence Account
                </span>
              ) : (
                <span>
                  Step 2: Connect to <ConfluenceIcon /> Confluence
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
            <Copy variant="h3" className={classNames(classes.header, { [classes.clickable]: isStep3Clickable })} >
              Step 3: Select your <ConfluenceIcon /> Confluence Space
              {isStep3Clickable && <DownIcon className={classes.downIcon} />}
            </Copy>
          </StepLabel>
          <StepContent className={classes.content}>
            <Copy variant="pSmall">This will allow Eave to automatically generate documentation in Confluence.</Copy>
            <div className={classes.selectWrapper}>
              <FormControl variant='outlined' className={classes.select}>
              {!space && <InputLabel id="space-selector-label">Select your Confluence Space</InputLabel>}
                <Select
                  labelId="space-selector-label"
                  id="space-selector"
                  value={space}
                  onChange={handleSelectChange}
                  disabled={loadingUpdateConfluenceSpace}
                >
                  {teamInfo?.integrations?.atlassian?.available_confluence_spaces.map((spc) => {
                    return (
                      <MenuItem value={spc.key} key={spc.key}>{spc.name}</MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
              <Button
                  className={classes.submit}
                  onClick={handleSpaceUpdate}
                  disabled={loadingUpdateConfluenceSpace}
                >
                  {loadingUpdateConfluenceSpace ? (
                    <CircularProgress />
                  ) : (
                    'Submit'
                  )}
                </Button>
            </div>
            {updateConfluenceError && (
              <Copy variant="footnote" className={classes.error}>Something went wrong setting the Confluence space, please try again</Copy>
            )}
          </StepContent>
        </Step>
        <Step>
          <StepLabel StepIconComponent={StepIcon}>
            <Copy variant="h3" className={classes.header}>Step 4: Integrate your business tools</Copy>
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
                className={classNames(classes.githubButtonLogo, { [classes.completed]: teamInfo?.integrations.github })}
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
                className={classNames(classes.slackButtonLogo, { [classes.completed]: teamInfo?.integrations.slack })}
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
                className={classNames(classes.jiraButtonLogo, { [classes.completed]: teamInfo?.integrations.atlassian })}
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
