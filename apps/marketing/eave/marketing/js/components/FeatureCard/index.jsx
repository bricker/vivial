import React from "react";
import { makeStyles } from "@material-ui/styles";
import { Typography } from "@material-ui/core";

import Button from "../Button/index.jsx";
import classNames from "classnames";

const makeClasses = makeStyles((theme) => ({
  container: {
    border: `1px solid ${theme.palette.secondary.main}`,
    color: theme.palette.background.contrastText,
    position: 'relative',
    width: '100%',
    padding: 22,
    [theme.breakpoints.up('md')]: {
      display: 'inline-block',
      width: 317,
    }
  },
  title: {
    fontSize: 20,
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    marginBottom: 16,
  },
  comingSoon: {
    backgroundColor: theme.palette.background.main,
    color: theme.palette.secondary.main,
    position: 'absolute',
    top: -10,
    left: 15,
    width: 122,
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 700,
  },
}));

const FeatureCard = ({ title, description, comingSoon, onClick, className }) => {
  const classes = makeClasses();
  const containerClass = classNames(classes.container, className);

  return (
    <div className={containerClass}>
      {comingSoon && (
        <div className={classes.comingSoon}>
          Coming Soon!
        </div>
      )}
      <Typography className={classes.title} variant="h3">
        {title}
      </Typography>
      <Typography className={classes.description}>
        {description}
      </Typography>
      <Button
        onClick={onClick}
        disabled={comingSoon}
        color="secondary"
      >
        Turn On
      </Button>
    </div>
  );
}

export default FeatureCard;
