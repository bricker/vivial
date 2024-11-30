import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled, Typography } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import React from "react";
import BackIcon from "../Icons/BackIcon";

const ModalContainer = styled("div")(() => ({
  background: `rgba(0, 0, 0, 0.75)`,
  height: "100vh",
  width: "100vh",
  position: "fixed",
  overflowX: "hidden",
  top: 0,
  left: 0,
  zIndex: 1,
}));

const ModalContent = styled("div")(({ theme }) => ({
  background: `linear-gradient(180deg, ${theme.palette.grey[900]} 0%, #2A2929 100%)`,
  borderRadius: `17.276px 17.276px 0px 0px`,
  position: "fixed",
  width: "100%",
  padding: "24px 40px 56px",
  bottom: 0,
}));

const TitleContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  margin: "0 0 24px -16px",
}));

const Title = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
  lineHeight: rem("32px"),
  marginLeft: 16,
}));

const CloseButton = styled(IconButton)(() => ({
  padding: 0,
}));

interface ModalProps {
  children: React.ReactNode;
  title: string;
  open: boolean;
  onClose: () => void;
}

const Modal = ({ title, open, onClose, children }: ModalProps) => {
  if (open) {
    return (
      <ModalContainer>
        <ModalContent>
          <TitleContainer>
            <CloseButton onClick={onClose}>
              <BackIcon large />
            </CloseButton>
            <Title variant="h3">{title}</Title>
          </TitleContainer>
          {children}
        </ModalContent>
      </ModalContainer>
    );
  }
  return null;
};

export default Modal;
