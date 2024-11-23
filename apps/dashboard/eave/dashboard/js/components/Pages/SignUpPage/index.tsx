import { styled } from "@mui/material";
import React, { useCallback, useState, useEffect } from "react";
import { useCreteAccountMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";

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
  const [createAccount, { isLoading, data }] = useCreteAccountMutation();
  const [error, setError] = useState("");

  const handleSubmit = useCallback(async ({ email, password }: { email: string; password: string }) => {
    await createAccount({ email, plaintextPassword: password });
  }, []);

  // TODO: Handle Errors.

  return (
    <PageContainer>
      <AuthForm
        title="Create a free account to book"
        cta="Create Free Account"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        error={error}
        validateEmail
        validatePassword
        showLegal
      />
      <ValuePropsImg src={accountValuePropsSrc} />
    </PageContainer>
  );
};

export default SignUpPage;
