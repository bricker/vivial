import React from "react";
import { makeStyles } from "tss-react/mui";
import PageLink from "./PageLink";

const useStyles = makeStyles()((theme) => ({
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

interface Page {
  title: string;
  path: string;
  icon: React.ElementType;
}

interface SidebarSectionProps {
  isOpen: boolean;
  sectionPages: Page[];
  sectionName?: string;
  reloadDocument?: boolean;
}

const SidebarSection: React.FC<SidebarSectionProps> = ({ isOpen, sectionPages, sectionName, reloadDocument }) => {
  const { classes } = useStyles();

  return (
    <div className={classes.section}>
      <div>
        <h2 className={`${classes.caption} ${classes.gray} ${!isOpen && classes.hidden}`}>{sectionName}</h2>
      </div>
      <div className={classes.linkContainer}>
        {sectionPages.map((page) => (
          <PageLink
            name={page.title}
            path={page.path}
            isOpen={isOpen}
            Icon={page.icon}
            reloadDocument={reloadDocument}
          />
        ))}
      </div>
    </div>
  );
};

export default SidebarSection;
