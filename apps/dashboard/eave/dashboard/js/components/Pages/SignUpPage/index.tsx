import { styled } from "@mui/material";
import React, { useCallback } from "react";

import accountValuePropsSrc from "../../../../static/images/vivial-account-value-props.png";
import AuthForm from "../../Forms/AuthForm";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const ValuePropsImg = styled("img")(() => ({
  marginTop: 32,
  width: "100%",
  height: "auto",
}));

const SignUpPage = () => {
  const handleSubmit = useCallback((email: string, password: string) => {
    console.log("email:", email);
    console.log("password:", password);
  }, []);

  return (
    <PageContainer>
      <AuthForm
        title="Create a free account to book"
        cta="Create Free Account"
        onSubmit={handleSubmit}
        validateEmail
        validatePassword
        showLegal
      />
      <ValuePropsImg src={accountValuePropsSrc} />
    </PageContainer>
  );
};

export default SignUpPage;
