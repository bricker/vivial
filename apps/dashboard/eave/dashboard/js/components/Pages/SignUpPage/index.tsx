import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";

import { CreateAccountFailureReason } from "$eave-dashboard/js/graphql/generated/graphql";
import { loggedIn } from "$eave-dashboard/js/store/slices/authSlice";
import { useCreateAccountMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { imageUrl } from "$eave-dashboard/js/util/asset";

import { AppRoute, DateSurveyPageVariant, SearchParam, SignUpPageVariant, routePath } from "$eave-dashboard/js/routes";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import CloseButton from "../../Buttons/CloseButton";
import AuthForm from "../../Forms/AuthForm";
import Link from "../../Links/Link";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const CloseButtonContainer = styled("div")(() => ({
  textAlign: "end",
  margin: "-8px 0px 8px",
}));

const ValuePropsImg = styled("img")(() => ({
  marginTop: 32,
  width: "100%",
  height: "auto",
}));

const LoginContainer = styled("p")(() => ({
  margin: "32px 0 0",
  fontSize: rem(18),
  lineHeight: rem(18),
  textAlign: "center",
}));

const SignUpPage = () => {
  const [createAccount, { isLoading }] = useCreateAccountMutation();
  const [error, setError] = useState("");
  const [searchParams, _] = useSearchParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const variant = searchParams.get(SearchParam.variant) as SignUpPageVariant;

  let title = "Create a free account to book";
  let allowClose = false;
  let redirectRoute: string = AppRoute.root;

  if (variant === SignUpPageVariant.MultiReroll) {
    title = "Get personalized recommendations";
    allowClose = true;
    redirectRoute = routePath({
      route: AppRoute.root,
      searchParams: { [SearchParam.variant]: DateSurveyPageVariant.PreferencesOpen },
    });
  }

  const redirectQueryParam = searchParams.get(SearchParam.redirect);
  if (redirectQueryParam) {
    redirectRoute = decodeURIComponent(redirectQueryParam);
  }

  const handleSubmit = useCallback(async ({ email, password }: { email: string; password: string }) => {
    const resp = await createAccount({ input: { email, plaintextPassword: password } });
    const typename = resp.data?.createAccount.__typename;
    switch (typename) {
      case "CreateAccountSuccess": {
        dispatch(loggedIn({ account: resp.data!.createAccount.account }));
        navigate(redirectRoute);
        break;
      }
      case "CreateAccountFailure": {
        const failureReason = resp.data?.createAccount.failureReason;
        switch (failureReason) {
          case CreateAccountFailureReason.AccountExists: {
            setError("This account already exists.");
            break;
          }
          case CreateAccountFailureReason.WeakPassword: {
            setError("The password does not meet the minimum requirements.");
            break;
          }
          default: {
            setError("Unable to create account. Reach out to friends@vivialapp.com.");
          }
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
      {allowClose && (
        <CloseButtonContainer>
          <CloseButton onClick={() => navigate(AppRoute.root)} iconColor={colors.whiteText} />
        </CloseButtonContainer>
      )}
      <AuthForm
        title={title}
        subtitle={""}
        cta="Create Free Account"
        onSubmit={handleSubmit}
        isLoading={isLoading}
        externalError={error}
        validateEmail
        validatePassword
        showLegal
        purpose="signup"
      />
      <ValuePropsImg src={imageUrl("vivial-account-value-props.png")} />
      <LoginContainer>
        Already have an account?{" "}
        <Link to={AppRoute.login} preserveQueryParams>
          Login
        </Link>
      </LoginContainer>
    </PageContainer>
  );
};

export default SignUpPage;
