import classNames from "classnames";
import { motion, useAnimationControls } from "framer-motion";
import React, { useEffect, useState } from "react";
import { makeStyles } from "tss-react/mui";
import EaveNoTextIcon from "../Icons/Sidebar/EaveNoTextIcon";
import EaveTextIcon from "../Icons/Sidebar/EaveTextIcon";
import SidebarSection from "./SidebarSection";
import { SidebarData } from "./data";

// These objects determine the animation states of the sidebar.
// Check out: https://www.framer.com/motion/animation/
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

const sectionOne = [SidebarData.setup, SidebarData.insights, SidebarData.glossary];
const sectionTwo = [SidebarData.team, SidebarData.settings];
const logoutSection = [SidebarData.logout];

const useStyles = makeStyles()((theme) => ({
  container: {
    position: "sticky",
    display: "flex",
    justifyContent: "space-between",
    top: 0,
    height: "100vh",
    backgroundColor: "#F6F6F6",
    padding: theme.spacing(2),
    zIndex: 10,
    flexDirection: "column",
    boxSizing: "border-box",
    margin: 0,
  },

  topIcons: {
    display: "flex",
    flexDirection: "column",
    gap: 32,
    width: "100%",
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
      {/* Entire Sidebar Except Logout */}
      <div className={classes.topIcons}>
        {/* Header + Toggle Sidebar Length */}
        <div className={classes.header}>
          {isOpen ? (
            <EaveTextIcon width={"100%"} />
          ) : (
            <button
              className={classNames(classes.button, {
                [classes.buttonGray]: isHovering && !isOpen,
              })}
              onClick={handleToggle}
            >
              <EaveNoTextIcon isHovering={isHovering} />
            </button>
          )}
        </div>
        {/* Section: Getting Started, Dashboard and Glossary */}
        <SidebarSection isOpen={isOpen} sectionName={"MENU"} sectionPages={sectionOne} />

        {/* Section: Team and Settings */}
        <SidebarSection isOpen={isOpen} sectionName={"SETTINGS"} sectionPages={sectionTwo} />
      </div>
      {/* Logout Section  */}
      <SidebarSection isOpen={isOpen} sectionPages={logoutSection} reloadDocument={true} />
      Collapse Button
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
