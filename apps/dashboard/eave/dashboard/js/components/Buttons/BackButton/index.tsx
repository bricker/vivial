import { styled } from "@mui/material";
import Button from "@mui/material/Button";
import React from "react";
import { useNavigate } from "react-router-dom";
import BackIcon from "../../Icons/BackIcon";

const CustomButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontFamily: theme.typography.fontFamily,
  fontWeight: 700,
  paddingTop: 12,
  paddingBottom: 12,
  paddingLeft: 0,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
}));

const BackButton = () => {
  const navigate = useNavigate();
  return (
    // mimic browser back nav button behavior
    <CustomButton onClick={() => navigate(-1)}>
      <BackIcon /> Back
    </CustomButton>
  );
};

export default BackButton;
