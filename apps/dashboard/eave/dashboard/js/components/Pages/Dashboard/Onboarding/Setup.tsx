import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { CircularProgress } from "@mui/material";
import React, { useContext, useEffect } from "react";
import { makeStyles } from "tss-react/mui";
import { SetupStep } from "./SetupStep";

const useStyles = makeStyles()((theme) => ({
  stepsContainer: {
    // Display
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "center",
    // Spacing
    gap: theme.spacing(4),
    padding: theme.spacing(12),
  },
  container: {
    display: "flex",
    flexDirection: "column",
    width: "100vw",
    height: "100vh",
  },
  headerContainer: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    margin: 16,
  },
  error: {
    color: theme.palette.error.main,
    padding: "0px 30px",
    textAlign: "center",
    fontSize: "26px",
  },
  loader: {
    display: "flex",
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 32,
  },
}));

const Setup = () => {
  const { classes } = useStyles();

  const { team, getClientCredentials } = useTeam();
  const { clientCredentialsNetworkStateCtx } = useContext(AppContext);
  const [networkState] = clientCredentialsNetworkStateCtx!;

  useEffect(getClientCredentials, []);

  return (
    <div className={classes.container}>
      <div className={classes.headerContainer}>
        <h1>Getting Started</h1>
        <button>copy something TODO</button>
      </div>
      {(() => {
        if (team?.clientCredentials) {
          const stepOne = `<script src="https://cdn.eave.fyi/collector.js?id=${team.clientCredentials.id}"></script>`;
          const stepTwo = `pip install eave-collectors`;
          const stepThree = `EAVE_CREDENTIALS="${team.clientCredentials.secret}"`;
          const stepFour = `from eave.collectors import start_eave_collectors
  start_eave_collectors()`;
          return (
            <div className={classes.stepsContainer}>
              <SetupStep
                header={"Add the Eave browser snippet to the header of your website"}
                code={stepOne}
                codeHeader={"index.html"}
              />
              <SetupStep
                header={"Install the Eave Collectors Package"}
                subHeader={
                  "If necessary, also add the eave-collectors package to your project dependencies ( requirements.txt, pyproject.toml, etc.)"
                }
                code={stepTwo}
                codeHeader={"Terminal"}
              />
              <SetupStep header={"Set the following environment variable"} code={stepThree} codeHeader={".env"} />
              <SetupStep
                header={"Start the Eave Collectors anywhere in your application"}
                code={stepFour}
                codeHeader={"main.py"}
              />
            </div>
          );
        } else if (networkState?.credentialsAreLoading) {
          return (
            <div className={classes.loader}>
              <CircularProgress color="secondary" />
            </div>
          );
        } else {
          // erroring, or request completed but no credentials were found
          return <div className={classes.error}>ERROR: Failed to fetch your Eave credentials. Please try again later.</div>;
        }
      })()}
    </div>
  );
};

export default Setup;
