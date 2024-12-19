import { Breakpoint, isDesktop, useBreakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import BaseSkeleton from "@mui/material/Skeleton";
import React from "react";

const ViewContainer = styled("div")(({ theme }) => ({
  padding: "24px 16px",
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    padding: "112px 104px",
    textAlign: "center",
  },
}));

const Skeleton = styled(BaseSkeleton)(() => ({
  marginBottom: 16,
  borderRadius: "14.984px",
  "&:last-of-type": {
    marginBottom: 0,
  },
}));

const LoadingView = () => {
  const breakpoint = useBreakpoint();
  if (isDesktop(breakpoint)) {
    return (
      <ViewContainer>
        <CircularProgress />
      </ViewContainer>
    );
  }
  return (
    <ViewContainer>
      <Skeleton variant="rectangular" width="100%" height={218} />
      <Skeleton variant="rectangular" width="100%" height={332} />
    </ViewContainer>
  );
};

export default LoadingView;
