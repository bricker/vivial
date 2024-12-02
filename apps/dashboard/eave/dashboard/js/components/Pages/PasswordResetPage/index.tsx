import { styled } from "@mui/material";
import React from "react";
import BackButton from "../../Buttons/BackButton";
import PasswordResetForm from "../../Forms/PasswordResetForm";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  margin: "0 auto",
  maxWidth: 450,
}));

const PasswordResetPage = () => {
  return (
    <PageContainer>
      <BackButton />
      <Paper>
        <PasswordResetForm />
      </Paper>
    </PageContainer>
  );
};

export default PasswordResetPage;
