import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import { DateCalendar } from "@mui/x-date-pickers";
import dayjs, { Dayjs } from "dayjs";
import React, { useCallback, useEffect, useState } from "react";

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

  useEffect(() => {
    if (timeDropdownOpen) {
      document.getElementById(selectedTime.label)?.scrollIntoView();
    }
  }, [timeDropdownOpen]);

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

  const timeSelectorId = "time-selector-menu";
  const timeSelectorMenuClickOffHandler = (target: HTMLElement) => {
    /* We want to close the dropdown selector if the clicked `target`
    element is not a child of the selector (i.e. click was outside it).
    However, the dropdown component swaps the up/down chevron icon completely
    into or out of the DOM whenever it is clicked. So, if the icon SVG 
    element is clicked directly, it will no longer be part of the DOM 
    by the time we're handling this event, which would cause us to incorrectly
    conclude that a click on the dropdown icon itself is outside the selector
    menu, closing the menu as soon as it opens.
    To prevent that, I make the assumption that any element that is not
    part contained in the DOM was likely to have been the swapped chevron
    dropdown icon.
    Therefore: only clicked elements that are still part of the DOM are
    considered when checking to see if the click was outside the dropdown.
    */
    const targetIsStillPartOfDOM = document.contains(target);

    // close dropdown if the clicked element is not a child of
    // the time selector dropdown element (i.e. click was outside timeSelectorId)
    if (targetIsStillPartOfDOM && !target.closest(`#${timeSelectorId}`)) {
      setTimeDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("click", (event: MouseEvent) => {
      if (event.target) {
        timeSelectorMenuClickOffHandler(event.target as HTMLElement);
      }
    });
  }, []);

  return (
    <DateTimeContainer>
      <TimeRow>
        <TooltipButton info="Recommended plans will be within roughly a 4 hour window from selected start time." />
        <TimeTitle>Date Start Time:</TimeTitle>
        <TimePicker id={timeSelectorId}>
          <DropdownButtonContainer onClick={() => setTimeDropdownOpen(!timeDropdownOpen)}>
            <Time data-selected>{selectedTime.label}</Time>
            <DropdownButton open={timeDropdownOpen} />
          </DropdownButtonContainer>
          {timeDropdownOpen && (
            <TimeOptions>
              {timeOptions.map((timeObj) => (
                <TimeButton id={timeObj.label} key={timeObj.label} onClick={() => handleTimeChange(timeObj)}>
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
