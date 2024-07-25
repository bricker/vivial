import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import React, { useContext, useEffect } from "react";
import { makeStyles } from "tss-react/mui";
import { SetupStep } from "./SetupStep";

const useStyles = makeStyles()((theme) => ({
  container: {
    // Display
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "center",
    // Spacing
    gap: theme.spacing(4),
    padding: theme.spacing(12),
  },

  flex: {
    flex: 1,
  },
}));

const Setup = () => {
  const { classes } = useStyles();

  const { team, getClientCredentials } = useTeam();
  const { clientCredentialsNetworkStateCtx } = useContext(AppContext);
  const [networkState] = clientCredentialsNetworkStateCtx!;

  useEffect(getClientCredentials, []);

  if (networkState?.credentialsAreLoading) {
    // return loading ui
    return <p>loading</p>
  } else if (networkState?.credentialsAreErroring) {
    // return error uI
    return <p>error</p>
  } else {
    const stepOne = `<script src="https://cdn.eave.fyi/collector.js?id=${team?.clientCredentials?.id}"></script>`;
    const stepTwo = `pip install eave-collectors`;
    const stepThree = `EAVE_CREDENTIALS="${team?.clientCredentials?.secret}"`;
    const stepFour = `from eave.collectors import start_eave_collectors
  start_eave_collectors()`;
    return (
      <div className={classes.container}>
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
          codeHeader={"index.html"}
        />
      </div>
    );
  }
};

export default Setup;
