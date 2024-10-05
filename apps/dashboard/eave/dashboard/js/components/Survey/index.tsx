import { AppContext } from "$eave-dashboard/js/context/Provider";
import { buttonStyles, textStyles } from "$eave-dashboard/js/theme";
import classNames from "classnames";
import React, { useContext, useState } from "react";
import { makeStyles } from "tss-react/mui";

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

const Survey = () => {
  const { classes } = useStyles();
  const { classes: button } = buttonStyles();
  const { classes: text } = textStyles();

  const { surveyNetworkStateCtx } = useContext(AppContext);
  const [networkState] = surveyNetworkStateCtx!;

  const [location, setLocation] = useState(["90011"]);
  const [budget, setBudget] = useState(["$", "$$", "$$$", "$$$$"]);
  const [attendees, setAttendees] = useState(2);
  const [time, setTime] = useState(new Date());
  const [vibe, setVibe] = useState<string | undefined>(undefined);

  const handleSubmitClick = () => {
    // TODO: post data
  };

  return (
    <div className={classes.main}>
      <div className={classes.contentContainer}>
        {/* Header */}
        <div>
          {/* Title and Copy Button */}
          <div className={classes.titleContainer}>
            <h1 className={classNames(text.headerII, text.bold)}>Let's Plan your Date!</h1>
          </div>
          <h2 className={classNames(text.body, text.gray)}>Tell us about the kind of date you want.</h2>
        </div>

        {/* Questions */}
        <div className={classes.questionsContainer}>
          <label>
            When will your date be? {/* TODO: proper date range selector + enforce 24h buffer */}
            <input name="time" type="datetime-local" value={time.toISOString()} onChange={(e) => setTime(new Date(e.target.value))} />
          </label>

          <label>
            What area of Los Angeles would you like the date to be in? {/* TODO: proper tyupe */}
            <input name="location" value={location} onChange={(e) => setLocation(e.target.value)} />
          </label>

          <label>
            What is your budget? <input name="budget" value={budget} onChange={(e) => setBudget(e.target.value)} />
          </label>

          <label>
            How many people are you planning for?{" "}
            <input name="attendees" type="number" value={attendees} onChange={(e) => setAttendees(parseInt(e.target.value))} />
          </label>

          <label>
            What is the vibe?
            <select name="vibe" value={vibe} onChange={(e) => setVibe(e.target.value)} multiple={true}>
              <option value="sedentary">Sedentary</option>
              <option value="active">Active</option>
              <option value="romantic">Romantic</option>
              <option value="casual">Casual</option>
              <option value="intimate">Intimiate</option>
              <option value="social">Social</option>
            </select>
          </label>
        </div>

        {networkState.formSubmitIsErroring && (
          <div className={classNames(text.subHeader, text.error)}>
            ERROR: Form could not be submitted. Please try again later.
          </div>
        )}
        <div className={classes.submitContainer}>
          <button
            className={classNames(button.darkBlue, { [button.disabled]: !allFieldsValid })}
            onClick={handleSubmitClick}
            disabled={!allFieldsValid}
          >
            Show me my Date
          </button>
        </div>
      </div>
    </div>
  );
};

export default Survey;
