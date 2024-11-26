import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { CreateAccountFailureReason } from "$eave-dashboard/js/graphql/generated/graphql";
import { loggedIn } from "$eave-dashboard/js/store/slices/authSlice";
import { useCreateAccountMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { imageUrl } from "$eave-dashboard/js/util/asset";

import { AppRoute } from "$eave-dashboard/js/routes";
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
  const [createAccount, { isLoading }] = useCreateAccountMutation();
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleSubmit = useCallback(async ({ email, password }: { email: string; password: string }) => {
    const resp = await createAccount({ email, plaintextPassword: password });
    const typename = resp.data?.data.createAccount.__typename;
    switch (typename) {
      case "CreateAccountSuccess": {
        dispatch(loggedIn({ account: resp.data!.data.createAccount.account }));
        navigate(AppRoute.root);
        break;
      }
      case "CreateAccountFailure": {
        const failureReason = resp.data?.data.createAccount.failureReason;
        if (failureReason === CreateAccountFailureReason.AccountExists) {
          setError("This account already exists.");
        } else {
          setError("Unable to create account. Reach out to friends@vivialapp.com.");
        }
        break;
      }
      default: {
        setError("Unable to create account. Try again later.");
      }
    }
  }, []);

  return (
    <PageContainer>
      <AuthForm
        title="Create a free account to book"
        cta="Create Free Account"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        externalError={error}
        validateEmail
        validatePassword
        showLegal
      />
      <ValuePropsImg src={imageUrl("vivial-account-value-props.png")} />
    </PageContainer>
  );
};

export default SignUpPage;
