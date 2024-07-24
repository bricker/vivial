import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { motion } from "framer-motion";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import InputField from "./InputField";
import SideBanner from "./SideBanner";
import {
  ColourOption,
  copyString,
  databaseOptions,
  frameworksOptions,
  languagesOptions,
  platformOptions,
  thirdPartyOptions,
} from "./questionOptions";

const useStyles = makeStyles()((theme) => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
  content: {
    flex: 2,
    // border: "2px solid",
    overflow: "auto",
    height: "100vh",
    justifyContent: "flex-end",
    paddingTop: theme.spacing(8),
    paddingLeft: theme.spacing(8),
    paddingRight: theme.spacing(8),
  },
  titleAndButton: {
    // border: "2px solid black",
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
    cursor: "pointer",
    width: "150px", // Set a fixed width for consistency
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  buttonBlue: {
    backgroundColor: "#1980DF",
    cursor: "pointer",
    color: "white",
    borderRadius: 10,
    margin: 0,
    padding: "16px 32px",
    height: "fit-content",
    border: "1px solid #1980DF",
    fontSize: 20,
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
    marginTop: theme.spacing(2),
  },
  loading: {
    position: "fixed",
    width: "100%",
    height: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.5)",
    zIndex: 100,
  },
}));

const Onboarding = () => {
  const { classes } = useStyles();
  const navigate = useNavigate();

  const [platformValue, setPlatformValue] = useState<readonly ColourOption[]>([]);
  const [languagesValue, setLanguagesValue] = useState<readonly ColourOption[]>([]);
  const [frameworksValue, setFrameworksValue] = useState<readonly ColourOption[]>([]);
  const [databaseValue, setDatabaseValue] = useState<readonly ColourOption[]>([]);
  const [thirdPartyValue, setThirdPartyValue] = useState<readonly ColourOption[]>([]);

  const [platformError, setPlatformError] = useState(false);
  const [languagesError, setLanguagesError] = useState(false);
  const [frameworksError, setFrameworksError] = useState(false);
  const [databaseError, setDatabaseError] = useState(false);
  const [thirdPartyError, setThirdPartyError] = useState(false);

  const [copy, setCopy] = useState(false);

  const { team, getOnboardingFormSubmission, createOnboardingFormSubmission } = useTeam();
  const { onboardingFormNetworkStateCtx } = useContext(AppContext);

  useEffect(getOnboardingFormSubmission, []);

  // check if they have already submitted form
  if (team?.dashboardAccess || team?.onboardingSubmission !== undefined) {
    // check if they are qualified
    if (team?.dashboardAccess) {
      alert("good to go");
    } else {
      navigate("/waitlist");
    }
  }

  const handleNextClick = () => {
    let hasError = false;

    if (platformValue.length === 0) {
      setPlatformError(true);
      hasError = true;
    } else {
      setPlatformError(false);
    }

    if (languagesValue.length === 0) {
      setLanguagesError(true);
      hasError = true;
    } else {
      setLanguagesError(false);
    }

    if (frameworksValue.length === 0) {
      setFrameworksError(true);
      hasError = true;
    } else {
      setFrameworksError(false);
    }

    if (databaseValue.length === 0) {
      setDatabaseError(true);
      hasError = true;
    } else {
      setDatabaseError(false);
    }

    if (thirdPartyValue.length === 0) {
      setThirdPartyError(true);
      hasError = true;
    } else {
      setThirdPartyError(false);
    }

    if (hasError) {
      return;
    }
    // TODO: Change structure
    // [{value: 'mobile', label: 'Mobile'}, {value: 'desktop_app', label: 'Desktop App'}]

    /*
    {
      "question text": ["answer 1", "answer 2"],
      ...
    }
    */
    createOnboardingFormSubmission({
      form_data: {
        platform: platformValue.map((v) => v.value),
        languages: languagesValue.map((v) => v.value),
        frameworks: frameworksValue.map((v) => v.value),
        databases: databaseValue.map((v) => v.value),
        ai: thirdPartyValue.map((v) => v.value),
      },
    });
  };

  return (
    <div className={classes.main}>
      <div className={classes.content}>
        {/* Header */}
        <div className={classes.border}>
          {/* Title and Copy Button */}
          <div className={classes.titleAndButton}>
            <h1 className={classes.headerText}>Let's Get Started!</h1>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.9 }}
              className={classes.button}
              onClick={() => {
                navigator.clipboard.writeText(copyString);
                setCopy(true);
                setTimeout(() => {
                  setCopy(false);
                }, 1500);
              }}
            >
              {copy ? "Copied!" : "Copy Questions"}
            </motion.button>
          </div>
          <h2 className={classes.subText}> Tell us about your tech stack</h2>
        </div>

        {/* Questions */}
        <div className={classes.questionsContainer}>
          <InputField
            question={"Which platform(s) does your product support? "}
            questionOptions={platformOptions}
            setValue={setPlatformValue}
            error={platformError}
          />
          <InputField
            question={"Which programming language(s) are used to build your product?"}
            questionOptions={languagesOptions}
            setValue={setLanguagesValue}
            error={languagesError}
          />
          <InputField
            question={"Which libraries and framework(s) are used to build your product?"}
            questionOptions={frameworksOptions}
            setValue={setFrameworksValue}
            error={frameworksError}
          />
          <InputField
            question={"Which database(s) are used to store your product data?"}
            questionOptions={databaseOptions}
            setValue={setDatabaseValue}
            error={databaseError}
          />
          <InputField
            question={"Which third party service(s) are integrated into your product?"}
            questionOptions={thirdPartyOptions}
            setValue={setThirdPartyValue}
            error={thirdPartyError}
          />
        </div>
        <div className={classes.buttonContainer}>
          <button className={classes.buttonBlue} onClick={handleNextClick}>
            Next
          </button>
        </div>
      </div>
      {/* <div className={classes.loading}>
        <CircularProgress color="secondary" />
      </div> */}
      <SideBanner />
    </div>
  );
};

export default Onboarding;
