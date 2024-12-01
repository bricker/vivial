import React, { useState, useCallback } from "react";
import { DateCalendar, TimePicker } from '@mui/x-date-pickers';

interface DateTimeSelectionsProps {
  cta: string;
  onSubmit: (selectedTime: Date) => void;
  startTime: Date;
};

const DateTimeSelections = ({ cta, startTime, onSubmit}: DateTimeSelectionsProps) => {
  const [selectedTime, setSelectedTime] = useState(startTime);

  const handleSumbit = useCallback(() => {
    onSubmit(selectedTime);
  }, []);

  return (
    <>
      <TimePicker />
      <DateCalendar />
    </>
  );
};

export default DateTimeSelections;
