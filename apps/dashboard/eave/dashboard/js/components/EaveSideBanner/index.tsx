import EaveBlueIcon from "$eave-dashboard/js/components/Icons/EaveBlueIcon";
import { textStyles } from "$eave-dashboard/js/theme";
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
  textContainer: {
    margin: theme.spacing(4),
    border: "2px solid white",
  },
  logo: {
    position: "absolute",
    bottom: -40,
    right: -20,
    width: 300,
    height: "auto",
  },
  rounded: {
    borderRadius: 20,
    margin: 16,
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
  const { classes: text } = textStyles();

  const bannerClasses = classNames(classes.sidebar, { [classes.rounded]: style === BannerStyle.ROUNDED });

  return (
    <div className={bannerClasses}>
      <div className={classes.textContainer}>
        <h1 className={`${text.headerIII} ${text.bold}`}>{title}</h1>
        <h3 className={`${text.subHeader} ${text.bold}`}>{subtext}</h3>
      </div>
      <div className={classes.logo}>
        <EaveBlueIcon />
      </div>
    </div>
  );
}
