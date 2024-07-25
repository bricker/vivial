import React from "react";
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
  const stepOne = `<script src="https://cdn.eave.fyi/collector.js?id=161357f1aa744408849067af2cffa7fc"></script>`;
  const stepTwo = `pip install eave-collectors`;
  //TODO: Fetch credentials from Database
  const stepThree = `EAVE_CREDENTIALS="161357f1aa744408849067af2cffa7fc:66ab93f72afd45ae94d0c9c2efc76789"`;
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
};

export default Setup;
