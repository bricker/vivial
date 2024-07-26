import EaveBlueIcon from "$eave-dashboard/js/components/Icons/EaveBlueIcon";
import classNames from "classnames";
import React from "react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  sidebar: {
    flex: 1,
    color: "white",
    display: "flex",
    maxWidth: 700,
    backgroundColor: theme.palette.success.main,
    flexDirection: "column",
    overflow: "hidden",
    position: "relative",
  },
  rounded: {
    borderRadius: 20,
    margin: 16,
  },
  textContainer: {
    paddingLeft: 32,
    paddingRight: 32,
  },
  title: {
    fontSize: 52,
    marginBottom: 16,
    lineHeight: 1.1,
  },
  subtext: {
    width: 256,
    fontSize: 20,
    marginTop: 0,
  },
  logo: {
    position: "absolute",
    bottom: -40,
    right: -20,
    width: 300,
    height: "auto",
  },
}));

export enum BannerStyle {
  FULL,
  ROUNDED,
}

export default function EaveSideBanner({
  style = BannerStyle.ROUNDED,
  title = "Eave Technologies",
  subtext = "You're a few clicks away from automated insights.",
}: {
  style?: BannerStyle;
  title?: string;
  subtext?: string;
}) {
  const { classes } = useStyles();

  const bannerClasses = classNames(classes.sidebar, { [classes.rounded]: style === BannerStyle.ROUNDED });

  return (
    <div className={bannerClasses}>
      <div className={classes.textContainer}>
        <h1 className={classes.title}>{title}</h1>
        <h3 className={classes.subtext}>{subtext}</h3>
      </div>
      <div className={classes.logo}>
        <EaveBlueIcon />
      </div>
    </div>
  );
}
