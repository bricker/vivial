import { rem } from "$eave-dashboard/js/util/rem";
import { styled } from "@mui/material";
import Button from "@mui/material/Button";
import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

const CustomButton = styled(Button)(({ theme }) => ({
  color: theme.palette.grey[500],
  border: `1px solid ${theme.palette.grey[500]}`,
  fontSize: rem("15px"),
  lineHeight: rem("18px"),
  fontWeight: 700,
  padding: "8px 20px",
  borderRadius: "50px",
}));

const LogInButton = () => {
  const navigate = useNavigate();
  const handleClick = useCallback(() => {
    navigate("/login");
  }, []);

  return <CustomButton onClick={handleClick}>Log in</CustomButton>;
};

export default LogInButton;
