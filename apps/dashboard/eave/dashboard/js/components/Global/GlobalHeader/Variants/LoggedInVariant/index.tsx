import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import React, { useCallback, useState } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { AppRoute } from "$eave-dashboard/js/routes";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import MenuButton from "$eave-dashboard/js/components/Buttons/MenuButton";
import VivialLogo from "$eave-dashboard/js/components/Logo";
import Button from "@mui/material/Button";
import Header, { HeaderHeight } from "../../Shared/Header";

export enum DeviceType {
  Mobile = "mobile",
  Desktop = "desktop",
}

const DesktopMenu = styled("div")(() => ({
  display: "flex",
}));

const MobileMenu = styled("div")(({ theme }) => ({
  flex: "1 1 auto",
  background: `linear-gradient(180deg, ${theme.palette.background.paper} 0%, #000 84.33%)`,
  marginTop: "-1px",
  padding: 40,
}));

const MenuItem = styled(Button)(({ theme }) => ({
  fontFamily: fontFamilies.quicksand,
  color: theme.palette.text.primary,
  fontSize: rem(28),
  lineHeight: rem(60),
  fontWeight: 400,
  width: "100%",
  justifyContent: "left",
  padding: "0",
  borderRadius: "unset",
  '&[data-active="true"]': {
    color: theme.palette.primary.main,
    fontWeight: 700,
  },
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    height: HeaderHeight.Desktop,
    display: "flex",
    justifyContent: "center",
    width: "auto",
    minWidth: "0",
    margin: "0 20px",
    fontSize: rem(15),
    lineHeight: rem(18),
    "&:hover": {
      backgroundColor: "transparent",
    },
  },
}));

interface LoggedInVariantProps {
  deviceType: DeviceType;
}

const LoggedInVariant = ({ deviceType }: LoggedInVariantProps) => {
  const [mobileMenuIsOpen, setMobileMenuIsOpen] = useState(false);
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const toggleMobileMenu = useCallback(() => {
    const mainContent = document.getElementsByTagName("main")[0];
    if (mainContent) {
      if (mobileMenuIsOpen) {
        mainContent.style.display = "block";
        setMobileMenuIsOpen(false);
      } else {
        mainContent.style.display = "none";
        setMobileMenuIsOpen(true);
      }
    }
  }, [mobileMenuIsOpen]);

  const handleNavigate = useCallback(
    (path: string) => {
      if (mobileMenuIsOpen) {
        toggleMobileMenu();
      }
      navigate(path);
    },
    [mobileMenuIsOpen],
  );

  const handleLogout = useCallback(() => {
    dispatch(loggedOut());
    window.location.assign(AppRoute.logout);
  }, []);

  const menuNavButtons: Array<{ route: string; text: string }> = [
    {
      route: AppRoute.root,
      text: "Pick a date",
    },
    {
      route: AppRoute.plans,
      text: "My plans",
    },
    {
      route: AppRoute.account,
      text: "Account",
    },
    {
      route: AppRoute.help,
      text: "Help",
    },
  ];

  const menuItems = (
    <>
      {menuNavButtons.map((navButton) => (
        <MenuItem
          key={navButton.text}
          data-active={pathname === navButton.route}
          onClick={() => handleNavigate(navButton.route)}
          disableRipple
        >
          {navButton.text}
        </MenuItem>
      ))}
      <MenuItem onClick={handleLogout} disableRipple>
        Log out
      </MenuItem>
    </>
  );

  if (deviceType === DeviceType.Desktop) {
    return (
      <Header>
        <VivialLogo />
        <DesktopMenu>{menuItems}</DesktopMenu>
      </Header>
    );
  }

  return (
    <>
      <Header>
        <VivialLogo />
        <MenuButton onClick={toggleMobileMenu} open={mobileMenuIsOpen} />
      </Header>
      {mobileMenuIsOpen && <MobileMenu>{menuItems}</MobileMenu>}
    </>
  );
};

export default LoggedInVariant;
