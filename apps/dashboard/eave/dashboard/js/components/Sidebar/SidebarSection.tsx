import React from "react";
import { makeStyles } from "tss-react/mui";
import PageLink from "./PageLink";

const useStyles = makeStyles()((theme) => ({
  sectionText: {
    fontSize: 14,
    color: "#B2B2B2",
  },
  linkContainer: {
    width: "100%",
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(1),
  },
  hideSectionName: {
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
    <div>
      <div>
        <h2 className={`${classes.sectionText} ${!isOpen && classes.hideSectionName}`}>{sectionName}</h2>
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
