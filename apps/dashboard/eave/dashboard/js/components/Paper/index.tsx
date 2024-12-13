import { styled } from "@mui/material";
import React from "react";

const PaperContainer = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: "14.984px",
  background: `linear-gradient(180deg, ${theme.palette.background.paper} 75.85%, rgba(85, 88, 14, 0.10) 190.15%)`,
  boxShadow: `0px 4px 4px 0px rgba(0, 0, 0, 0.25)`,
  padding: "24px 40px",
}));

const Paper = (props: React.HTMLAttributes<HTMLDivElement>) => {
  return <PaperContainer {...props} />;
};

export default Paper;
