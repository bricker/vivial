import BaseVivialIcon from "$eave-dashboard/js/components/Logo/VivialIcon";
import Circle from "$eave-dashboard/js/components/Shapes/Circle";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React from "react";

const Badge = styled("div")(() => ({
  zIndex: 1,
  position: "absolute",
  top: -21.5,
}));

const Connector = styled("div")(() => ({
  position: "absolute",
  height: 32,
  width: 3,
  left: 18,
  top: -32,
  background: "linear-gradient(0deg, rgba(49,43,44,1) 0%, rgba(255,129,181,1) 100%)",
}));

const VivialIcon = styled(BaseVivialIcon)(() => ({
  marginTop: 2,
}));

interface VivialBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  categoryGroupId?: string;
}

const VivialBadge = (props: VivialBadgeProps) => {
  return (
    <Badge {...props}>
      <Connector />
      <Circle color={colors.fieldBackground.primary}>
        <VivialIcon small />
      </Circle>
    </Badge>
  );
};

export default VivialBadge;
