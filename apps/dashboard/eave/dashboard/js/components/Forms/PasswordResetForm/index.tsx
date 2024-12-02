import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getPasswordInfo, passwordIsValid } from "$eave-dashboard/js/util/password";
import { Typography, styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LoadingButton from "../../Buttons/LoadingButton";
import SecondaryButton from "../../Buttons/SecondaryButton";
import InputError from "../../Inputs/InputError";
import SensitiveInput from "../../Inputs/SensitiveInput";
import PasswordRequirements from "../../PasswordRequirements";

const FormContainer = styled("form")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const TitleContainer = styled("div")(() => ({}));

const Subtitle = styled(Typography)(() => ({
  marginTop: 8,
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "0 16px",
}));

const SpreadButtonsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const PaddedPrimaryButton = styled(LoadingButton)(() => ({
  padding: "10px 14px",
  minWidth: rem("76px"),
}));

const PaddedSecondaryButton = styled(SecondaryButton)(() => ({
  padding: "10px 14px",
  minWidth: rem("76px"),
}));

const PasswordResetForm = () => {
  const navigate = useNavigate();
  const isLoading = false; // TODO: swap for networkign
  const [newPassword, setNewPassword] = useState("");
  const [retypedPassword, setRetypedPassword] = useState("");
  const [isPasswordValid, setIsPasswordValid] = useState(false);
  const [internalError, setInternalError] = useState<string | undefined>(undefined);
  const error = internalError; //|| externalError;
  const isDisabled = !isPasswordValid || !!error;

  useEffect(() => {
    setInternalError(undefined);
    if (newPassword && retypedPassword) {
      if (newPassword !== retypedPassword) {
        setInternalError("Passwords do not match");
      } else {
        setIsPasswordValid(passwordIsValid(getPasswordInfo(newPassword)));
      }
    } else {
      setIsPasswordValid(false);
    }
  }, [newPassword, retypedPassword]);

  const handleSubmit = useCallback((e: React.FormEvent<HTMLFormElement>) => {
    // todo send pw reset
    e.preventDefault();
    return false;
  }, []);

  return (
    <FormContainer onSubmit={handleSubmit}>
      <TitleContainer>
        <Typography variant="h2">Password reset</Typography>
        <Subtitle variant="subtitle2">Input your new password below:</Subtitle>
      </TitleContainer>

      <PasswordRequirements passwordInfo={getPasswordInfo(newPassword)} verticalLayout />

      <SensitiveInput placeholder="New password" onChange={(e) => setNewPassword(e.target.value)} />
      <SensitiveInput placeholder="Retype new password" onChange={(e) => setRetypedPassword(e.target.value)} />

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}

      <SpreadButtonsContainer>
        <PaddedSecondaryButton onClick={() => navigate(-1)}>Cancel</PaddedSecondaryButton>
        <PaddedPrimaryButton type="submit" loading={isLoading} disabled={isDisabled}>
          Save
        </PaddedPrimaryButton>
      </SpreadButtonsContainer>
    </FormContainer>
  );
};

export default PasswordResetForm;
