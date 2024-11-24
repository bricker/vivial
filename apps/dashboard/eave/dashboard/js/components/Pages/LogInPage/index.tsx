import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { loggedIn } from "$eave-dashboard/js/store/slices/authSlice";
import { useLoginMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";

import AuthForm from "../../Forms/AuthForm";
import Link from "../../Links/Link";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const SignUp = styled("p")(() => ({
  margin: "32px 0 0",
  fontSize: rem("18px"),
  lineHeight: rem("18px"),
  textAlign: "center",
}));

const LogInPage = () => {
  const [login, { isLoading }] = useLoginMutation();
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleSubmit = useCallback(async ({ email, password }: { email: string; password: string }) => {
    const resp = await login({ email, plaintextPassword: password });
    const typename = resp.data?.data.login.__typename;
    switch (typename) {
      case "LoginSuccess": {
        const accountId = resp.data?.data.login.account.id;
        if (accountId) {
          dispatch(loggedIn({ accountId }));
          navigate("/");
        }
        break;
      }
      case "LoginFailure": {
        setError("Incorrect email or password.");
        break;
      }
      default: {
        setError("Unable to log in. Reach out to friends@vivialapp.com.");
      }
    }
  }, []);

  return (
    <PageContainer>
      <AuthForm
        title="Log in"
        cta="Log in"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        externalError={error}
        showForgotPassword
      />
      <SignUp>
        Don’t have an account? <Link to="/signup">Sign up</Link>
      </SignUp>
    </PageContainer>
  );
};

export default LogInPage;
