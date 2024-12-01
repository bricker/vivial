import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { useGetSearchRegionsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import React, { useCallback, useEffect, useState } from "react";

import { getVisitorId } from "$eave-dashboard/js/analytics/segment";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import { getInitialStartTime } from "./helpers";

import BaseSkeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import Modal from "../../Modal";
import Paper from "../../Paper";
import DateAreaSelections from "../../Selections/DateAreaSelections";
import DateSelections from "../../Selections/DateSelections";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
}));

const Skeleton = styled(BaseSkeleton)(() => ({
  marginBottom: 16,
  borderRadius: "14.984px",
  "&:last-of-type": {
    marginBottom: 0,
  },
}));

const Title = styled(Typography)(() => ({
  maxWidth: 250,
  marginBottom: 4,
}));

const City = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("14px"),
  lineHeight: rem("18px"),
  marginBottom: 8,
}));

const DateSurvey = styled(Paper)(() => ({
  marginTop: 16,
}));

const DateSurveyPage = () => {
  const { data: searchRegionsData, isLoading: searchRegionsAreLoading } = useGetSearchRegionsQuery();
  const searchRegions = searchRegionsData?.data?.searchRegions;

  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [groupPreferences, setGroupPreferences] = useState([]);
  const [headcount, setHeadcount] = useState(2);
  const [searchAreaIds, setSearchAreaIds] = useState([""]);
  const [serachAreaLabel, setSearchAreaLabel] = useState("Anywhere in LA");
  const [startTime, setStartTime] = useState(getInitialStartTime());
  const [startTimeLabel, setStartTimeLabel] = useState("Tomorrow @ 6pm");
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);

  const handleSubmit = useCallback(async () => {
    const visitorId = await getVisitorId();
    // TODO: call planOuting mutation and dispatch response to store.
  }, []);

  const handleSelectHeadcount = useCallback((value: number) => {
    setHeadcount(value);
  }, []);

  const handleSelectBudget = useCallback((value: OutingBudget) => {
    setBudget(value);
  }, []);

  const handleSelectSearchAreas = useCallback((searchAreaIds: string[]) => {
    console.log(searchAreaIds);

    setSearchAreaIds(searchAreaIds);
  }, []);

  const toggleDatePickerOpen = useCallback(() => {
    setDatePickerOpen(!datePickerOpen);
  }, [datePickerOpen]);

  const toggleAreasOpen = useCallback(() => {
    setAreasOpen(!areasOpen);
  }, [areasOpen]);

  useEffect(() => {
    if (searchRegions) {
      setSearchAreaIds(searchRegions.map((region) => region.id));
    }
  }, [searchRegions]);

  if (searchRegionsAreLoading) {
    return (
      <PageContainer>
        <Skeleton variant="rectangular" width="100%" height={218} />
        <Skeleton variant="rectangular" width="100%" height={332} />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Paper>
        <Title variant="h1">One Click Date Picked</Title>
        <City>🌴 Los Angeles, California</City>
        <Typography variant="subtitle1">
          Your free date planner. We cover all the details, and you only pay for experiences you book.
        </Typography>
      </Paper>
      <DateSurvey>
        <DateSelections
          cta="🎲 Pick my date"
          headcount={headcount}
          startTime={startTimeLabel}
          searchArea={serachAreaLabel}
          budget={budget}
          onSubmit={handleSubmit}
          onSelectHeadcount={handleSelectHeadcount}
          onSelectBudget={handleSelectBudget}
          onSelectStartTime={toggleDatePickerOpen}
          onSelectSearchArea={toggleAreasOpen}
        />
      </DateSurvey>
      <Modal title="Where in LA?" onClose={toggleAreasOpen} open={areasOpen}>
        <DateAreaSelections cta="Save" regions={searchRegions} onSubmit={handleSelectSearchAreas} />
      </Modal>
      <Modal title="When is your date?" onClose={toggleDatePickerOpen} open={datePickerOpen}>
        DATE PICKER
      </Modal>
    </PageContainer>
  );
};

export default DateSurveyPage;
