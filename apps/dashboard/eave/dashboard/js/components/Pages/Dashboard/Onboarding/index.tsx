import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { buttonStyles, textStyles, uiStyles } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import { motion } from "framer-motion";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import InputField from "./InputField";
import EaveSideBanner from "$eave-dashboard/js/components/EaveSideBanner";
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
    paddingTop: theme.spacing(8),
    paddingLeft: theme.spacing(8),
    paddingRight: theme.spacing(8),
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
  },
}));

const Onboarding = () => {
  const { classes } = useStyles();
  const { classes: button } = buttonStyles();
  const { classes: text } = textStyles();
  const { classes: ui } = uiStyles();

  const navigate = useNavigate();

  const [copyQuestions, setCopyQuestions] = useState(false);

  const { team, getOnboardingFormSubmission, createOnboardingFormSubmission } = useTeam();
  const { onboardingFormNetworkStateCtx } = useContext(AppContext);
  const [networkState] = onboardingFormNetworkStateCtx!;

  const questions = useQuestions();

  useEffect(getOnboardingFormSubmission, []);

  // check if they have already submitted form
  useEffect(() => {
    console.log("Onboarding Submission", team?.onboardingSubmission);
    if (
      !networkState.formDataIsLoading &&
      !networkState.formDataIsErroring &&
      (team?.dashboardAccess || team?.onboardingSubmission)
    ) {
      // Check if they are qualified
      if (team?.dashboardAccess) {
        // Navigate to setup
        navigate("/setup");
      } else {
        // Navigate to waitlist
        navigate("/waitlist");
      }
    }
  }, [networkState.formDataIsLoading, networkState.formDataIsErroring, team, navigate]);

  const handleNextClick = () => {
    let hasError = false;

    // Check if every question is filled
    questions.forEach((question) => {
      if (question.value.length === 0) {
        question.setError(true);
        hasError = true;
      } else {
        question.setError(false);
      }
    });

    if (hasError) {
      return;
    }
    createOnboardingFormSubmission({
      form_data: {
        platform: questions[0]?.value.map((v) => v.value),
        languages: questions[1]?.value.map((v) => v.value),
        frameworks: questions[2]?.value.map((v) => v.value),
        databases: questions[3]?.value.map((v) => v.value),
        third_party: questions[4]?.value.map((v) => v.value),
      },
    });
  };

  return (
    <div className={classes.main}>
      <div className={classes.contentContainer}>
        {/* Header */}
        <div>
          {/* Title and Copy Button */}
          <div className={classes.titleContainer}>
            <h1 className={text.headerII}>Let's Get Started!</h1>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.9 }}
              className={button.default}
              onClick={() => {
                navigator.clipboard.writeText(copyString);
                setCopyQuestions(true);
                setTimeout(() => {
                  setCopyQuestions(false);
                }, 1500);
              }}
            >
              {copyQuestions ? "Copied!" : "Copy Questions"}
            </motion.button>
          </div>
          <h2 className={`${text.body} ${text.gray}`}> Tell us about your tech stack</h2>
        </div>

        {/* Questions */}
        <div className={classes.questionsContainer}>
          {questions.map((question, index) => (
            <InputField
              key={index}
              question={question.question}
              questionOptions={question.options}
              setValue={question.setValue}
              error={question.error}
            />
          ))}
        </div>
        <div className={classes.submitContainer}>
          <button className={button.darkBlue} onClick={handleNextClick}>
            Next
          </button>
        </div>
      </div>
      {networkState.formSubmitIsLoading && (
        <div className={`${ui.loadingContainer} ${ui.opaque}`}>
          <CircularProgress color="secondary" />
        </div>
      )}
      <EaveSideBanner />
    </div>
  );
};

export default Onboarding;
