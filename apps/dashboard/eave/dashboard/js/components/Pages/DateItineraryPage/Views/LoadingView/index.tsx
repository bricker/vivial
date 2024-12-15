import { styled } from "@mui/material";
import BaseSkeleton from "@mui/material/Skeleton";
import React from "react";

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
  return (
    <>
      <LogisticsSkeleton variant="rectangular" width="100%" height={181} />
      <RestaurantSkeleton variant="rectangular" width="100%" height={139} />
      <ActivitySkeleton variant="rectangular" width="100%" height={139} />
      <ActivitySkeleton variant="rectangular" width="100%" height={319} />
    </>
  );
};

export default LoadingView;
