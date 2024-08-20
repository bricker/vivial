import classNames from "classnames";
import { motion, useAnimationControls } from "framer-motion";
import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import DashboardIcon from "../Icons/Sidebar/DashboardIcon";
import EaveNoTextIcon from "../Icons/Sidebar/EaveNoTextIcon";
import GlossaryIcon from "../Icons/Sidebar/GlossaryIcon";
import LogoIcon from "../Icons/Sidebar/LogoIcon";
import LogoutIcon from "../Icons/Sidebar/LogoutIcon";
import SettingsIcon from "../Icons/Sidebar/SettingsIcon";
import SetupIcon from "../Icons/Sidebar/SetupIcon";
import TeamIcon from "../Icons/Sidebar/TeamIcon";
import { SidebarData } from "./data";

const containerVariants = {
  close: {
    width: "5rem",
    transition: {
      type: "spring",
      damping: 15,
      duration: 0.5,
    },
  },
  open: {
    width: "13rem",
    transition: {
      type: "tween",
      damping: 15,
      duration: 0.5,
    },
  },
};

const useStyles = makeStyles()(() => ({
  container: {
    position: "sticky",
    display: "flex",
    justifyContent: "space-between",
    top: 0,
    height: "100vh",
    backgroundColor: "#F6F6F6",
    padding: 16,
    zIndex: 10,
    flexDirection: "column",
    boxSizing: "border-box",
    margin: 0,
  },

  topPart: {
    display: "flex",
    flexDirection: "column",
    gap: 32,
    width: "100%",
    // border: "2px solid",
  },
  header: {
    borderBottom: "1px solid #B2B2B2",
    paddingBottom: 8,
    height: "48px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  section: {
    // border: "2px solid",
    width: "100%",
  },
  buttonTopRight: {
    position: "absolute",
    top: 20, // Set to 16px down from the top
    right: 0, // Set to 16px from the right edge
    display: "none", // Initially hidden
    border: "none",
    borderTopLeftRadius: 4,
    borderBottomLeftRadius: 4,
    cursor: "pointer",
  },
  buttonTopRightVisible: {
    display: "block", // Display when conditions are met
  },
  linkText: {
    textDecoration: "none", // Ensure no underline
  },
  button: {
    display: "flex",
    backgroundColor: "transparent",
    justifyContent: "center",
    alignItems: "center",
    border: "none",
    cursor: "pointer",
  },
  buttonGray: {
    backgroundColor: "#D8D8D8",
    borderRadius: 10,
  },
  caption: {
    fontSize: 14,
  },
  gray: {
    color: "#B2B2B2",
  },
  name: {
    fontSize: 16,
    fontWeight: "bold",
    margin: 0,
    textDecoration: "none",
  },
  link: {
    maxWidth: "100%",

    color: "#7D7D7D",
    borderRadius: "10px",
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    width: "100%",
    paddingTop: 8,
    // border: "2px solid",
    overflow: "hidden",
    paddingBottom: 8,
    "&:hover": {
      backgroundColor: "#EEEEEE",
      color: "black",
      cursor: "pointer",
    },
  },
  active: {
    backgroundColor: "#EEEEEE",
    textDecoration: "none",
  },
  centeredLink: {
    display: "flex",
    justifyContent: "center",
    width: "auto",
  },
  nameContainer: {
    flexGrow: 1,
    overflow: "hidden",
    whiteSpace: "nowrap",
    textOverflow: "ellipsis",
  },
  linkContainer: {
    width: "100%",
    display: "flex",
    // border: "2px solid",
    flexDirection: "column",
    gap: 8,
  },
  hidden: {
    visibility: "hidden", // Hide the text but retain the space
  },
  border: {
    // border: "2px solid",
  },
}));

const SideBarEave = () => {
  const { classes } = useStyles();
  const [isOpen, setIsOpen] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const containerControls = useAnimationControls();

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    if (isOpen) {
      containerControls.start("open");
    } else {
      containerControls.start("close");
    }
  }, [isOpen]);

  return (
    <motion.div
      className={classes.container}
      initial="close"
      variants={containerVariants}
      animate={containerControls}
      onHoverStart={() => setIsHovering(true)}
      onHoverEnd={() => setIsHovering(false)}
    >
      <div className={classes.topPart}>
        <div className={classes.header}>
          {isOpen ? (
            <LogoIcon width={"100%"} />
          ) : (
            <button
              className={classNames(classes.button, {
                [classes.buttonGray]: isHovering && !isOpen,
              })}
              onClick={handleToggle}
            >
              <EaveNoTextIcon isHovering={isHovering} />{" "}
            </button>
          )}
        </div>
        <div className={classes.section}>
          <div className={classes.border}>
            <h2 className={`${classes.caption} ${classes.gray} ${!isOpen && classes.hidden}`}>MENU</h2>
          </div>
          <div className={classes.linkContainer}>
            <PageLink name={SidebarData.setup.title} path={SidebarData.setup.path} isOpen={isOpen} Icon={SetupIcon} />
            <PageLink
              name={SidebarData.insights.title}
              path={SidebarData.insights.path}
              isOpen={isOpen}
              Icon={DashboardIcon}
            />
            <PageLink
              name={SidebarData.glossary.title}
              path={SidebarData.glossary.path}
              isOpen={isOpen}
              Icon={GlossaryIcon}
            />
          </div>
        </div>

        <div className={classes.section}>
          <h2 className={`${classes.caption} ${classes.gray} ${!isOpen && classes.hidden}`}> GENERAL </h2>
          <div className={classes.linkContainer}>
            <PageLink name={SidebarData.team.title} path={SidebarData.team.path} isOpen={isOpen} Icon={TeamIcon} />
            <PageLink
              name={SidebarData.settings.title}
              path={SidebarData.settings.path}
              isOpen={isOpen}
              Icon={SettingsIcon}
            />
          </div>
        </div>
      </div>
      <div className={classes.linkContainer}>
        <PageLink
          name={SidebarData.logout.title}
          path={SidebarData.logout.path}
          isOpen={isOpen}
          Icon={LogoutIcon}
          reloadDocument={true}
        />
      </div>
      <motion.button
        className={classNames(classes.buttonTopRight, {
          [classes.buttonTopRightVisible]: isHovering && isOpen,
        })}
        onClick={handleToggle}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M15 6L9 12L15 18M15 12H15.01"
            stroke="#000000"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </motion.button>
    </motion.div>
  );
};

export default SideBarEave;

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
}

type PageLinkProps = {
  name: string;
  path: string;
  isOpen: boolean;
  Icon: React.FC<LogoIconProps>;
  reloadDocument?: boolean;
};

const PageLink: React.FC<PageLinkProps> = ({ name, path, isOpen, Icon, reloadDocument }) => {
  const { classes } = useStyles();
  return (
    <NavLink
      to={path}
      className={({ isActive }) => (isActive ? classes.active : classes.linkText)}
      reloadDocument={reloadDocument}
    >
      <div className={`${classes.link} ${!isOpen && classes.centeredLink} ${classes.linkText} `}>
        <Icon color="#7D7D7D" width="48px" />
        <div className={classes.nameContainer}>{isOpen && <p className={`${classes.name}`}>{name}</p>}</div>
      </div>
    </NavLink>
  );
};
