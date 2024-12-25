import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled, Typography } from "@mui/material";

import IconButton from "@mui/material/IconButton";
import React, { useEffect } from "react";
import BackIcon from "../Icons/BackIcon";

const ModalContainer = styled("div")(() => ({
  background: `rgba(0, 0, 0, 0.75)`,
  height: "100vh",
  width: "100%",
  position: "fixed",
  overflowX: "hidden",
  top: 0,
  left: 0,
  zIndex: 10,
}));

const ModalContent = styled("div")(({ theme }) => ({
  background: `linear-gradient(180deg, ${theme.palette.grey[900]} 0%, #2A2929 100%)`,
  borderRadius: `17.276px 17.276px 0px 0px`,
  position: "fixed",
  width: "100%",
  maxHeight: "100vh",
  overflow: "auto",
  bottom: 0,
  paddingBottom: "56px",
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    borderRadius: "17.276px",
    width: 500,
    bottom: "auto",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    padding: "12px 0px 40px",
  },
}));

const TitleContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  padding: "24px",
}));

const Title = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  lineHeight: rem(32),
  marginLeft: 16,
}));

const TitleBadgeContainer = styled("div")(() => ({
  width: "100%",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
}));

const ChildrenContainer = styled("div")<{ padChildren?: boolean }>(({ padChildren }) => ({
  padding: padChildren ? "0px 40px" : "0px",
}));

const CloseButton = styled(IconButton)(() => ({
  padding: 0,
}));

interface ModalProps {
  children: React.ReactNode;
  title: string;
  open: boolean;
  onClose: () => void;
  badge?: React.ReactNode;
  padChildren?: boolean;
}

const Modal = ({ title, open, onClose, children, badge, padChildren = true }: ModalProps) => {
  useEffect(() => {
    if (open) {
      document.body.setAttribute("style", "overflow: hidden;");
    } else {
      document.body.setAttribute("style", "overflow: visible;");
    }
    return () => {
      document.body.setAttribute("style", "overflow: visible;");
    };
  }, [open]);

  if (open) {
    return (
      <ModalContainer>
        <ModalContent>
          <TitleContainer>
            <CloseButton onClick={onClose}>
              <BackIcon large />
            </CloseButton>
            <TitleBadgeContainer>
              <Title variant="h3">{title}</Title>
              {badge}
            </TitleBadgeContainer>
          </TitleContainer>
          <ChildrenContainer padChildren={padChildren}>{children}</ChildrenContainer>
        </ModalContent>
      </ModalContainer>
    );
  }
  return null;
};

export default Modal;
