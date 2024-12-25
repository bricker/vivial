import { AppRoute } from "$eave-dashboard/js/routes";
import { myWindow } from "$eave-dashboard/js/types/window";
import { styled } from "@mui/material";
import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ListArrowButton from "../../Buttons/ListArrowButton";
import EditableContainer from "./EditableContainer";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const ButtonList = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  padding: "0 24px",
}));

const AccountPage = () => {
  const navigate = useNavigate();

  const handlePrefsClick = useCallback(() => {
    navigate(AppRoute.accountPreferences);
  }, [navigate]);

  const handleBillingClick = useCallback(() => {
    window.location.href = myWindow.app.stripeCustomerPortalUrl;
  }, []);

  const handlePasswordResetClick = useCallback(() => {
    navigate(AppRoute.passwordReset);
  }, [navigate]);

  return (
    <PageContainer>
      <EditableContainer />
      <ButtonList>
        <ListArrowButton onClick={handlePrefsClick}>My preferences</ListArrowButton>
        <ListArrowButton onClick={handleBillingClick}>Payment & billing</ListArrowButton>
        <ListArrowButton onClick={handlePasswordResetClick}>Password reset</ListArrowButton>
      </ButtonList>
    </PageContainer>
  );
};

export default AccountPage;
