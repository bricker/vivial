import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { useGetSearchRegionsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import React, { useCallback, useEffect, useState } from "react";

import { getVisitorId } from "$eave-dashboard/js/analytics/segment";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import { getInitialStartTime } from "./helpers";

import BaseSkeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import HighlightButton from "../../Buttons/HighlightButton";
import LoadingButton from "../../Buttons/LoadingButton";
import Paper from "../../Paper";

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

const Title = styled(Typography)(({ theme }) => ({
  maxWidth: 250,
  marginBottom: 4,
}));

const City = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("14px"),
  lineHeight: rem("18px"),
  marginBottom: 8,
}));

const Survey = styled(Paper)(({ theme }) => ({
  marginTop: 16,
}));

const SurveyRow = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  marginBottom: 16,
}));

const SurveyRowTitle = styled("div")(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem("16px"),
  lineHeight: rem("19px"),
  fontWeight: 500,
  minWidth: 60,
}));

const SurveyRowButtons = styled("div")(() => ({
  display: "flex",
}));

const SurveyButton = styled(HighlightButton)(() => ({
  marginRight: 8,
}));

const SubmitButton = styled(LoadingButton)(() => ({
  marginTop: 8,
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
  const [startTimeLabel, getStartTimeLabel] = useState("Tomorrow @ 6pm");
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);

  const handleSubmit = useCallback(async () => {
    const visitorId = await getVisitorId();
    // TODO: call planOuting mutation and dispatch response to store.
  }, []);

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
      <Survey>
        <SurveyRow>
          <SurveyRowTitle>Who:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton
              onClick={() => setHeadcount(2)}
              highlighted={headcount === 2}
              highlightColor={colors.lightPinkAccent}
            >
              👥 For 2
            </SurveyButton>
            <SurveyButton
              onClick={() => setHeadcount(1)}
              highlighted={headcount === 1}
              highlightColor={colors.lightPinkAccent}
            >
              👤 Solo
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>When:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton
              onClick={() => setCalendarOpen(true)}
              highlightColor={colors.lightPurpleAccent}
              highlighted={true}
            >
              🕑 {startTimeLabel}
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>Where:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton
              onClick={() => setAreasOpen(true)}
              highlightColor={colors.lightOrangeAccent}
              highlighted={true}
            >
              📍 {serachAreaLabel}
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>Price:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton
              onClick={() => setBudget(OutingBudget.Inexpensive)}
              highlighted={budget === OutingBudget.Inexpensive}
              highlightColor={colors.mediumPurpleAccent}
            >
              $
            </SurveyButton>
            <SurveyButton
              onClick={() => setBudget(OutingBudget.Moderate)}
              highlighted={budget === OutingBudget.Moderate}
              highlightColor={colors.mediumPurpleAccent}
            >
              $$
            </SurveyButton>
            <SurveyButton
              onClick={() => setBudget(OutingBudget.Expensive)}
              highlighted={budget === OutingBudget.Expensive}
              highlightColor={colors.mediumPurpleAccent}
            >
              $$$
            </SurveyButton>
            <SurveyButton
              onClick={() => setBudget(OutingBudget.VeryExpensive)}
              highlighted={budget === OutingBudget.VeryExpensive}
              highlightColor={colors.mediumPurpleAccent}
            >
              $$$$
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SubmitButton onClick={handleSubmit} loading={false} fullWidth>
          🎲 Pick my date
        </SubmitButton>
      </Survey>
    </PageContainer>
  );
};

export default DateSurveyPage;
