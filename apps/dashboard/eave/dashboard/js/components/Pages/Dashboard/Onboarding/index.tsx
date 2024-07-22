"use client";
import React from "react";
import { makeStyles } from "tss-react/mui";
import InputField from "./InputField";
import SideBanner from "./SideBanner";
import { aiOptions, frameworksOptions, languagesOptions, platformOptions } from "./questionOptions";

const useStyles = makeStyles()(() => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
  content: {
    flex: 2,
    overflow: "auto",
    height: "100vh",
    paddingTop: 64,
    paddingLeft: 64,
    paddingRight: 64,
    // Currently not including padding in 2/3 size.
    boxSizing: "border-box",
  },
  titleAndButton: {
    // border: "2px solid black",
    display: "flex",
    padding: 0,
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
    marginTop: 8,
  },
  button: {
    backgroundColor: "#E8F4FF",
    color: "#1980DF",
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

  return (
    <div className={classes.main}>
      <div className={classes.content}>
        {/* Header */}
        <div className={classes.border}>
          {/* Title and Copy Button */}
          <div className={classes.titleAndButton}>
            <h1 className={classes.headerText}>Let's Get Started!</h1>
            <button className={classes.button}> Copy and send to team </button>
          </div>
          <h2 className={classes.subText}> Tell us about your tech stack</h2>
        </div>

        {/* Questions */}
        <div className={classes.questionsContainer}>
          <InputField question={"Which platforms are you building for?"} questionOptions={platformOptions} />
          <InputField question={"Which languages are you using?"} questionOptions={languagesOptions} />
          <InputField question={"Which libraries and frameworks are you using?"} questionOptions={frameworksOptions} />
          <InputField question={"Which (if any) of these AI platforms are you using?"} questionOptions={aiOptions} />
        </div>
        <div className={classes.buttonContainer}>
          <button className={classes.buttonBlue}>Next</button>
        </div>
      </div>

      <SideBanner />
    </div>
  );
};

export default Onboarding;
