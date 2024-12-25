import { styled } from "@mui/material";
import React from "react";

interface CircleProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  color: string;
}

const CustomCircle = styled("div", {
  shouldForwardProp: (prop: string) => prop !== "color",
})<CircleProps>(({ color }) => ({
  backgroundColor: color,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  width: 39,
  height: 39,
  borderRadius: "50%",
  filter: "drop-shadow(0px 4px 4px rgba(0, 0, 0, 0.25))",
}));

const Circle = (props: CircleProps) => {
  return <CustomCircle {...props} />;
};

export default Circle;
