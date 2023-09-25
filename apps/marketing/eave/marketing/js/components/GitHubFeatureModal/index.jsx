import React, { useCallback, useState, useEffect } from "react";
import { useCookies } from "react-cookie";
import { useSearchParams } from "react-router-dom";
import classNames from "classnames";
import { makeStyles } from "@material-ui/styles";
import { Dialog, IconButton, Typography } from '@material-ui/core';

import { FEATURES, COOKIE_NAMES, SEARCH_PARAM_NAMES, SEARCH_PARAM_VALUES } from "../../constants.js";
import { imageUrl } from "../../util/asset-helpers.js";
import useTeam from "../../hooks/useTeam.js";
import CloseIcon from "../Icons/CloseIcon.js";
import ExpandIcon from "../Icons/ExpandIcon.jsx";
import Button from "../Button/index.jsx";
import InfoTooltip from "../InfoTooltip/index.jsx";
import GitHubRepoSelect from "../GitHubRepoSelect/index.jsx";

const makeClasses = makeStyles((theme) => ({
  paper: {
    backgroundColor: theme.palette.background.main,
    color: theme.palette.background.contrastText,
    width: '100vw',
    height: '100vh',
    maxHeight: 'none',
    maxWidth: 762,
    margin: 0,
    padding: '88px 25px',
    overflow: 'visible',
    [theme.breakpoints.up('md')]: {
      backgroundColor: theme.palette.background.light,
      height: 'auto',
      padding: '60px 54px 44px',
    }
  },
  confirmationPaper: {
    [theme.breakpoints.up('md')]: {
      padding: '146px 96px 64px',
    }
  },
  closeButton: {
    position: 'absolute',
    top: 10,
    right: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 400,
    marginBottom: 14,
    [theme.breakpoints.up('md')]: {
      textAlign: 'center',
      marginBottom: 18,
      fontSize: 36,
    }
  },
  githubRequirement: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 14,
    [theme.breakpoints.up('md')]: {
      flexDirection: 'column',
      marginBottom: 30,
    }
  },
  requiredText: {
    marginRight: 10,
    fontSize: 16,
    [theme.breakpoints.up('md')]: {
      fontSize: 18,
      marginRight: 0,
    }
  },
  githubLogo: {
    width: 144,
    [theme.breakpoints.up('md')]: {
      width: 200,
    }
  },
  githubWarning: {
    fontSize: 16,
    fontWeight: 700,
    marginBottom: 25,
    color: theme.palette.error.main,
    [theme.breakpoints.up('md')]: {
      fontSize: 18,
      marginBottom: 36,
    }
  },
  description: {
    fontSize: 18,
    fontWeight: 400,
    marginBottom: 10,
    '& > p': {
      margin: '0 0 30px',
      [theme.breakpoints.up('md')]: {
        margin: '0 0 32px',
      }
    },
    [theme.breakpoints.up('md')]: {
      marginBottom: 0,
    }
  },
  ctaBtnContainer: {
    [theme.breakpoints.up('md')]: {
      display: 'flex',
      justifyContent: 'flex-end',
    }
  },
  ctaBtn: {
    width: '100%',
    fontSize: 20,
    marginTop: 20,
    [theme.breakpoints.up('md')]: {
      width: 'auto',
      minWidth: 200,
      marginTop: 0,
    }
  },
  selectedReposText: {
    display: 'flex',
    alignItems: 'center',
    fontSize: 18,
  },
  disabledText: {
    color: '#808182',
  },
  tooltip: {
    marginLeft: 4,
  },
  selectedReposLabel: {
    display: 'inline-block',
    marginLeft: 4,
    fontWeight: 700,
  },
  expandBtnContainer: {
    marginTop: 8,
  },
  expandBtn: {
    width: 'auto',
    height: 'auto',
    padding: 0,
    color: '#0092C7',
    fontSize: 14,
    '&:hover': {
      backgroundColor: 'transparent',
    }
  },
  selectText: {
    fontSize: 14,
    margin: '11px 0 5px',
  },
  turnOffBtn: {
    color: theme.palette.error.main,
    textDecoration: 'underline',
    fontSize: 16,
    fontWeight: 700,
    position: 'absolute',
    left: 25,
    top: 25,
    width: 'auto',
    height: 'auto',
    padding: 0,
    '&:hover': {
      backgroundColor: 'transparent',
      textDecoration: 'underline',
    },
    [theme.breakpoints.up('md')]: {
      fontSize: 14,
      left: 31,
      top: 22,
    }
  },
  confirmationBtns: {
    marginTop: 42,
    [theme.breakpoints.up('md')]: {
      display: 'flex',
      justifyContent: 'center',
    }
  },
  disableConfirmationBtn: {
    border: `1px solid ${theme.palette.background.contrastText}`,
    color: theme.palette.background.contrastText,
    fontSize: 20,
    width: '100%',
    marginBottom: 10,
    '&:hover': {
      border: `1px solid ${theme.palette.background.contrastText}`,
      backgroundColor: 'transparent',
    },
    [theme.breakpoints.up('md')]: {
      marginBottom: 0,
      marginRight: 15,
      width: 'auto',
    }
  },
  feedbackLinkContainer: {
    marginTop: 90,
    textAlign: 'center',
    [theme.breakpoints.up('md')]: {
      marginTop: 140,
    }
  },
  feedbackLink: {
    color: "#0092C7",
    fontSize: 16,
    fontWeight: 400,
  },
}));

function renderTitle(feature) {
  if (feature === FEATURES.INLINE_CODE_DOCS) {
    return "Inline Code Documentation";
  }
}

function renderDescription(feature) {
  if (feature === FEATURES.INLINE_CODE_DOCS) {
    return (
      <>
        <p>Automate inline code documentation within your GitHub files.</p>
        <p>As changes are made to the codebase, Eave will automatically generate inline documentation via a pull request for your team's review.</p>
      </>
    );
  }
}

const GitHubFeatureModal = ({ onClose, onUpdate, open, feature, param }) => {
  const classes = makeClasses();
  const { team } = useTeam();
  const [_, setCookie] = useCookies([COOKIE_NAMES.FEATURE_MODAL]);
  const [searchParams, setSearchParams] = useSearchParams();
  const githubIntegration = team.integrations.github_integration;
  const githubLogoFile = githubIntegration ? 'eave-github-logo-installed.png' : 'eave-github-logo-required.png';
  const teamRepoIds = team.repos.map(repo => repo.external_repo_id);
  const enabledRepoIds = team.repos
    .filter(repo => repo[feature] === "enabled")
    .map(repo => repo.external_repo_id);
  const allSelected = teamRepoIds.length === enabledRepoIds.length;
  const cta = enabledRepoIds.length ? "Update" : "Turn On"
  const canDisable = !!enabledRepoIds.length;
  const [showDisableConfirmation, setShowDisableConfirmation] = useState(false);
  const [optionsExpanded, setOptionsExpanded] = useState(false);
  const [selectedRepoIds, setSelectedRepoIds] = useState(allSelected ? teamRepoIds : enabledRepoIds);
  const [selectedRepoError, setSelectedRepoError] = useState(null);
  const [selectedReposLabel, setSelectedReposLabel] = useState(allSelected ? "Default" : "Custom");
  const selectedReposTextClass = classNames(
    classes.selectedReposText,
    !githubIntegration && classes.disabledText
  );

  const toggleExpandOptions = useCallback(() => {
    setOptionsExpanded(!optionsExpanded);
  }, [optionsExpanded]);

  const handleClose = useCallback(() => {
    onClose();
    setShowDisableConfirmation(false);
  }, []);

  const handleUpdate = useCallback(() => {
    onUpdate(team.id, teamRepoIds, selectedRepoIds, feature);
  }, [team.id, teamRepoIds, selectedRepoIds]);

  const handleDisable = useCallback(() => {
    onUpdate(team.id, teamRepoIds, [], feature);
  }, [team.id, teamRepoIds]);

  const handleTurnOffClick = useCallback(() => {
    setShowDisableConfirmation(true);
  }, []);

  const handleHideDisableConfirmation = useCallback(() => {
    setShowDisableConfirmation(false);
  }, []);

  const handleAddApp = useCallback(() => {
    setCookie(COOKIE_NAMES.FEATURE_MODAL, feature);
    const githubOauthUrl = `${window.eave.apiBase}/oauth/github/authorize`;
    window.open(githubOauthUrl, "_self");
  }, []);

  const handleSelectRepo = useCallback((val) => {
    const selectionError = "At least one repository must be selected to turn on this feature.";
    if (val === "default") {
      // Case 1: All repos are already selected and user selects "default".
      if (selectedRepoIds.length === teamRepoIds.length) {
        setSelectedRepoIds([]);
        setSelectedReposLabel("Custom");
        setSelectedRepoError(selectionError);
        return;
      }
      // Case 2: One or more repos are not selected and use selects "default".
      setSelectedRepoIds(teamRepoIds);
      setSelectedReposLabel("Default");
      setSelectedRepoError(null);
      return;
    }
    // Case 3: The user is deselecting a repo.
    if (selectedRepoIds.includes(val)) {
      const newSelectedRepoIds = selectedRepoIds.filter(id => id !== val);
      setSelectedRepoIds(newSelectedRepoIds);
      setSelectedReposLabel("Custom");
      if (!newSelectedRepoIds.length) {
        setSelectedRepoError(selectionError);
      }
      return;
    }
    // Case 4: The user is reselecting a repo.
    setSelectedRepoIds([...selectedRepoIds, val]);
    setSelectedRepoError(null);
    if ((selectedRepoIds.length + 1) === teamRepoIds.length) {
      setSelectedReposLabel("Default");
    }
  }, [selectedRepoIds, teamRepoIds]);

  useEffect(() => {
    if (open) {
      const currentParam = searchParams.get(SEARCH_PARAM_NAMES.FEATURE_MODAL);
      if (!currentParam) {
        setSearchParams({[SEARCH_PARAM_NAMES.FEATURE_MODAL]: param });
      }
    } else {
      setSearchParams({});
    }
  }, [searchParams, open]);

  if (showDisableConfirmation) {
    const paperClass = classNames(classes.paper, classes.confirmationPaper);
    return (
      <Dialog classes={{ paper: paperClass }} onClose={handleClose} open={open}>
        <IconButton className={classes.closeButton} onClick={handleClose}>
          <CloseIcon />
        </IconButton>
        <Typography className={classes.title} variant="h2">
          Are you sure you want to turn off {renderTitle(feature)}?
        </Typography>
        <div className={classes.description}>
          Eave will stop automatically updating these documents once this feature is turned off. Updates will need to be made manually.
        </div>
        <div className={classes.confirmationBtns}>
          <Button onClick={handleDisable} className={classes.disableConfirmationBtn} variant="outlined">
            Yes, I'll Manually Update
          </Button>
          <Button onClick={handleHideDisableConfirmation} className={classes.ctaBtn} color="secondary">
            No, Keep Automation
          </Button>
        </div>
        <div className={classes.feedbackLinkContainer}>
          <a className={classes.feedbackLink} href="https://forms.gle/3v5Xdz7kPya5UW9U6" target="_blank">
            Send Feedback
          </a>
        </div>
      </Dialog>
    )
  }

  return (
    <Dialog classes={{ paper: classes.paper }} onClose={handleClose} open={open}>
      {canDisable && (
        <Button className={classes.turnOffBtn} onClick={handleTurnOffClick} variant="text" disableRipple>
          Turn Off
        </Button>
      )}
      <IconButton className={classes.closeButton} onClick={handleClose}>
        <CloseIcon />
      </IconButton>
      <Typography className={classes.title} variant="h2">
        {renderTitle(feature)}
      </Typography>
      <div className={classes.githubRequirement}>
        <Typography className={classes.requiredText}>
          Required for setup:
        </Typography>
        <img className={classes.githubLogo} src={imageUrl(githubLogoFile)} />
      </div>
      {!githubIntegration && (
        <Typography className={classes.githubWarning}>
          This feature requires a GitHub integration. In order to proceed, please add the Eave app to your GitHub account by clicking on the button below.
        </Typography>
      )}
      <div className={classes.description}>
        {renderDescription(feature)}
      </div>
      <div className={selectedReposTextClass}>
        Selected Repositories: <span className={classes.selectedReposLabel}>{selectedReposLabel}</span>
        <InfoTooltip className={classes.tooltip} disabled={!githubIntegration}>
          <p>By default, this feature will access all repositories provided to the Eave for GitHub app.</p>
          <p>To select a custom subset of repos, click “Advanced Options”, or to update what Eave for GitHub can access, go to the app settings in your GitHub account (settings/apps/eave-fyi/permissions).</p>
        </InfoTooltip>
      </div>
      {githubIntegration && (
        <div className={classes.expandBtnContainer}>
          <Button className={classes.expandBtn} onClick={toggleExpandOptions} variant="text" disableRipple>
            Advanced Options <ExpandIcon up={optionsExpanded} color="#0092C7" />
          </Button>
        </div>
      )}
      <div style={{ visibility: optionsExpanded ? 'visible' : 'hidden' }}>
        <Typography className={classes.selectText}>
          Select Individual Repositories
        </Typography>
        <GitHubRepoSelect
          repos={team.repos}
          selectedRepoIds={selectedRepoIds}
          error={selectedRepoError}
          onSelect={handleSelectRepo}
        />
      </div>
      <div className={classes.ctaBtnContainer}>
        {githubIntegration ? (
          <Button onClick={handleUpdate} className={classes.ctaBtn} disabled={!!selectedRepoError} color="secondary" >
            {cta}
          </Button>
        ) : (
          <Button onClick={handleAddApp} className={classes.ctaBtn} color="secondary">
            Add App
          </Button>
        )}
      </div>
    </Dialog>
  );
};

export default GitHubFeatureModal;
