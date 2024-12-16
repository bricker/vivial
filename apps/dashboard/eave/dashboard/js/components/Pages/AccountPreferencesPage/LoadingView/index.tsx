import BackButton from "$eave-dashboard/js/components/Buttons/BackButton";
import { styled } from "@mui/material";
import BaseSkeleton from "@mui/material/Skeleton";
import React from "react";

const ViewContainer = styled("div")(() => ({
  padding: "12px 16px 24px",
  maxWidth: 600,
  margin: "0 auto",
}));

const Skeleton = styled(BaseSkeleton)(() => ({
  marginTop: 16,
  borderRadius: "14.984px",
  "&:first-of-type": {
    marginTop: 12,
  },
}));

const LoadingView = () => {
  return (
    <ViewContainer>
      <BackButton />
      <Skeleton variant="rectangular" width="100%" height={135} />
      <Skeleton variant="rectangular" width="100%" height={594} />
      <Skeleton variant="rectangular" width="100%" height={594} />
    </ViewContainer>
  );
};

export default LoadingView;
