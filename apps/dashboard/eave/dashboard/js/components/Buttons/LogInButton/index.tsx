import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import Button from "@mui/material/Button";
import React from "react";

const CustomButton = styled(Button)(({ theme }) => ({
  color: theme.palette.grey[500],
  border: `1px solid ${theme.palette.grey[500]}`,
  fontSize: rem(15),
  lineHeight: rem(18),
  fontWeight: 700,
  padding: "8px 20px",
  borderRadius: "50px",
}));

const LogInButton = ({ onClick }: { onClick: () => void }) => {
  return <CustomButton onClick={onClick}>Log in</CustomButton>;
};

export default LogInButton;
