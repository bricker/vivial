import React from "react";
import { NavLink } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  linkText: {
    textDecoration: "none", // Ensure no underline
  },
  name: {
    fontSize: 14,
    fontWeight: "bold",
    margin: 0,
    textDecoration: "none",
  },
  link: {
    maxWidth: "100%",
    color: "#7D7D7D",
    borderRadius: "8px",
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
    width: "100%",
    paddingTop: 8,
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
    borderRadius: 8,
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
}));

type PageLinkProps = {
  name: string;
  path: string;
  isOpen: boolean;
  Icon: React.ElementType;
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

export default PageLink;
