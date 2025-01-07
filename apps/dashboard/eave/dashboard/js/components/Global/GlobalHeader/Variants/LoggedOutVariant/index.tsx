import { AppRoute } from "$eave-dashboard/js/routes";
import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
import VivialLogo from "$eave-dashboard/js/components/Logo";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import Header from "../../Shared/Header";

const CustomButton = styled(PrimaryButton)(() => ({
  height: 35,
  fontSize: rem(16),
  lineHeight: rem(18),
  fontWeight: 700,
  padding: "8px 20px",
}));

const LoggedOutVariant = () => {
  const navigate = useNavigate();
  const handleSignUpClick = useCallback(() => {
    navigate({
      pathname: AppRoute.signup,
      search: window.location.search,
    });
  }, []);

  return (
    <Header>
      <VivialLogo />
      <CustomButton onClick={handleSignUpClick}>Sign up</CustomButton>
    </Header>
  );
};

export default LoggedOutVariant;
