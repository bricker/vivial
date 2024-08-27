import classNames from "classnames";
import { motion, useAnimationControls } from "framer-motion";
import React, { useEffect, useState } from "react";
import { makeStyles } from "tss-react/mui";
import EaveNoTextIcon from "../Icons/Sidebar/EaveNoTextIcon";
import EaveTextIcon from "../Icons/Sidebar/EaveTextIcon";
import LeftArrowIcon from "../Icons/Sidebar/LeftArrowIcon";
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
    backgroundColor: "#F6F6F6", // need to normalize these colors into theme.
    padding: theme.spacing(2),
    zIndex: 10,
    flexDirection: "column",
    boxSizing: "border-box",
    margin: 0,
  },

  upperSections: {
    display: "flex",
    flexDirection: "column",
    gap: 32,
    width: "100%",
  },
  header: {
    borderBottom: "1px solid #B2B2B2",
    paddingBottom: 8,
    height: theme.spacing(6),
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  retractButton: {
    position: "absolute",
    top: 20,
    right: 0,
    display: "none", // Initially hidden
    border: "none",
    borderTopLeftRadius: 4,
    borderBottomLeftRadius: 4,
    cursor: "pointer",
  },
  retractButtonVisible: {
    display: "block",
  },
  expandButton: {
    display: "flex",
    backgroundColor: "transparent",
    justifyContent: "center",
    alignItems: "center",
    border: "none",
    cursor: "pointer",
  },
  expandButtonVisible: {
    backgroundColor: "#D8D8D8",
    borderRadius: 10,
  },
}));

const Sidebar = () => {
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
      <div className={classes.upperSections}>
        {/* Header + Toggle Sidebar Length */}
        <div className={classes.header}>
          {isOpen ? (
            <EaveTextIcon width={"100%"} />
          ) : (
            <button
              className={classNames(classes.expandButton, {
                [classes.expandButtonVisible]: isHovering && !isOpen,
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
      {/* Collapse Button */}
      <motion.button
        className={classNames(classes.retractButton, {
          [classes.retractButtonVisible]: isHovering && isOpen,
        })}
        onClick={handleToggle}
      >
        <LeftArrowIcon />
      </motion.button>
    </motion.div>
  );
};

export default Sidebar;
