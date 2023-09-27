import { CircularProgress } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import Page from "../Page/index.jsx";

const makeClasses = makeStyles(() => ({
  loader: {
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

const LoadingPage = () => {
  const classes = makeClasses();
  return (
    <Page>
      <div className={classes.loader}>
        <CircularProgress />
      </div>
    </Page>
  );
};

export default LoadingPage;
