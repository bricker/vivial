import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { styled } from "@mui/material";
import Button from "@mui/material/Button";

import EmailIcon from "../../Icons/EmailIcon/";
import InstagramIcon from "../../Icons/InstagramIcon";
import TikTokIcon from "../../Icons/TikTokIcon";

import { AppRoute } from "$eave-dashboard/js/routes";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";

const Footer = styled("footer")(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  flex: "0 0 140px",
  zIndex: 0,
}));

const FootNote = styled("p")(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  margin: 0,
  textAlign: "center",
}));

const LegalContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "center",
  marginTop: 8,
}));

const LegalButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  textDecoration: "underline",
  minWidth: "auto",
  fontSize: rem(12),
  lineHeight: rem(15),
  padding: "0 12px",
  "&:focus": {
    textDecoration: "underline",
  },
}));

const SocialContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "center",
  marginBottom: 8,
}));

const SocialLink = styled("a")(({ theme }) => ({
  display: "inline-flex",
  justifyContent: "center",
  alignItems: "center",
  height: 32,
  width: 32,
  margin: "0 4px",
  border: `1px solid ${theme.palette.text.primary}`,
  borderRadius: "50%",
}));

const GlobalFooter = () => {
  const year = new Date().getFullYear();
  const navigate = useNavigate();
  const handleTermsClick = useCallback(() => {
    navigate(AppRoute.terms);
  }, []);
  const handlePrivacyClick = useCallback(() => {
    navigate(AppRoute.privacy);
  }, []);

  return (
    <Footer>
      <SocialContainer>
        <SocialLink href="mailto:info@vivialapp.com" target="_blank">
          <EmailIcon />
        </SocialLink>
        <SocialLink href="https://www.tiktok.com/@vivial.app" target="_blank">
          <TikTokIcon />
        </SocialLink>
        <SocialLink href="https://www.instagram.com/vivial.app" target="_blank">
          <InstagramIcon />
        </SocialLink>
      </SocialContainer>
      <FootNote>&copy; {year} Vivial by Eave Technologies, Inc.</FootNote>
      <FootNote>All rights reserved.</FootNote>
      <LegalContainer>
        <LegalButton onClick={handleTermsClick}>Terms</LegalButton>
        <LegalButton onClick={handlePrivacyClick}>Privacy</LegalButton>
      </LegalContainer>
    </Footer>
  );
};

export default GlobalFooter;
