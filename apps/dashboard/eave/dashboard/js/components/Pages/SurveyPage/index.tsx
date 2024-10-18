import { AppContext } from "$eave-dashboard/js/context/AppContext.js";
import { textStyles } from "$eave-dashboard/js/theme";
import {
  Button,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Slider,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import classNames from "classnames";
import dayjs from "dayjs";
import React, { useContext, useState } from "react";
import { makeStyles } from "tss-react/mui";
import OutingLoader from "../../OutingLoader/index.js";

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

const budgetOptions = [
  {
    value: 0,
    label: "$",
    ariaLabel: "Cheap as possible",
  },
  {
    value: 1,
    label: "$$",
    ariaLabel: "Some money",
  },
  {
    value: 2,
    label: "$$$",
    ariaLabel: "More money",
  },
  {
    value: 3,
    label: "$$$$",
    ariaLabel: "Any amount",
  },
];

// const vibeOptions = ["sedentary", "active", "romantic", "casual", "intimate", "social"];

const laNeighborhoodOptions = [
  {
    value: ["90011"], // TODO: fill in proper postal codes
    label: "North Valley",
  },
  {
    value: ["sv"],
    label: "South Valley",
  },
  {
    value: ["wl"],
    label: "West LA",
  },
  {
    value: ["c"],
    label: "Central",
  },
  {
    value: ["e"],
    label: "East",
  },
  {
    value: ["sl"],
    label: "South LA",
  },
  {
    value: ["h"],
    label: "Harbor",
  },
];

const SurveyPage = () => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();

  const { submitSurvey } = useContext(AppContext);
  const [networkState] = submitSurvey!.networkState;

  // default time to tomorrow
  const today = new Date();
  const tomorrow = new Date(today.setDate(today.getDate() + 1)); // TODO: enforce 24h buffer
  const [time, setTime] = useState(dayjs(tomorrow));
  const [locations, setLocations] = useState(() => [...Array(laNeighborhoodOptions.length).keys()]);
  const [budget, setBudget] = useState(2);
  const [attendees, setAttendees] = useState(2);
  // TODO: client side validation!

  const handleSubmitClick = () => {
    submitSurvey!.execute({
      visitorId: "TODO UUID",
      startTime: time.toDate(),
      searchAreaIds: locations, // TODO: convert to area codes
      budget: budget,
      headcount: attendees,
    });
  };

  if (networkState.loading) {
    return <OutingLoader />;
  }

  return (
    <div className={classes.main}>
      <div className={classes.contentContainer}>
        <div>
          <div className={classes.titleContainer}>
            <h1 className={classNames(text.headerII, text.bold)}>Let's Plan your Date!</h1>
          </div>
          <h2 className={classNames(text.body, text.gray)}>Tell us about the kind of date you want.</h2>
        </div>

        {/* Questions */}
        <FormControl className={classes.questionsContainer}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <FormLabel id="date-picker-label">When will your date be?</FormLabel>
            <DateTimePicker
              label="Date time picker"
              value={time}
              onChange={(newValue: any) => setTime(newValue || dayjs(tomorrow))}
            />
          </LocalizationProvider>

          <FormLabel id="locations-selector-label">What areas of Los Angeles can the date be in?</FormLabel>
          <ToggleButtonGroup
            id="locations-selector"
            value={locations}
            onChange={(_e, newIndices) => setLocations(newIndices)}
            aria-label="date area locations selector"
          >
            {laNeighborhoodOptions.map((neighborhood, i) => {
              return (
                <ToggleButton value={i} key={neighborhood.label} aria-label={neighborhood.label}>
                  {neighborhood.label}
                </ToggleButton>
              );
            })}
          </ToggleButtonGroup>

          <FormLabel id="budget-selector">What is your budget?</FormLabel>
          <Slider
            aria-label="Budget selection slider"
            value={budgetOptions[budget]?.value || budgetOptions.length - 1}
            onChange={(_e, newValue) => setBudget(newValue as number)}
            getAriaValueText={(_value, index) => budgetOptions[index]?.ariaLabel || "Any amount"}
            step={1}
            min={0}
            max={budgetOptions.length - 1}
            marks={budgetOptions}
          />

          <FormLabel id="attendees-group-label">How many people are you going on the date?</FormLabel>
          <FormControl>
            <RadioGroup
              aria-labelledby="attendees-group-label"
              name="attendees-group"
              value={attendees}
              onChange={(e) => setAttendees(parseInt(e.target.value))}
            >
              <FormControlLabel value={1} control={<Radio />} label="1" />
              <FormControlLabel value={2} control={<Radio />} label="2" />
            </RadioGroup>
          </FormControl>

          {/* <FormLabel id="vibe-selector-label">What's the vibe?</FormLabel>
          <Select
            labelId="vibe-selector-label"
            id="vibe-selector"
            value={vibe}
            onChange={(e) => setVibe(e.target.value instanceof Array ? e.target.value : [e.target.value])}
            autoWidth
            aria-labelledby="vibe-selector-label"
            multiple
          >
            {vibeOptions.map((option) => {
              return (
                <MenuItem value={option} key={option}>
                  {option.toLocaleUpperCase()}
                </MenuItem>
              );
            })}
          </Select> */}
        </FormControl>

        {networkState.error && (
          <div className={classNames(text.subHeader, text.error)}>
            ERROR: Form could not be submitted. Please try again later.
          </div>
        )}
        <div className={classes.submitContainer}>
          <Button variant="contained" onClick={handleSubmitClick}>
            Show me my Date
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SurveyPage;
