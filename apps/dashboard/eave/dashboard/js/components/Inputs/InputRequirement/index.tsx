import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React from "react";

import Typography from "@mui/material/Typography";
import ErrorIcon from "../../Icons/ErrorIcon";
import SuccessIcon from "../../Icons/SuccessIcon";

const ReqContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  padding: "0 4px",
}));

const Req = styled(Typography)(() => ({
  marginLeft: 4,
  fontSize: "inherit",
  lineHeight: "inherit",
}));

interface InputReqProps {
  children: React.ReactNode;
  met: boolean;
}

const InputRequirement = ({ met = false, children }: InputReqProps) => {
  const color = met ? colors.passingGreen : colors.midGreySecondaryField;
  const icon = met ? <SuccessIcon /> : <ErrorIcon color={color} />;
  return (
    <ReqContainer>
      {icon}
      <Req color={color}>{children}</Req>
    </ReqContainer>
  );
};

export default InputRequirement;
