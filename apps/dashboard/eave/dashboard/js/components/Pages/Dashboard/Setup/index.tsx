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
    flexGrow: 1,
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
 * (since Dashboard needs that state to determine if this tab should even be
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
    } else if (team?.dashboardAccess === false) {
      // prevent sneaky direct URL nav to dash
      navigate("/onboarding");
    }
  }, [team]);

  const [copyQuestions, setCopyQuestions] = useState(false);

  // return <div> Hello Eave! </div>;

  return (
    <div className={classes.container}>
      {(() => {
        if (team?.clientCredentials) {
          const steps = [
            {
              header: "Add the Eave browser snippet to the header of your website",
              subheader: undefined,
              codeSnippet: `<script>window.EAVE_CLIENT_ID = "${team.clientCredentials.id}";</script>
<script async src="https://cdn.eave.fyi/collector.js"></script>`,
              codeLanguage: "javascript",
              codeFileName: "index.html",
            },
            {
              header: "Install the Eave Collectors Package",
              subheader:
                "If necessary, also add the eave-collectors package to your project dependencies (requirements.txt, pyproject.toml, etc.)",
              codeSnippet: "pip install eave-collectors",
              codeLanguage: "shell",
              codeFileName: "Terminal",
            },
            {
              header: "Set the following environment variable",
              subheader: undefined,
              codeSnippet: `EAVE_CREDENTIALS="${team.clientCredentials.combined}"`,
              codeLanguage: "shellSession",
              codeFileName: ".env",
            },
            {
              header: "Start the Eave Collectors anywhere in your application",
              subheader: undefined,
              codeSnippet: `from eave.collectors import start_eave_collectors
start_eave_collectors()`,
              codeLanguage: "python",
              codeFileName: "main.py",
            },
          ];

          const copyInstructions = steps.map((step, i) => `Step ${i}: ${step.codeSnippet}`).join("\n\n");
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
                      .writeText(copyInstructions)
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
                {steps.map((step, i) => (
                  <SetupStep
                    key={step.header}
                    header={step.header}
                    subHeader={step.subheader}
                    code={step.codeSnippet}
                    codeHeader={step.codeFileName}
                    codeLanguage={step.codeLanguage}
                    stepNumber={i + 1}
                  />
                ))}
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
            <div className={classNames(ui.loadingContainer, text.header, text.error)}>
              ERROR: Failed to fetch your Eave credentials. Please try again later.
            </div>
          );
        }
      })()}
    </div>
  );
};

export default Setup;
