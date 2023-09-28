import { makeStyles } from "@material-ui/styles";
import React from "react";

import AuthModal from "../../AuthModal/index.jsx";
import Footer from "../../Footer/index.jsx";
import Header from "../../Header/index.jsx";
import horizontalBgImage from "../../../../static/images/hero-background-horizontal-4x.png";
import verticalBgImage from "../../../../static/images/hero-background-vertical-3x.png";

const makeClasses = makeStyles((theme) => ({
  heroBackgroundImage: {
    
  },
  container: {
    backgroundColor: theme.palette.background.main,
    fontFamily: theme.typography.fontFamily,
    position: "relative",
    minHeight: "100vh",
    backgroundImage: `url(${horizontalBgImage})`,
    backgroundRepeat: "no-repeat",
    backgroundSize: 'contain',
    [theme.breakpoints.down("sm")]: {
      backgroundImage: `url(${verticalBgImage})`,
    }
    // TODO: max width
  },
  sections: {
    minHeight: `calc(100vh - ${theme.header.height}px - ${theme.header.marginBottom}px - ${theme.footer.height}px)`,
    [theme.breakpoints.up("md")]: {
      minHeight: `calc(100vh - ${theme.header.md.height}px - ${theme.header.md.marginBottom}px - ${theme.footer.height}px)`,
    },
  },
}));

const Page = ({ children, simpleHeader }) => {
  const classes = makeClasses();
  return (
    <div className={classes.container}>
      <Header simpleHeader={simpleHeader} />
      <div className={classes.sections}>{children}</div>
      <Footer />
      <AuthModal />
    </div>
  );
};

export default Page;
