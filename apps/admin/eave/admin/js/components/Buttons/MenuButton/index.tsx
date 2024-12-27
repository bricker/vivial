import { styled } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import React from "react";
import CloseIcon from "../../Icons/CloseIcon";
import MenuIcon from "../../Icons/MenuIcon";

const Button = styled(IconButton)(() => ({
  padding: 0,
}));

interface MenuButtonProps {
  onClick: () => void;
  open: boolean;
}

const MenuButton = ({ onClick, open }: MenuButtonProps) => {
  return <Button onClick={onClick}>{open ? <CloseIcon /> : <MenuIcon />}</Button>;
};

export default MenuButton;
