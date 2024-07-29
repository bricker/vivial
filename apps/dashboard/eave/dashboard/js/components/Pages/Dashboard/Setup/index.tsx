import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { buttonStyles, textStyles, uiStyles } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import { motion } from "framer-motion";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import { SetupStep } from "./SetupStep";
import { isSetupComplete } from "./util";

const useStyles = makeStyles()((theme) => ({
  container: {
    display: "flex",
    flexDirection: "column",
    overflow: "auto",
  },
  stepsContainer: {
    // Display
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    alignItems: "center",
    // Spacing
    gap: theme.spacing(6),
    padding: theme.spacing(12),
  },
  headerContainer: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: theme.spacing(2),
    paddingLeft: theme.spacing(12),
    paddingRight: theme.spacing(12),
  },
}));

/**
 * Depends on Dashboard parent component to call `getClientCredentials` for it
 * (since Dashboard needs that  state to determine if this tab should even be
 * available, and since calling the req again here causes a render loop.)
 * @returns
 */
const Setup = () => {
  const { classes } = useStyles();
  const { classes: ui } = uiStyles();
  const { classes: text } = textStyles();
  const { classes: button } = buttonStyles();

  const navigate = useNavigate();
  const { team } = useTeam();
  const { clientCredentialsNetworkStateCtx } = useContext(AppContext);
  const [networkState] = clientCredentialsNetworkStateCtx!;

  useEffect(() => {
    if (isSetupComplete(team)) {
      navigate("/insights");
    }
  }, [team]);
  const [copyQuestions, setCopyQuestions] = useState(false);

  // useEffect(getClientCredentials, []);

  return (
    <div className={classes.container}>
      {(() => {
        if (team?.clientCredentials && team?.eaveCombinedCredentials) {
          const stepOne = `<script>window.EAVE_CLIENT_ID = "${team.clientCredentials.id}";</script>
<script async src="https://cdn.eave.fyi/collector.js"></script>`;
          const stepTwo = "pip install eave-collectors";
          const stepThree = `EAVE_CREDENTIALS="${team.eaveCombinedCredentials}"`;
          const stepFour = `from eave.collectors import start_eave_collectors
start_eave_collectors()`;
          const copyString = `${stepOne}`;
          return (
            <div>
              <div className={classes.headerContainer}>
                <h1>Getting Started</h1>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.9 }}
                  className={button.default}
                  onClick={() => {
                    navigator.clipboard
                      .writeText(copyString)
                      .then(() => {
                        setCopyQuestions(true);
                        setTimeout(() => {
                          setCopyQuestions(false);
                        }, 1500);
                      })
                      .catch(() => {
                        setCopyQuestions(false);
                      });
                  }}
                >
                  {copyQuestions ? "Copied!" : "Copy Questions"}
                </motion.button>
              </div>
              <div className={classes.stepsContainer}>
                <SetupStep
                  header="Add the Eave browser snippet to the header of your website"
                  code={stepOne}
                  codeHeader="index.html"
                  stepNumber={1}
                />
                <SetupStep
                  header="Install the Eave Collectors Package"
                  subHeader="If necessary, also add the eave-collectors package to your project dependencies (requirements.txt, pyproject.toml, etc.)"
                  code={stepTwo}
                  codeHeader="Terminal"
                  stepNumber={2}
                />
                <SetupStep
                  header="Set the following environment variable"
                  code={stepThree}
                  codeHeader=".env"
                  stepNumber={3}
                />
                <SetupStep
                  header="Start the Eave Collectors anywhere in your application"
                  code={stepFour}
                  stepNumber={4}
                  codeHeader="main.py"
                />
              </div>
            </div>
          );
        } else if (networkState?.credentialsAreLoading) {
          return (
            <div className={ui.loadingContainer}>
              <CircularProgress color="secondary" />
            </div>
          );
        } else {
          // erroring, or request completed but no credentials were found
          return (
            <div className={classNames(ui.loadingContainer, text.header)}>
              ERROR: Failed to fetch your Eave credentials. Please try again later.
            </div>
          );
        }
      })()}
    </div>
  );
};

export default Setup;
