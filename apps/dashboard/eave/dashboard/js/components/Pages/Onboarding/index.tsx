import EaveSideBanner from "$eave-dashboard/js/components/EaveSideBanner";
import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { buttonStyles, textStyles, uiStyles } from "$eave-dashboard/js/theme";
import { CreateMyOnboardingSubmissionRequestBody } from "$eave-dashboard/js/types.js";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import { motion } from "framer-motion";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import InputField from "./InputField";
import { copyString, useQuestions } from "./questionOptions";

const useStyles = makeStyles()((theme) => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
  contentContainer: {
    flex: 2,
    overflow: "auto",
    height: "100vh",
    justifyContent: "flex-end",
    padding: theme.spacing(8),
    paddingBottom: theme.spacing(2),
  },
  titleContainer: {
    display: "flex",
    padding: theme.spacing(0),
    flexDirection: "row",
    justifyContent: "space-between",
    height: "fit-content",
    alignItems: "center",
  },
  submitContainer: {
    marginTop: 32,
    display: "flex",
    justifyContent: "flex-end",
  },
  questionsContainer: {
    width: "75%",
    marginTop: theme.spacing(2),
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(4),
  },
  loader: {
    display: "flex",
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 32,
  },
}));

const Onboarding = () => {
  const { classes } = useStyles();
  const { classes: button } = buttonStyles();
  const { classes: text } = textStyles();
  const { classes: ui } = uiStyles();

  const navigate = useNavigate();

  const [copyQuestions, setCopyQuestions] = useState(false);
  const [allFieldsValid, setAllFieldsValid] = useState(false);

  const { team, getOnboardingFormSubmission, createOnboardingFormSubmission } = useTeam();
  const { onboardingFormNetworkStateCtx } = useContext(AppContext);
  const [networkState] = onboardingFormNetworkStateCtx!;

  const questions = useQuestions();

  useEffect(getOnboardingFormSubmission, []);

  useEffect(() => {
    const allValid = questions.every((question) => question.value.length > 0);
    setAllFieldsValid(allValid);
  }, [questions]);

  // check if they have already submitted form
  useEffect(() => {
    if (
      !networkState.formDataIsLoading &&
      !networkState.formDataIsErroring &&
      (team?.dashboardAccess || team?.onboardingSubmission)
    ) {
      // Check if they are qualified to setup/use eave
      if (team?.dashboardAccess) {
        navigate("/setup");
      } else {
        navigate("/waitlist");
      }
    }
  }, [networkState.formDataIsLoading, networkState.formDataIsErroring, team, navigate]);

  const handleNextClick = () => {
    createOnboardingFormSubmission({
      onboarding_submission: questions.reduce((formDataAcc: any, question) => {
        formDataAcc[question.key] = question.value.map((v) => v.value);
        return formDataAcc;
      }, {} as CreateMyOnboardingSubmissionRequestBody),
    });
  };

  if (networkState.formDataIsLoading) {
    return (
      <div className={classes.main}>
        <div className={classes.loader}>
          <CircularProgress color="secondary" />
        </div>
      </div>
    );
  } else if (networkState.formDataIsErroring) {
    // TODO: update this text to something even more generic??
    return (
      <div className={classNames(ui.loadingContainer, text.header, text.error)}>
        ERROR: Failed to fetch your Eave credentials. Please try again later.
      </div>
    );
  } else {
    return (
      <div className={classes.main}>
        <div className={classes.contentContainer}>
          {/* Header */}
          <div>
            {/* Title and Copy Button */}
            <div className={classes.titleContainer}>
              <h1 className={classNames(text.headerII, text.bold)}>Let's Get Started!</h1>
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
            <h2 className={classNames(text.body, text.gray)}> Tell us about your tech stack</h2>
          </div>

          {/* Questions */}
          <div className={classes.questionsContainer}>
            {questions.map((question) => (
              <InputField
                key={question.key}
                question={question.question}
                questionOptions={question.options}
                setValue={question.setValue}
              />
            ))}
          </div>
          {networkState.formSubmitIsErroring && (
            <div className={classNames(text.subHeader, text.error)}>
              ERROR: Form could not be submitted. Please try again later.
            </div>
          )}
          <div className={classes.submitContainer}>
            <button
              className={classNames(button.darkBlue, { [button.disabled]: !allFieldsValid })}
              onClick={handleNextClick}
              disabled={!allFieldsValid}
            >
              Next
            </button>
          </div>
        </div>
        {networkState.formSubmitIsLoading && (
          <div className={classNames(ui.loadingContainer, ui.opaque)}>
            <CircularProgress color="secondary" />
          </div>
        )}
        <EaveSideBanner />
      </div>
    );
  }
};

export default Onboarding;
