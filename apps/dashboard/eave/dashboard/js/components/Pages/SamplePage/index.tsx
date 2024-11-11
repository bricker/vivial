import { getVisitorId } from "$eave-dashboard/js/analytics/segment";
import { AppContext } from "$eave-dashboard/js/context/AppContext";
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
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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

const budgetOptions = [
  {
    value: 1,
    label: "$",
    ariaLabel: "Cheap as possible",
  },
  {
    value: 2,
    label: "$$",
    ariaLabel: "Some money",
  },
  {
    value: 3,
    label: "$$$",
    ariaLabel: "More money",
  },
  {
    value: 4,
    label: "$$$$",
    ariaLabel: "Any amount",
  },
];

const laNeighborhoodOptions = [
  {
    value: "US_CA_LA1",
    label: "Central LA & Hollywood",
  },
  {
    value: "US_CA_LA2",
    label: "Downtown Los Angeles",
  },
  {
    value: "US_CA_LA3",
    label: "Pasadena, Glendale, & Northeast LA",
  },
  {
    value: "US_CA_LA4",
    label: "Westside",
  },
  {
    value: "US_CA_LA5",
    label: "South Bay",
  },
  {
    value: "US_CA_LA6",
    label: "San Gabriel Valley",
  },
];

const SurveyPage = () => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();
  const navigate = useNavigate();
  const { submitSurvey } = useContext(AppContext);
  const [networkState, setNetworkState] = submitSurvey!.networkState;

  // default time to tomorrow
  const tomorrow = dayjs().add(1, "day").add(3, "hour");
  const [time, setTime] = useState(tomorrow);
  // indices of selected laNeighborhood entries
  const [locations, setLocations] = useState(() => [0]);
  const [budget, setBudget] = useState(2);
  const [attendees, setAttendees] = useState(2);
  const [errors, setErrors] = useState<any>({});

  const validate = () => {
    const newErrors: any = {};
    const today = dayjs();
    // refetch tommorow in case tab has been sitting open a super long time
    const currTomorrow = today.add(1, "day");
    const nextMonth = today.add(1, "month");

    if (time < currTomorrow) {
      newErrors["time"] = "Must be 24 hours or more from now";
    }
    if (time > nextMonth) {
      newErrors["time"] = "Must be less than one month from now";
    }

    if (locations.length < 1) {
      newErrors["locations"] = "At least one location must be selected";
    }

    return newErrors;
  };

  const handleSubmitClick = async () => {
    const newErrors = validate();
    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      submitSurvey!.execute({
        req: {
          visitorId: await getVisitorId(),
          startTime: time.toDate(),
          searchAreaIds: locations.map((idx) => laNeighborhoodOptions[idx]!.value),
          budget: budget,
          headcount: attendees,
        },
        ctx: submitSurvey!,
      });
    }
  };

  // go to outing display page once data is loaded
  useEffect(() => {
    if (networkState.data?.outingId) {
      navigate(`/outing/${networkState.data.outingId}`);
      // clear response data so that back-nav works
      setNetworkState((prev) => ({
        ...prev,
        data: undefined,
      }));
    }
  }, [navigate, networkState]);

  if (networkState.loading || networkState.data) {
    return <div>Loading...</div>;
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
              onChange={(newValue: any) => setTime(newValue || tomorrow)}
            />
            {errors["time"] && <div>{errors["time"]}</div>}
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
          {errors["locations"] && <div>{errors["locations"]}</div>}

          <FormLabel id="budget-selector">What is your budget?</FormLabel>
          <Slider
            aria-label="Budget selection slider"
            value={budgetOptions[budget]!.value}
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
              onChange={(e) => setAttendees(parseInt(e.target.value, 10))}
            >
              <FormControlLabel value={1} control={<Radio />} label="1" />
              <FormControlLabel value={2} control={<Radio />} label="2" />
            </RadioGroup>
          </FormControl>
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
