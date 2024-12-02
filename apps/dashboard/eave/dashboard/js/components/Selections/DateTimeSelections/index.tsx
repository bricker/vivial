import React, { useState, useCallback } from "react";
import dayjs from "dayjs";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled  } from "@mui/material";
import { DateCalendar as BaseDatePicker, TimePicker as BaseTimePicker } from '@mui/x-date-pickers';
import Typography from "@mui/material/Typography";
import TooltipButton from "../../Buttons/TooltipButton";

interface DateTimeSelectionsProps {
  cta: string;
  onSubmit: (selectedTime: Date) => void;
  startTime: Date;
};

const DateTimeContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  width: "100%",
}));

const TimeRow = styled("div")(() => ({
  display: "flex",
  width: 320, // width of MUI calendar
  alignItems: "center",
  paddingBottom: 16,
  borderBottom: "1.08px solid #595959", // one-off color
}));

const TimeTitle = styled(Typography)(() => ({
  fontWeight: 500,
  margin: "0 16px 0 4px",
}));

const TimePicker = styled(BaseTimePicker)(({ theme }) => ({
  maxWidth: 124,
  "& .MuiInputBase-root": {
    paddingRight: 0,
  },
  "& .MuiOutlinedInput-notchedOutline": {
    border: "none",
  },
  "& .MuiInputBase-input": {
    color: theme.palette.common.white,
    border: `1px solid ${theme.palette.accent[2]}`,
    borderRadius: 100,
    fontSize: rem("16px"),
    lineHeight: rem("19px"),
    fontWeight: 500,
    padding: "10px 24px",
  }
}));

const DatePicker = styled(BaseDatePicker)(() => ({
  margin: 0,
}));

const DateTimeSelections = ({ cta, startTime, onSubmit}: DateTimeSelectionsProps) => {
  // split out time
  const [selectedTime, setSelectedTime] = useState(dayjs(startTime));
  const minTime = dayjs().hour(6).minute(0); // 6:00 AM
  const maxTime = dayjs().hour(20).minute(30); // 8:30 PM

  const handleSumbit = useCallback(() => {
    // TODO: Combine time and date into one Date object
    // TODO: Convert from days js to Date obj
  }, []);

  return (
    <DateTimeContainer>
      <TimeRow>
        <TooltipButton info="Recommended plans will be within roughly a 4 hour window from selected start time." />
        <TimeTitle>Date Start Time:</TimeTitle>
        {/* <TimePicker
          slotProps={{
            field: { shouldRespectLeadingZeros: true },
            digitalClockSectionItem: { sx: { backgroundColor: "red" }}
          }}

          // thresholdToRenderTimeInASingleColumn={500}
          defaultValue={selectedTime}
          minTime={minTime}
          maxTime={maxTime}
          format="LT"
          timeSteps={{ minutes: 30 }}
          thresholdToRenderTimeInASingleColumn={500}
          skipDisabled
        /> */}
      </TimeRow>
      <DatePicker />
    </DateTimeContainer>
  );
};

export default DateTimeSelections;
