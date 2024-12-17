import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";

import { loggedIn } from "$eave-dashboard/js/store/slices/authSlice";
import { useLoginMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";

import { AppRoute, SearchParam } from "$eave-dashboard/js/routes";
import AuthForm from "../../Forms/AuthForm";
import Link from "../../Links/Link";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const SignUp = styled("p")(() => ({
  margin: "32px 0 0",
  fontSize: rem(18),
  lineHeight: rem(18),
  textAlign: "center",
}));

const LogInPage = () => {
  const [login, { isLoading }] = useLoginMutation();
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();

  let redirectRoute: string = AppRoute.root;

  const redirectQueryParam = searchParams.get(SearchParam.redirect);
  if (redirectQueryParam) {
    redirectRoute = decodeURIComponent(redirectQueryParam);
  }

  const handleSubmit = useCallback(async ({ email, password }: { email: string; password: string }) => {
    const resp = await login({ input: { email, plaintextPassword: password } });
    const typename = resp.data?.login.__typename;
    switch (typename) {
      case "LoginSuccess": {
        dispatch(loggedIn({ account: resp.data!.login.account }));
        navigate(redirectRoute);
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
        Don't have an account?{" "}
        <Link to={AppRoute.signup} preserveQueryParams>
          Sign up
        </Link>
      </SignUp>
    </PageContainer>
  );
};

export default LogInPage;
