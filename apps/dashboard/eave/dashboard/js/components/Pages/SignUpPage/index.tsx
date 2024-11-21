import { styled } from "@mui/material";
import React, { useCallback } from "react";
import { useAppDispatch } from "$eave-dashboard/js/store/hooks";




import { authenticateUser } from '$eave-dashboard/js/store/auth/thunks';

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
  const dispatch = useAppDispatch();

  const handleSubmit = useCallback(async (email: string, password: string) => {

    await dispatch(authenticateUser({ email, password }));

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
