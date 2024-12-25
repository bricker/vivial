import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import { DateCalendar } from "@mui/x-date-pickers";
import dayjs, { Dayjs } from "dayjs";
import React, { useCallback, useState } from "react";

import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import DropdownButton from "../../Buttons/DropdownButton";
import PrimaryButton from "../../Buttons/PrimaryButton";
import TooltipButton from "../../Buttons/TooltipButton";
import CheckIcon from "../../Icons/CheckIcon";

import { getMaxDate, getMinDate, getTimeObj, getTimeOptions, TimeObj } from "./helpers";

interface DateTimeSelectionsProps {
  cta: string;
  onSubmit: (selectedTime: Date) => void;
  startDateTime: Date;
}

const DateTimeContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  width: "100%",
}));

const TimeRow = styled("div")(() => ({
  position: "relative",
  display: "flex",
  width: 320, // width of MUI calendar
  alignItems: "center",
  padding: "8px 4px 24px",
  borderBottom: "1.08px solid #595959", // one-off color
}));

const TimeTitle = styled(Typography)(() => ({
  fontWeight: 500,
  margin: "0 16px 0 4px",
}));

const TimePicker = styled("div")(({ theme }) => ({
  border: `1px solid ${theme.palette.accent[2]}`,
  backgroundColor: theme.palette.grey[900],
  zIndex: 1,
  position: "absolute",
  left: 162,
  top: 0,
  padding: "4px 16px 2px 28px",
  borderRadius: "20px",
  maxHeight: 358,
  overflowY: "auto",
}));

const TimeOptions = styled("div")(() => ({
  paddingTop: 6,
}));

const Time = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontWeight: 500,
  "&[data-selected]": {
    display: "inline",
    color: theme.palette.common.white,
  },
}));

const TimeButton = styled(Button)(() => ({
  padding: "12px 0px",
  minWidth: 0,
  display: "block",
  "&:hover": {
    backgroundColor: "transparent",
  },
}));

const DropdownButtonContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  "&:hover": {
    cursor: "pointer",
  },
}));

const DatePicker = styled(DateCalendar)(({ theme }) => ({
  height: 316,
  margin: 0,
  "& button.MuiButtonBase-root": {
    fontWeight: 500,
  },
  "& button.Mui-selected": {
    backgroundColor: theme.palette.accent[2],
    "&:focus, &:active, &:hover": {
      backgroundColor: theme.palette.accent[2],
    },
  },
}));

const SubmitButton = styled(PrimaryButton)(() => ({
  maxWidth: 264, // aligns with MUI calendar
}));

const DateTimeSelections = ({ cta, startDateTime, onSubmit }: DateTimeSelectionsProps) => {
  const defaultValue = dayjs(startDateTime);
  const [selectedDay, setSelectedDay] = useState(defaultValue);
  const [selectedTime, setSelectedTime] = useState(getTimeObj(defaultValue));
  const [timeOptions, setTimeOptions] = useState(getTimeOptions(defaultValue));
  const [timeDropdownOpen, setTimeDropdownOpen] = useState(false);

  const handleDayChange = useCallback((value: Dayjs) => {
    setSelectedDay(value);
    setTimeOptions(getTimeOptions(value));
  }, []);

  const handleTimeChange = useCallback((value: TimeObj) => {
    setSelectedTime(value);
    setTimeDropdownOpen(false);
  }, []);

  const handleSubmit = useCallback(() => {
    const selectedDateTime = selectedDay.toDate();
    selectedDateTime.setHours(selectedTime.hour, selectedTime.minute, 0);
    onSubmit(selectedDateTime);
  }, [selectedTime, selectedDay]);

  return (
    <DateTimeContainer>
      <TimeRow>
        <TooltipButton info="Recommended plans will be within roughly a 4 hour window from selected start time." />
        <TimeTitle>Date Start Time:</TimeTitle>
        <TimePicker>
          <DropdownButtonContainer onClick={() => setTimeDropdownOpen(!timeDropdownOpen)}>
            <Time data-selected>{selectedTime.label}</Time>
            <DropdownButton open={timeDropdownOpen} />
          </DropdownButtonContainer>
          {timeDropdownOpen && (
            <TimeOptions>
              {timeOptions.map((timeObj) => (
                <TimeButton key={timeObj.label} onClick={() => handleTimeChange(timeObj)}>
                  {timeObj.label === selectedTime.label ? (
                    <Time data-selected>
                      {timeObj.label} <CheckIcon />
                    </Time>
                  ) : (
                    <Time>{timeObj.label}</Time>
                  )}
                </TimeButton>
              ))}
            </TimeOptions>
          )}
        </TimePicker>
      </TimeRow>
      <DatePicker
        defaultValue={defaultValue}
        onChange={handleDayChange}
        minDate={getMinDate()}
        maxDate={getMaxDate()}
        disablePast
      />
      <SubmitButton onClick={handleSubmit} bg={colors.lightPurpleAccent} fullWidth>
        {cta}
      </SubmitButton>
    </DateTimeContainer>
  );
};

export default DateTimeSelections;
