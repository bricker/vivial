import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React from "react";

import Button from "../Button/index.jsx";
import CheckIcon from "../Icons/CheckIcon.jsx";

const makeClasses = makeStyles((theme) => ({
  container: {
    color: theme.palette.background.contrastText,
    border: `1px solid ${theme.palette.primary.main}`,
    borderRadius: 10,
    fontSize: 20,
    width: "auto",
    height: 68,
    padding: "0 22px",
    "&:hover": {
      backgroundColor: theme.palette.background.main,
    },
  },
  checkIcon: {
    marginLeft: 10,
  },
}));

const FeatureSettingCard = ({ children, className, onClick }) => {
  const classes = makeClasses();
  const containerClass = classNames(classes.container, className);
  return (
    <Button
      className={containerClass}
      onClick={onClick}
      variant="outlined"
      disableRipple
    >
      {children} <CheckIcon className={classes.checkIcon} />
    </Button>
  );
};

export default FeatureSettingCard;
