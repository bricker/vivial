import React, { useCallback, useState } from "react";
import classNames from "classnames";
import { makeStyles } from "@material-ui/styles";
import { Dialog, IconButton, Typography } from '@material-ui/core';

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
    [theme.breakpoints.up('md')]: {
      backgroundColor: theme.palette.background.light,
      height: 'auto',
      padding: '60px 54px 44px',
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
      marginBottom: 10,
      fontSize: 36,
    }
  },
  githubRequirement: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 14,
    [theme.breakpoints.up('md')]: {
      flexDirection: 'column',
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
    color: "#E03C6C",
    [theme.breakpoints.up('md')]: {
      fontSize: 18,
      marginBottom: 36,
    }
  },
  children: {
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
  btnContainer: {
    [theme.breakpoints.up('md')]: {
      display: 'flex',
      justifyContent: 'flex-end',
    }
  },
  btn: {
    width: '100%',
    marginTop: 30,
    fontSize: 20,
    [theme.breakpoints.up('md')]: {
      marginTop: 40,
      width: 200,
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
  defaultText: {
    display: 'inline-block',
    marginLeft: 4,
    fontWeight: 700,
  },
  expandBtnContainer: {
    marginTop: 12,
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
    margin: '14px 0',
  }
}));


const GitHubFeatureModal = ({
  children,
  onClose,
  onTurnOn,
  open,
  title,
  enabledRepoIds,
}) => {
  const classes = makeClasses();
  const { team } = useTeam();
  const githubIntegration = team.integrations.github_integration;
  const githubLogoFile = githubIntegration ? 'eave-github-logo-installed.png' : 'eave-github-logo-required.png';
  const githubOauthUrl = `${window.eave.apiBase}/oauth/github/authorize`;
  const [optionsExpanded, setOptionsExpanded] = useState(true); // TODO: false default
  const accessibleRepoIds = team.accessibleRepos.map(repo => repo.id);
  const [selectedRepoIds, setSelectedRepoIds] = useState(enabledRepoIds.length ? enabledRepoIds : accessibleRepoIds);
  const [selectedReposDesc, setSelectedReposDesc] = useState("Default");
  const selectedReposTextClass = classNames(
    classes.selectedReposText,
    !githubIntegration && classes.disabledText,
  );

  const toggleExpandOptions = () => {
    setOptionsExpanded(!optionsExpanded);
  };

  const handleTurnOn = useCallback(() => {
    onTurnOn(team.id, selectedRepoIds);
  }, [team.id, selectedRepoIds]);




  const handleSelectRepo = useCallback((val) => {
    if (val === "default") {
      setSelectedRepoIds(accessibleRepoIds);
      setSelectedReposDesc("Default");
      return;
    }
    if (selectedRepoIds.includes(val)) {
      const newSelectedRepoIds = selectedRepoIds.filter(id => id !== val);
      setSelectedRepoIds(newSelectedRepoIds);
      setSelectedReposDesc("Custom");
      return;
    }
    setSelectedRepoIds([...selectedRepoIds, val]);
    if ((selectedRepoIds.length + 1) === accessibleRepoIds.length) {
      setSelectedReposDesc("Default");
    }
  }, [selectedRepoIds]);







  return (
    <Dialog
      classes={{ paper: classes.paper }}
      onClose={onClose}
      open={open}
    >
      <IconButton className={classes.closeButton} onClick={onClose}>
        <CloseIcon />
      </IconButton>
      <Typography className={classes.title} variant="h2">
        {title}
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
      <div className={classes.children}>
        {children}
      </div>
      <div className={selectedReposTextClass}>
        Selected Repositories: <span className={classes.defaultText}>{selectedReposDesc}</span>
        <InfoTooltip className={classes.tooltip} disabled={!githubIntegration}>
          <p>By default, this feature will access all repositories provided to the Eave for GitHub app.</p>
          <p>To select a custom subset of repos, click “Advanced Options”, or to update what Eave for GitHub can access, go to the app settings in your GitHub account (settings/apps/eave-fyi/permissions).</p>
        </InfoTooltip>
      </div>
      {githubIntegration && (
        <div className={classes.expandBtnContainer}>
          <Button className={classes.expandBtn} onClick={toggleExpandOptions} variant="text">
            Advanced Options <ExpandIcon up={optionsExpanded} />
          </Button>
        </div>
      )}
      {optionsExpanded && (
        <>
          <Typography className={classes.selectText}>
            Select Individual Repositories
          </Typography>
          <GitHubRepoSelect
            repos={team.accessibleRepos}
            selectedRepoIds={selectedRepoIds}
            onSelect={handleSelectRepo}
          />
        </>
      )}
      <div className={classes.btnContainer}>
        {githubIntegration ? (
          <Button onClick={handleTurnOn} className={classes.btn} color="secondary" >
            Turn On
          </Button>
        ) : (
          <Button to={githubOauthUrl} className={classes.btn} color="secondary">
            Add App
          </Button>
        )}
      </div>
    </Dialog>
  );
};


export default GitHubFeatureModal;
