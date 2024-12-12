import { AppRoute } from "$eave-dashboard/js/routes";
import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import LogInButton from "$eave-dashboard/js/components/Buttons/LogInButton";
import VivialLogo from "$eave-dashboard/js/components/Logo";
import Header from "../../Shared/Header";

const LoggedOutVariant = () => {
  const navigate = useNavigate();
  const handleLogin = useCallback(() => {
    navigate(AppRoute.login);
  }, []);

  return (
    <Header>
      <VivialLogo />
      <LogInButton onClick={handleLogin} />
    </Header>
  );
};

export default LoggedOutVariant;
