import React, { useCallback } from "react";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";

import Typography from "@mui/material/Typography";
import HighlightButton from "../../Buttons/HighlightButton";
import LoadingButton from "../../Buttons/LoadingButton";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
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
  marginTop: 8
}));

const DateSurveyPage = () => {
  const handleSubmit = useCallback(() => {

  }, []);

  return (
    <PageContainer>
      <Paper>
        <Title variant="h1">
          One Click Date Picked
        </Title>
        <City>
          🌴 Los Angeles, California
        </City>
        <Typography variant="subtitle1">
          Your free date planner. We cover all the details, and you only pay for experiences you book.
        </Typography>
      </Paper>
      <Survey>
        <SurveyRow>
          <SurveyRowTitle>Who:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton highlightColor={colors.lightPinkAccent} highlighted={true}>
              👥 For 2
            </SurveyButton>
            <SurveyButton highlightColor={colors.lightPinkAccent} highlighted={false}>
              👤 Solo
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>When:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton highlightColor={colors.lightPurpleAccent} highlighted={true}>
              🕑 Tomorrow @ 6pm
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>Where:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton highlightColor={colors.lightOrangeAccent} highlighted={true}>
              📍 Anywhere in LA
            </SurveyButton>
          </SurveyRowButtons>
        </SurveyRow>
        <SurveyRow>
          <SurveyRowTitle>Price:</SurveyRowTitle>
          <SurveyRowButtons>
            <SurveyButton highlightColor={colors.mediumPurpleAccent} highlighted={false}>
              $
            </SurveyButton>
            <SurveyButton highlightColor={colors.mediumPurpleAccent} highlighted={false}>
              $$
            </SurveyButton>
            <SurveyButton highlightColor={colors.mediumPurpleAccent} highlighted={true}>
              $$$
            </SurveyButton>
            <SurveyButton highlightColor={colors.mediumPurpleAccent} highlighted={false}>
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
