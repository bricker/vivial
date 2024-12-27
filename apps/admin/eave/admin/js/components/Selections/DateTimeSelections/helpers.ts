import dayjs, { Dayjs } from "dayjs";

export interface TimeObj {
  label: string;
  hour: number;
  minute: number;
}

export function getMaxDate(): Dayjs {
  const now = new Date();
  const maxDate = new Date(now);
  maxDate.setDate(now.getDate() + 30);
  return dayjs(maxDate);
}

export function getMinDate(): Dayjs {
  const now = new Date();
  const minDate = new Date(now);
  return dayjs(minDate);
}

export function getBaseDay(day: Dayjs): Dayjs {
  return day.hour(0).minute(0).second(0);
}

export function getTimeObj(selectedDay: Dayjs): TimeObj {
  return {
    label: selectedDay.format("h:mma"),
    hour: selectedDay.hour(),
    minute: selectedDay.minute(),
  };
}

export function getTimeOptions(_selectedDay: Dayjs): TimeObj[] {
  const timesBeforeSixPM = [
    { label: "6:00am", hour: 6, minute: 0 },
    { label: "6:30am", hour: 6, minute: 30 },
    { label: "7:00am", hour: 7, minute: 0 },
    { label: "7:30am", hour: 7, minute: 30 },
    { label: "8:00am", hour: 8, minute: 0 },
    { label: "8:30am", hour: 8, minute: 30 },
    { label: "9:00am", hour: 9, minute: 0 },
    { label: "9:30am", hour: 9, minute: 30 },
    { label: "10:00am", hour: 10, minute: 0 },
    { label: "10:30am", hour: 10, minute: 30 },
    { label: "11:00am", hour: 11, minute: 0 },
    { label: "11:30am", hour: 11, minute: 30 },
    { label: "12:00pm", hour: 12, minute: 0 },
    { label: "12:30pm", hour: 12, minute: 30 },
    { label: "1:00pm", hour: 13, minute: 0 },
    { label: "1:30pm", hour: 13, minute: 30 },
    { label: "2:00pm", hour: 14, minute: 0 },
    { label: "2:30pm", hour: 14, minute: 30 },
    { label: "3:00pm", hour: 15, minute: 0 },
    { label: "3:30pm", hour: 15, minute: 30 },
    { label: "4:00pm", hour: 16, minute: 0 },
    { label: "4:30pm", hour: 16, minute: 30 },
    { label: "5:00pm", hour: 17, minute: 0 },
    { label: "5:30pm", hour: 17, minute: 30 },
  ];
  const timesAfterSixPM = [
    { label: "6:00pm", hour: 18, minute: 0 },
    { label: "6:30pm", hour: 18, minute: 30 },
    { label: "7:00pm", hour: 19, minute: 0 },
    { label: "7:30pm", hour: 19, minute: 30 },
    { label: "8:00pm", hour: 20, minute: 0 },
    { label: "8:30pm", hour: 20, minute: 30 },
  ];
  return timesBeforeSixPM.concat(timesAfterSixPM);
}
