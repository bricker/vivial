import React from "react";

import { makeStyles } from "tss-react/mui";
import Header from "../../Header";

const makeClasses = makeStyles()((theme) => ({
  container: {
    backgroundColor: theme.palette.background.main,
    fontFamily: theme.typography.fontFamily,
    position: "relative",
    minHeight: "100vh",
    zIndex: 1, // this keeps the hero bg image behind the nav bar
  },
  sections: {
    minHeight: `calc(100vh - ${theme.header.height}px - ${theme.header.marginBottom}px - ${theme.footer.height}px)`,
    [theme.breakpoints.up("md")]: {
      minHeight: `calc(100vh - ${theme.header.md.height}px - ${theme.header.md.marginBottom}px - ${theme.footer.height}px)`,
    },
  },
}));

const Page = ({ children }: { children: React.ReactNode }) => {
  const { classes } = makeClasses();
  return (
    <div className={classes.container}>
      <Header />
      <div className={classes.sections}>{children}</div>
    </div>
  );
};

export default Page;
