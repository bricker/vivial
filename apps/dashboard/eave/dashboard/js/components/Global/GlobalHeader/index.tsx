import { type RootState } from "$eave-dashboard/js/store";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { Breakpoint, isDesktop, useBreakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import Button from "@mui/material/Button";

import { AppRoute } from "$eave-dashboard/js/routes";
import LogInButton from "../../Buttons/LogInButton";
import MenuButton from "../../Buttons/MenuButton";
import VivialLogo from "../../Logo";

export enum HeaderHeight {
  Mobile = 60,
  Desktop = 88,
}

const Header = styled("header")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "0 24px",
  backgroundColor: theme.palette.background.paper,
  flex: `0 0 ${HeaderHeight.Mobile}px`,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    flex: `0 0 ${HeaderHeight.Desktop}px`,
  },
}));

const MenuItem = styled(Button)(({ theme }) => ({
  fontFamily: fontFamilies.quicksand,
  color: theme.palette.text.primary,
  fontSize: rem("28px"),
  lineHeight: rem("60px"),
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
    fontSize: rem("15px"),
    lineHeight: rem("18px"),
    "&:hover": {
      backgroundColor: "transparent",
    },
  },
}));

const MobileMenu = styled("div")(({ theme }) => ({
  flex: "1 1 auto",
  background: `linear-gradient(180deg, ${theme.palette.background.paper} 0%, #000 84.33%)`,
  marginTop: "-1px",
  padding: 40,
}));

const DesktopMenu = styled("div")(() => ({
  display: "flex",
}));

const GlobalHeader = () => {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const [mobileMenuIsOpen, setMobileMenuIsOpen] = useState(false);
  const breakpoint = useBreakpoint();
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

  const handleLogin = useCallback(() => {
    navigate(AppRoute.login);
  }, []);

  const handleLogout = useCallback(() => {
    dispatch(loggedOut());
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

  if (isLoggedIn) {
    /**
     * Logged In Header (Desktop)
     */
    if (isDesktop(breakpoint)) {
      return (
        <Header>
          <VivialLogo />
          <DesktopMenu>{menuItems}</DesktopMenu>
        </Header>
      );
    }
    /**
     * Logged In Header (Mobile)
     */
    return (
      <>
        <Header>
          <VivialLogo />
          <MenuButton onClick={toggleMobileMenu} open={mobileMenuIsOpen} />
        </Header>
        {mobileMenuIsOpen && <MobileMenu>{menuItems}</MobileMenu>}
      </>
    );
  }
  /**
   * Logged Out Header
   */
  return (
    <Header>
      <VivialLogo />
      <LogInButton onClick={handleLogin} />
    </Header>
  );
};

export default GlobalHeader;
