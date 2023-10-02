import React, { useEffect } from "react";
import { CircularProgress } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { Typography } from "@material-ui/core";
import useTeam from "../../hooks/useTeam";

const makeClasses = makeStyles((theme) => ({
  container: {
    padding: "0 25px",
    marginBottom: 80,
    [theme.breakpoints.up("md")]: {
      padding: "0 128px",
    },
  },
  title: {
    color: theme.palette.tertiary.main,
    fontSize: 32,
    fontWeight: 400,
    marginBottom: 22,
    [theme.breakpoints.up("md")]: {
      fontSize: 36,
      marginBottom: 28,
    },
  },
  error: {
    color: theme.palette.error.main,
  },
  loader: {
    color: theme.palette.tertiary.main,
    textAlign: "center",
  }
}));

function renderContent(classes, team) {
  const { apiDocsErroring, apiDocs } = team;
  if (apiDocsErroring) {
    return (
      <p className={classes.error}>
        ERROR: Unable to fetch API documentation.
      </p>
    )
  }
  if (apiDocs.length === 0) {
    return (
      <div className={classes.loader}>
        <CircularProgress color="inherit" />
      </div>
    );
  }







  return (
    <div>
      API DOC ROWS
    </div>
  );








}

const APIDocumentation = () => {
  const { team, getTeamAPIDocs } = useTeam();
  const classes = makeClasses();

  useEffect(() => {
    getTeamAPIDocs();
    const interval = setInterval(getTeamAPIDocs, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className={classes.container}>
      <Typography className={classes.title} variant="h2">
        API Documentation
      </Typography>
      {renderContent(classes, team)}
    </section>
  );
};

export default APIDocumentation;
