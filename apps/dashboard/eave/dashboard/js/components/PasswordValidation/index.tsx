import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { PasswordInfo } from "$eave-dashboard/js/util/password";
import { styled } from "@mui/material";
import React from "react";
import InputRequirement from "../Inputs/InputRequirement";

const HorizontalInputReqsContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  marginTop: 10,
  display: "flex",
  flexDirection: "row",
  gap: 8,
  // alignItems: "center",
  // justifyContent: "center",
}));

const VerticalInputReqsContainer = styled(HorizontalInputReqsContainer)(() => ({
  flexDirection: "column",
}));

const PasswordValidation = ({
  passwordInfo,
  verticalLayout = false,
}: {
  passwordInfo: PasswordInfo;
  verticalLayout?: boolean;
}) => {
  // TODO: vertical/horz layout
  const Container = verticalLayout ? VerticalInputReqsContainer : HorizontalInputReqsContainer;
  return (
    <Container>
      <InputRequirement met={passwordInfo.hasEightChars}>8 characters</InputRequirement>
      <InputRequirement met={passwordInfo.hasLetter && passwordInfo.hasDigit}>1 letter and 1 digit</InputRequirement>
      <InputRequirement met={passwordInfo.hasSpecialChar}>1 special character</InputRequirement>
    </Container>
  );
};

export default PasswordValidation;
