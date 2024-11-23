import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import { ButtonProps } from "@mui/material/Button";
import BaseLoadingButton from '@mui/lab/LoadingButton';
import CircularProgress from "@mui/material/CircularProgress";
import React from "react";

interface LoadingButtonProps extends ButtonProps {
  loading: boolean;
}

const CustomLoadingButton = styled(BaseLoadingButton)(({ theme }) => ({
  color: theme.palette.common.black,
  backgroundColor: theme.palette.primary.main,
  height: rem("52px"),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
  "&.MuiLoadingButton-loading": {
    color: theme.palette.text.disabled,
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
