import { UpdateAccountFailureReason } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { useUpdateAccountMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getPasswordInfo, passwordIsValid } from "$eave-dashboard/js/util/password";
import { Typography, styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
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
  fontSize: rem(12),
  lineHeight: rem(16),
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
  minWidth: rem(76),
}));

const PaddedSecondaryButton = styled(SecondaryButton)(() => ({
  padding: "10px 14px",
  minWidth: rem(76),
}));

const PasswordResetForm = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [updateAccount, { isLoading }] = useUpdateAccountMutation();
  const [newPassword, setNewPassword] = useState("");
  const [retypedPassword, setRetypedPassword] = useState("");
  const [isPasswordValid, setIsPasswordValid] = useState(false);
  const [internalError, setInternalError] = useState<string | undefined>(undefined);
  const [externalError, setExternalError] = useState<string | undefined>(undefined);
  const error = internalError || externalError;
  const isDisabled = !isPasswordValid || !!internalError;

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

  const handleSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setExternalError(undefined);
      try {
        const resp = await updateAccount({ input: { plaintextPassword: newPassword } });
        switch (resp.data?.viewer.__typename) {
          case "AuthenticatedViewerMutations": {
            const respData = resp.data.viewer.updateAccount;
            switch (respData.__typename) {
              case "UpdateAccountSuccess":
                navigate(AppRoute.account);
                break;
              case "UpdateAccountFailure":
                switch (respData.failureReason) {
                  case UpdateAccountFailureReason.ValidationErrors: {
                    const invalidFields = respData.validationErrors?.map((e) => e.field).join(", ");
                    setExternalError(`The following fields are invalid: ${invalidFields}`);
                    break;
                  }
                  case UpdateAccountFailureReason.WeakPassword: {
                    setExternalError("The password does not meet the minimum requirements.");
                    break;
                  }
                  default:
                    console.error("Unexpected case for UpdateAccountFailure");
                    break;
                }
                break;
              default:
                throw new Error("Unexected Graphql result");
            }
            break;
          }
          case "UnauthenticatedViewer":
            dispatch(loggedOut());
            window.location.assign(AppRoute.logout);
            break;
          default:
            if (resp.error) {
              // 500 error
              throw new Error("Graphql error");
            }
            // else loading/not-requested
            break;
        }
      } catch {
        // handle network error
        setExternalError("Unable to change your password. Please try again later.");
      }
    },
    [newPassword],
  );

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
