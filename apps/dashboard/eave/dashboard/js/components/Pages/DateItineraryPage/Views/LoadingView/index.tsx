import { Breakpoint, isDesktop, useBreakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import BaseSkeleton from "@mui/material/Skeleton";
import React from "react";

const ViewContainer = styled("div")(({ theme }) => ({
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    padding: "112px 104px",
    textAlign: "center",
  },
}));

const LogisticsSkeleton = styled(BaseSkeleton)(() => ({
  marginBottom: 47,
}));

const RestaurantSkeleton = styled(BaseSkeleton)(() => ({
  padding: "0px 16px",
  borderRadius: 15,
  marginBottom: 103,
}));

const ActivitySkeleton = styled(BaseSkeleton)(() => ({
  padding: "0px 16px",
  borderRadius: 15,
  marginBottom: 52,
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
    <>
      <LogisticsSkeleton variant="rectangular" width="100%" height={181} />
      <RestaurantSkeleton variant="rectangular" width="100%" height={139} />
      <ActivitySkeleton variant="rectangular" width="100%" height={139} />
      <BaseSkeleton variant="rectangular" width="100%" height={319} />
    </>
  );
};

export default LoadingView;
