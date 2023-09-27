import { makeStyles } from "@material-ui/styles";
import React from "react";
import Page from "../Page/index.jsx";

const makeClasses = makeStyles((theme) => ({
  error: {
    color: theme.palette.error.main,
    padding: "0px 30px",
    textAlign: "center",
    fontSize: "26px",
  },
}));

const ErrorPage = ({ page }) => {
  const classes = makeClasses();
  return (
    <Page>
      <div className={classes.error}>ERROR: Unable to fetch {page}.</div>
    </Page>
  );
};

export default ErrorPage;
