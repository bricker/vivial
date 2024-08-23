import DashboardIcon from "../Icons/Sidebar/DashboardIcon";
import GlossaryIcon from "../Icons/Sidebar/GlossaryIcon";
import LogoutIcon from "../Icons/Sidebar/LogoutIcon";
import SettingsIcon from "../Icons/Sidebar/SettingsIcon";
import SetupIcon from "../Icons/Sidebar/SetupIcon";
import TeamIcon from "../Icons/Sidebar/TeamIcon";

export const SidebarData = {
  setup: {
    title: "Setup",
    path: "/setup",
    icon: SetupIcon,
  },
  settings: {
    title: "Settings",
    path: "/settings",
    icon: SettingsIcon,
  },
  glossary: {
    title: "Glossary",
    path: "/glossary",
    icon: GlossaryIcon,
  },
  insights: {
    title: "Insights",
    path: "/insights",
    icon: DashboardIcon,
  },
  team: {
    title: "Team",
    path: "/team",
    icon: TeamIcon,
  },
  logout: {
    title: "Logout",
    path: "/logout",
    icon: LogoutIcon,
  },
};
