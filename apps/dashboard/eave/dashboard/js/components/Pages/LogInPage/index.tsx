import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import React, { useCallback } from "react";

import AuthForm from "../../Forms/AuthForm";
import Link from "../../Links/Link";

const Container = styled("div")(() => ({
  padding: "24px 16px",
}));

const SignUp = styled("p")(() => ({
  margin: "32px 0 0",
  fontSize: rem("18px"),
  lineHeight: rem("18px"),
  textAlign: "center",
}));

const LogInPage = () => {
  const handleSubmit = useCallback((email: string, password: string) => {}, []);

  return (
    <Container>
      <AuthForm title="Log in" cta="Log in" onSubmit={handleSubmit} showForgotPassword />
      <SignUp>
        Don’t have an account? <Link to="/signup">Sign up</Link>
      </SignUp>
    </Container>
  );
};

export default LogInPage;
