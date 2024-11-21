import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import React, { useCallback } from "react";

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
  const handleSubmit = useCallback(({ email, password }: { email: string; password: string }) => {
    console.debug(email, password);
  }, []);

  return (
    <PageContainer>
      <AuthForm title="Log in" cta="Log in" onSubmit={handleSubmit} showForgotPassword />
      <SignUp>
        Don’t have an account? <Link to="/signup">Sign up</Link>
      </SignUp>
    </PageContainer>
  );
};

export default LogInPage;
