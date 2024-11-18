import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React, { useCallback, useState } from "react";

import Button from "../../Buttons/Button";
import Input from "../../Inputs/Input";
import SensitiveInput from "../../Inputs/SensitiveInput";
import Link from "../../Links/Link";

const FormContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: 15,
  padding: "32px 40px",
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

const PasswordInput = styled(SensitiveInput)(() => ({
  marginBottom: 24,
}));

const AuthButton = styled(Button)(() => ({
  marginBottom: 24,
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

interface AuthFormProps {
  title: string;
  cta: string;
  onSubmit: (email: string, password: string) => void;
  subtitle?: string;
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
  // validateEmail = false,
  // validatePassword = false,
  showForgotPassword = false,
  showLegal = false,
}: AuthFormProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const disabled = !email || !password;

  const handleSubmit = useCallback(() => {
    onSubmit(email, password);
  }, [email, password]);

  return (
    <FormContainer>
      <TitleContainer>
        <Typography variant="h2">{title}</Typography>
        {subtitle && <Subtitle variant="subtitle2">{subtitle}</Subtitle>}
      </TitleContainer>
      <EmailInput placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <PasswordInput placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
      <AuthButton onClick={handleSubmit} disabled={disabled} fullWidth>
        {cta}
      </AuthButton>
      {showForgotPassword && (
        <ForgotPassword>
          <Link to="/login/password">Forgot password?</Link>
        </ForgotPassword>
      )}
      {showLegal && (
        <Legal>
          By clicking “{cta}” above, you are agreeing to Vivial’s <Link to="/terms">TOS</Link> and{" "}
          <Link to="/privacy">Privacy Policy</Link>.
        </Legal>
      )}
    </FormContainer>
  );
};

export default AuthForm;
