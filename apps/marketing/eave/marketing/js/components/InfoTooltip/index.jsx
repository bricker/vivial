import React from "react";
import classNames from "classnames";
import { makeStyles } from "@material-ui/styles";
import { IconButton, Tooltip } from "@material-ui/core";
import InfoIcon from "../Icons/InfoIcon.jsx";

const makeClasses = makeStyles(() => ({
  tooltip: {
    padding: 14,
    backgroundColor: '#F1F1F1',
    color: '#3E3E3E',
    fontSize: 14,
    borderRadius: 10,
    '& > p': {
      margin: '0 0 16px',
      '&:last-of-type': {
        marginBottom: 0,
      }
    }
  },
  arrow: {
    color: '#F1F1F1',
  },
  iconBtn: {
    padding: 0,
  },
}));

const InfoTooltip = ({ children, className, disabled }) => {
  const classes = makeClasses();
  const iconBtnClass = classNames(classes.iconBtn, className);
  const iconColor = disabled ? '#808182' : '#3179E7';

  return (
    <Tooltip
      classes={{
        tooltip: classes.tooltip,
        arrow: classes.arrow
      }}
      disableFocusListener={disabled}
      disableHoverListener={disabled}
      disableTouchListener={disabled}
      title={children}
      placement="top"
      arrow
    >
      <IconButton className={iconBtnClass}>
        <InfoIcon color={iconColor} />
      </IconButton>
    </Tooltip>
  );
}

export default InfoTooltip;
