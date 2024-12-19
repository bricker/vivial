import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import React from "react";
import TooltipIcon from "../../Icons/TooltipIcon";

interface TooltipButtonProps {
  info: string;
  iconColor?: string;
  iconLarge?: boolean;
}

const Button = styled(IconButton)(() => ({
  padding: 0,
}));

const tooltipBorderStyle = "1px solid #4A4A4A"; // one-off color
const tooltipBgStyle = "#131313"; // one-off color
const tooltipStyles = {
  color: colors.whiteText,
  padding: "24px",
  borderRadius: "8px",
  maxWidth: 260,
  fontSize: rem(14),
  lineHeight: rem(16),
  backgroundColor: tooltipBgStyle,
  border: tooltipBorderStyle,
};
const arrowStyles = {
  color: tooltipBgStyle,
  "&:before": {
    border: tooltipBorderStyle,
  },
};

const TooltipButton = ({ info, iconColor, iconLarge }: TooltipButtonProps) => {
  return (
    <Tooltip slotProps={{ tooltip: { sx: tooltipStyles }, arrow: { sx: arrowStyles } }} title={info} arrow>
      <Button>
        <TooltipIcon color={iconColor} large={iconLarge} />
      </Button>
    </Tooltip>
  );
};

export default TooltipButton;
