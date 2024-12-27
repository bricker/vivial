import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled, type Theme } from "@mui/material";
import Button, { ButtonProps } from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import React from "react";

interface LoadingButtonProps extends ButtonProps {
  loading: boolean;
}

const CustomLoadingButton = styled(Button)(({ theme }: { theme: Theme }) => ({
  color: theme.palette.common.black,
  backgroundColor: theme.palette.primary.main,
  height: rem(52),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
}));

const LoadingButton = ({ children, loading, ...props }: LoadingButtonProps) => {
  const buttonContent = loading ? <CircularProgress color="inherit" size={20} /> : children;
  return (
    <CustomLoadingButton variant="contained" {...props}>
      {buttonContent}
    </CustomLoadingButton>
  );
};

export default LoadingButton;
