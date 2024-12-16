import { MAX_REROLLS, useReroll } from "$eave-dashboard/js/util/reroll";
import React from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import Button, { ButtonProps } from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";

const CustomButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  minWidth: 111.5,
  height: 52,
  fontSize: rem(16),
  backgroundColor: "#4D4D4D", // one-off color
  borderRadius: 50,
}));

interface RerollButtonProps extends ButtonProps {
  onReroll: () => void;
  loading?: boolean;
}

const RerollButton = ({ onReroll, loading, ...props }: RerollButtonProps) => {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const [rerolls, rerolled] = useReroll();
  const navigate = useNavigate();
  const buttonContent = loading ? <CircularProgress color="inherit" size={20} /> : "🎲 Reroll";

  const handleReroll = () => {
    if (isLoggedIn) {
      onReroll();
    } else {
      if (rerolls >= MAX_REROLLS) {
        navigate(AppRoute.signupMultiReroll);
      } else {
        rerolled();
        onReroll();
      }
    }
  };

  return (
    <CustomButton onClick={handleReroll} {...props}>
      {buttonContent}
    </CustomButton>
  );
};

export default RerollButton;
