import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import BaseLoadingButton from "@mui/lab/LoadingButton";
import { styled, type Theme } from "@mui/material";
import { ButtonProps } from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import React from "react";

interface LoadingButtonProps extends ButtonProps {
  loading: boolean;
}

const CustomLoadingButton = styled(BaseLoadingButton)(({ theme }: { theme: Theme }) => ({
  color: theme.palette.common.black,
  backgroundColor: theme.palette.primary.main,
  height: rem("52px"),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
  "&.MuiLoadingButton-loading": {
    color: theme.palette.primary.main,
    backgroundColor: theme.palette.primary.main,
  },
  ".MuiLoadingButton-loadingIndicator": {
    color: theme.palette.common.black,
  },
}));

const LoadingButton = (props: LoadingButtonProps) => {
  return (
    <CustomLoadingButton
      loadingIndicator={<CircularProgress color="inherit" size={20} />}
      variant="contained"
      {...props}
    />
  );
};

export default LoadingButton;
