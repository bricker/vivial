import {
  OutingBudget,
  type ActivityCategory,
  type RestaurantCategory,
  type PreferencesInput,
} from "$eave-dashboard/js/graphql/generated/graphql";

import { useGetSearchRegionsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import React, { useCallback, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "$eave-dashboard/js/store";

import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import { getVisitorId } from "$eave-dashboard/js/analytics/segment";
import { getInitialStartTime, getGroupPreferences } from "./helpers";

import Typography from "@mui/material/Typography";
import Modal from "../../Modal";
import Paper from "../../Paper";
import DateAreaSelections from "../../Selections/DateAreaSelections";
import DateSelections from "../../Selections/DateSelections";
import DateTimeSelections from "../../Selections/DateTimeSelections";
import EditPreferencesOption from "./Options/EditPreferencesOption";
import PreferencesView from "./Views/PreferencesView";
import LoadingView from "./Views/LoadingView";


const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
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
  // const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const isLoggedIn = true;

  const { data: searchRegionsData, isLoading: searchRegionsAreLoading } = useGetSearchRegionsQuery({});
  const searchRegions = searchRegionsData?.searchRegions;

  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [headcount, setHeadcount] = useState(2);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const [startTime, setStartTime] = useState(getInitialStartTime());
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);

  // TODO: fetch existing preferences from backend (pending backend implementation);
  const [userPreferences, setUserPreferences] = useState<PreferencesInput|null>(null);
  const [userPreferencesOpen, setUserPreferencesOpen] = useState(false);
  const [partnerPreferences, setPartnerPreferences] = useState<PreferencesInput|null>(null);
  const [partnerPreferencesOpen, setPartnerPreferencesOpen] = useState(false);

  const handleSubmit = useCallback(async () => {
    const _visitorId = await getVisitorId();
    const _groupPreferences = getGroupPreferences(userPreferences, partnerPreferences);
    // TODO: call planOuting mutation.
  }, []);

  const handleSubmitUserOpenToBars = useCallback((open: boolean) => {
    // TODO: call preferences mutation (pending backend implementation).
  }, []);

  const handleSubmitUserRestaurantPreferences = useCallback((categories: RestaurantCategory[]) => {
    // TODO: call preferences mutation (pending backend implementation).
  }, []);

  const handleSubmitUserActivityPreferences = useCallback((categories: ActivityCategory[]) => {
    // TODO: call preferences mutation (pending backend implementation).
  }, []);

  const handleSelectPartnerOpenToBars = useCallback((open: boolean) => {
    // TODO
  }, []);

  const handleSelectPartnerRestaurantPreferences = useCallback((categories: RestaurantCategory[]) => {
    // TODO
  }, []);

  const handleSelectPartnerActivityPreferences = useCallback((categories: ActivityCategory[]) => {
    // TODO
  }, []);

  const handleSelectHeadcount = useCallback((value: number) => {
    setHeadcount(value);
  }, []);

  const handleSelectBudget = useCallback((value: OutingBudget) => {
    setBudget(value);
  }, []);

  const handleSelectSearchAreas = useCallback((value: string[]) => {
    setSearchAreaIds(value);
    setAreasOpen(false);
  }, []);

  const handleSelectStartTime = useCallback((value: Date) => {
    setStartTime(value);
    setDatePickerOpen(false);
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
    return <LoadingView />;
  }

  if (isLoggedIn) {
    // if (userPreferencesOpen) {
      return (
        <PreferencesView
          title="Get personalized recommendations"
          subtitle="Your saved preferences are used to make more personalized recommendations."
          userPreferences={userPreferences}
          onSubmitOpenToBars={handleSubmitUserOpenToBars}
          onSubmitRestaurants={handleSubmitUserRestaurantPreferences}
          onSubmitActivities={handleSubmitUserActivityPreferences}
          onSkip={() => setUserPreferencesOpen(false)}
        />
      );
    // }
    // if (partnerPreferencesOpen) {
    //   return (
    //     <PreferencesView
    //       title="Add partner preferences"
    //       subtitle="We’ll use your saved preferences and your partner preferences to make recommendations."
    //       onSubmitOpenToBars={handleSelectPartnerOpenToBars}
    //       onSubmitRestaurants={handleSelectPartnerRestaurantPreferences}
    //       onSubmitActivities={handleSelectPartnerActivityPreferences}
    //       onSkip={() => setPartnerPreferencesOpen(false)}
    //     />
    //   );
    // }
  }

  return (
    <PageContainer>
      <Paper>
        <Title variant="h1">One Click Date Picked</Title>
        <City>🌴 Los Angeles, California</City>
        <Typography variant="subtitle1">
          Your free date planner. We cover all the details, and you only pay for experiences you book.
        </Typography>
        {isLoggedIn && (
          <>
            <EditPreferencesOption
              label="Your preferences"
              editable={!userPreferences}
              onClickEdit={() => setUserPreferencesOpen(true)}
            />
            <EditPreferencesOption
              label="Add partner preferences (optional)"
              editable={!partnerPreferences}
              onClickEdit={() => setPartnerPreferencesOpen(true)}
            />
          </>
        )}
      </Paper>
      <DateSurvey>
        <DateSelections
          cta="🎲 Pick my date"
          headcount={headcount}
          budget={budget}
          startTime={startTime}
          searchAreaIds={searchAreaIds}
          onSubmit={handleSubmit}
          onSelectHeadcount={handleSelectHeadcount}
          onSelectBudget={handleSelectBudget}
          onSelectStartTime={toggleDatePickerOpen}
          onSelectSearchArea={toggleAreasOpen}
        />
      </DateSurvey>
      <Modal title="Where in LA?" onClose={toggleAreasOpen} open={areasOpen}>
        <DateAreaSelections cta="Save" onSubmit={handleSelectSearchAreas} regions={searchRegions} />
      </Modal>
      <Modal title="When is your date?" onClose={toggleDatePickerOpen} open={datePickerOpen}>
        <DateTimeSelections cta="Save" onSubmit={handleSelectStartTime} startDateTime={startTime} />
      </Modal>
    </PageContainer>
  );
};

export default DateSurveyPage;
