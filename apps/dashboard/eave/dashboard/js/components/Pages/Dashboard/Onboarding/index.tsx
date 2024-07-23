"use client";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import InputField from "./InputField";
import SideBanner from "./SideBanner";
import {
  ColourOption,
  aiOptions,
  copyString,
  frameworksOptions,
  languagesOptions,
  platformOptions,
} from "./questionOptions";

const useStyles = makeStyles()((theme) => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
  content: {
    flex: 2,
    border: "2px solid",
    overflow: "auto",
    height: "100vh",
    justifyContent: "flex-end",
    paddingTop: theme.spacing(8),
    paddingLeft: theme.spacing(8),
    paddingRight: theme.spacing(8),
  },
  titleAndButton: {
    border: "2px solid black",
    display: "flex",
    padding: theme.spacing(0),
    flexDirection: "row",
    justifyContent: "space-between",
    height: "fit-content",
    alignItems: "center",
  },
  headerText: {
    fontSize: 36,
    margin: 0,
    height: "fit-content",
    // border: "1px solid #1980DF",
  },
  subText: {
    color: "#7D7D7D",
    fontSize: 18,
    margin: 0,
    marginTop: theme.spacing(1),
  },
  button: {
    backgroundColor: "#E8F4FF",
    color: theme.palette.success.main,
    borderRadius: 4,
    margin: 0,
    padding: "8px 8px",
    height: "fit-content",
    border: "1px solid #1980DF",
    fontSize: 16,
    fontWeight: "bold",
  },
  buttonBlue: {
    backgroundColor: "#1980DF",
    color: "white",
    borderRadius: 40,
    margin: 0,
    padding: "16px 32px",
    height: "fit-content",
    border: "1px solid #1980DF",
    fontSize: 24,
    fontWeight: "bold",
  },
  buttonContainer: {
    // border: "2px solid black",
    marginTop: 32,
    display: "flex",
    justifyContent: "flex-end",
  },
  border: {
    // border: "2px solid black",
  },

  questionText: {
    fontSize: 18,
    fontWeight: "bold",
    margin: 0,
  },
  questionsContainer: {
    marginTop: 32,
  },
  question: {
    marginTop: 32,
  },
}));

const Onboarding = () => {
  const { classes } = useStyles();
  const navigate = useNavigate();
  // One State
  const [platformValue, setPlatformValue] = useState<readonly ColourOption[]>([]);
  const [languagesValue, setLanguagesValue] = useState<readonly ColourOption[]>([]);
  const [frameworksValue, setFrameworksValue] = useState<readonly ColourOption[]>([]);
  const [aiValue, setAiValue] = useState<readonly ColourOption[]>([]);

  // Todo: handle each error message:
  const handleNextClick = () => {
    if (
      platformValue.length === 0 ||
      languagesValue.length === 0 ||
      frameworksValue.length === 0 ||
      aiValue.length === 0
    ) {
      alert("Invalid Form");
      return;
    }
    console.log(platformValue);
    navigate("/waitlist");
  };

  return (
    <div className={classes.main}>
      <div className={classes.content}>
        {/* Header */}
        <div className={classes.border}>
          {/* Title and Copy Button */}
          <div className={classes.titleAndButton}>
            <h1 className={classes.headerText}>Let's Get Started!</h1>
            <button
              className={classes.button}
              onClick={() => {
                navigator.clipboard.writeText(copyString);
              }}
            >
              {" "}
              Copy and send to team{" "}
            </button>
          </div>
          <h2 className={classes.subText}> Tell us about your tech stack</h2>
        </div>

        {/* Questions */}
        <div className={classes.questionsContainer}>
          <InputField
            question={"Which platforms are you building for?"}
            questionOptions={platformOptions}
            setValue={setPlatformValue}
          />
          <InputField
            question={"Which languages are you using?"}
            questionOptions={languagesOptions}
            setValue={setLanguagesValue}
          />
          <InputField
            question={"Which libraries and frameworks are you using?"}
            questionOptions={frameworksOptions}
            setValue={setFrameworksValue}
          />
          <InputField
            question={"Which (if any) of these AI platforms are you using?"}
            questionOptions={aiOptions}
            setValue={setAiValue}
          />
        </div>
        <div className={classes.buttonContainer}>
          <button className={classes.buttonBlue} onClick={handleNextClick}>
            Next
          </button>
        </div>
      </div>

      <SideBanner />
    </div>
  );
};

export default Onboarding;
