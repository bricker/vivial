import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getPasswordInfo, passwordIsValid } from "$eave-dashboard/js/util/password";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import * as EmailValidator from "email-validator";
import React, { useCallback, useState } from "react";

import LoadingButton from "../../Buttons/LoadingButton";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";
import InputReq from "../../Inputs/InputRequirement";
import SensitiveInput from "../../Inputs/SensitiveInput";
import Link from "../../Links/Link";

const FormContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: 15,
  padding: "32px 0",
}));

const FormContent = styled("div")(() => ({
  padding: "0 40px",
}));

const TitleContainer = styled("div")(() => ({
  marginBottom: 16,
}));

const Subtitle = styled(Typography)(() => ({
  marginTop: 8,
}));

const EmailInput = styled(Input)(() => ({
  marginBottom: 16,
}));

const AuthButton = styled(LoadingButton)(() => ({
  margin: "24px 0",
}));

const ForgotPassword = styled("div")(() => ({
  textAlign: "right",
  fontSize: rem("18px"),
  lineHeight: rem("18px"),
}));

const Legal = styled("p")(({ theme }) => ({
  color: theme.palette.grey[500],
  margin: 0,
  fontSize: rem("14px"),
  lineHeight: rem("18px"),
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  display: "flex",
  alignItems: "center",
  marginTop: 10,
  padding: "0 40px 0 56px",
}));

const InputReqsContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  marginTop: 10,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

interface AuthFormProps {
  title: string;
  cta: string;
  onSubmit: (args: { email: string; password: string }) => void;
  subtitle?: string;
  externalError?: string;
  isLoading?: boolean;
  validateEmail?: boolean;
  validatePassword?: boolean;
  showForgotPassword?: boolean;
  showLegal?: boolean;
}

const AuthForm = ({
  title,
  cta,
  onSubmit,
  subtitle = "",
  externalError = "",
  isLoading = false,
  validateEmail = false,
  validatePassword = false,
  showForgotPassword = false,
  showLegal = false,
}: AuthFormProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isDisabled, setIsDisabled] = useState(true);
  const [showPasswordInfo, setShowPasswordInfo] = useState(false);
  const [passwordInfo, setPasswordInfo] = useState({
    hasEightChars: false,
    hasSpecialChar: false,
    hasLetter: false,
    hasDigit: false,
  });
  const [internalError, setInternalError] = useState("");
  const error = externalError || internalError;

  const handleSubmit = useCallback(() => {
    if (validateEmail && !EmailValidator.validate(email)) {
      setInternalError("Invalid email address.");
      setShowPasswordInfo(false);
      setIsDisabled(true);
      return;
    }
    onSubmit({ email, password });
  }, [email, password]);

  const checkInputs = ({ currentEmail, currentPassword }: { currentEmail: string; currentPassword: string }) => {
    setInternalError("");
    if (validatePassword && currentPassword) {
      const newPasswordInfo = getPasswordInfo(currentPassword);
      setPasswordInfo(newPasswordInfo);
      setShowPasswordInfo(true);
      if (currentEmail && passwordIsValid(newPasswordInfo)) {
        setIsDisabled(false);
      } else {
        setIsDisabled(true);
      }
    } else if (currentEmail && currentPassword) {
      setIsDisabled(false);
    } else {
      setIsDisabled(true);
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    checkInputs({ currentEmail: newEmail, currentPassword: password });
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    checkInputs({ currentPassword: newPassword, currentEmail: email });
  };

  return (
    <FormContainer>
      <FormContent>
        <TitleContainer>
          <Typography variant="h2">{title}</Typography>
          {subtitle && <Subtitle variant="subtitle2">{subtitle}</Subtitle>}
        </TitleContainer>
        <EmailInput placeholder="Email" onChange={handleEmailChange} />
        <SensitiveInput placeholder="Password" onChange={handlePasswordChange} />
      </FormContent>
      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}
      {showPasswordInfo && (
        <InputReqsContainer>
          <InputReq met={passwordInfo.hasEightChars}>8 characters</InputReq>
          <InputReq met={passwordInfo.hasLetter && passwordInfo.hasDigit}>1 letter and 1 digit</InputReq>
          <InputReq met={passwordInfo.hasSpecialChar}>1 special character</InputReq>
        </InputReqsContainer>
      )}
      <FormContent>
        <AuthButton onClick={handleSubmit} loading={isLoading} disabled={isDisabled} fullWidth>
          {cta}
        </AuthButton>
        {showForgotPassword && (
          <ForgotPassword>
            <Link to="/login/password">Forgot password?</Link>
          </ForgotPassword>
        )}
        {showLegal && (
          <Legal>
            By clicking “{cta}” above, you are agreeing to Vivial’s{" "}
            <Link to="/terms" underline>
              TOS
            </Link>{" "}
            and{" "}
            <Link to="/privacy" underline>
              Privacy Policy
            </Link>
            .
          </Legal>
        )}
      </FormContent>
    </FormContainer>
  );
};

export default AuthForm;
