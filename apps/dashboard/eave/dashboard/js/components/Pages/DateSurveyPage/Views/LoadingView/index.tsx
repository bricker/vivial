import React from "react";
import { styled } from "@mui/material";
import BaseSkeleton from "@mui/material/Skeleton";

const ViewContainer = styled("div")(() => ({
  padding: "24px 16px",
}));

const Skeleton = styled(BaseSkeleton)(() => ({
  marginBottom: 16,
  borderRadius: "14.984px",
  "&:last-of-type": {
    marginBottom: 0,
  },
}));

const LoadingView = () => {
  return (
    <ViewContainer>
      <Skeleton variant="rectangular" width="100%" height={218} />
      <Skeleton variant="rectangular" width="100%" height={332} />
    </ViewContainer>
  );
};

export default LoadingView;
