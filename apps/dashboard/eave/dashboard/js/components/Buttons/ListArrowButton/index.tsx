import { Button, ButtonProps, Typography, styled } from "@mui/material";
import React from "react";
import ChevronRightIcon from "../../Icons/ChevronRightIcon";

const CustomButton = styled(Button)(({ theme }) => ({
  borderBottom: `1px solid ${theme.palette.grey[800]}`,
}));

const ContentContainer = styled("div")(({ theme }) => ({
  width: "100%",
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "16px",
  color: theme.palette.text.primary,
}));

const ListArrowButton = (props: ButtonProps) => {
  return (
    <CustomButton onClick={props.onClick}>
      <ContentContainer>
        <Typography variant="button">{props.children}</Typography>
        <ChevronRightIcon />
      </ContentContainer>
    </CustomButton>
  );
};

export default ListArrowButton;
