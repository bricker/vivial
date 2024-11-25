import { Button, ButtonProps, Typography, styled } from "@mui/material";
import React from "react";
import ChevronRightIcon from "../../Icons/ChevronRightIcon";

const CustomButton = styled(Button)(({ theme }) => ({
  borderBottom: `1px solid ${theme.palette.grey[800]}`,
}));

const ContentContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  padding: "16px",
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
