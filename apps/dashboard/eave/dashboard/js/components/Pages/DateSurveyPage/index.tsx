import {
  OutingBudget,
  type OutingPreferences,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { type Category } from "$eave-dashboard/js/types/category";

import { useGetOutingPreferencesQuery, useGetSearchRegionsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import React, { useCallback, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "$eave-dashboard/js/store";

import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
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


const PageContainer = styled("div")(({ theme }) => ({
  padding: "24px 16px",
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    backgroundImage: `url("${imageUrl("vivial-map-graphic.png")}")`,
    backgroundPosition: "center bottom",
    backgroundRepeat: "no-repeat",
    backgroundSize: "contain",
    padding: "112px 104px",
    marginBottom: 112,
    minHeight: 675,
  },
  [theme.breakpoints.up(Breakpoint.ExtraLarge)]: {
    minHeight: 900,
  },
}));

const PageContentContainer = styled("div")(({ theme }) => ({
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    display: "flex",
    justifyContent: "center",
  },
}));

const CopyContainer = styled(Paper)(({ theme }) => ({
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    padding: "16px 0 0",
    background: "transparent",
    maxWidth: 426,
    marginRight: 60,
    boxShadow: "none",
  },
}));

const TitleCopy = styled(Typography)(({ theme }) => ({
  maxWidth: 250,
  marginBottom: 4,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    maxWidth: "none",
    marginBottom: 24,
  },
}));

const CityCopy = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("14px"),
  lineHeight: rem("18px"),
  marginBottom: 8,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    border: `1px solid ${theme.palette.primary.main}`,
    color: theme.palette.text.primary,
    display: "inline-block",
    borderRadius: "92.929px",
    fontSize: rem("18.586px"),
    lineHeight: rem("23x"),
    padding: "10px 20px",
    marginBottom: 24,
    fontWeight: 700,
  },
}));

const DateSurveyContainer = styled(Paper)(({ theme }) => ({
  marginTop: 16,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    border: `2px solid ${theme.palette.primary.main}`,
    background: theme.palette.background.paper,
    padding: "64px",
    marginTop: 0,
    marginLeft: 60,
  },
}));

const DateSurveyPage = () => {
  // const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const isLoggedIn = true;

  const { data: outingPreferencesData } = useGetOutingPreferencesQuery({});
  const { data: searchRegionsData, isLoading: searchRegionsAreLoading } = useGetSearchRegionsQuery({});
  const searchRegions = searchRegionsData?.searchRegions;

  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [headcount, setHeadcount] = useState(2);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const [startTime, setStartTime] = useState(getInitialStartTime());
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [outingPreferences, setOutingPreferences] = useState<OutingPreferences|null>(null);
  const [partnerPreferences, setPartnerPreferences] = useState<OutingPreferences|null>(null);
  const [outingPreferencesOpen, setOutingPreferencesOpen] = useState(false);
  const [partnerPreferencesOpen, setPartnerPreferencesOpen] = useState(false);

  const handleSubmit = useCallback(async () => {
    const _visitorId = await getVisitorId();
    const _groupPreferences = getGroupPreferences(outingPreferences, partnerPreferences);
    // TODO: call planOuting mutation.
  }, []);

  const handleSubmitRestaurantPreferences = useCallback((categories: Category[]) => {
    console.log("selected restaurant categories", categories);
    // TODO: call preferences mutation.
    // TODO: handle openToBars
  }, []);

  const handleSubmitActivityPreferences = useCallback((categories: Category[]) => {
    // TODO: call preferences mutation.
  }, []);

  const handlePartnerRestaurantPreferences = useCallback((categories: Category[]) => {
    // TODO
    // TODO: handle open to bars
  }, []);

  const handlePartnerActivityPreferences = useCallback((categories: Category[]) => {
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

  useEffect(() => {
    const viewer = outingPreferencesData?.viewer;
    if (viewer?.__typename === "AuthenticatedViewerQueries") {
      setOutingPreferences(viewer.outingPreferences);
    }
  }, [outingPreferencesData]);

  if (searchRegionsAreLoading) {
    return <LoadingView />;
  }

  if (isLoggedIn) {
    // if (userPreferencesOpen) {
      return (
        <PreferencesView
          title="Get personalized recommendations"
          subtitle="Your saved preferences are used to make more personalized recommendations."
          outingPreferences={outingPreferences}
          onSubmitRestaurants={handleSubmitRestaurantPreferences}
          onSubmitActivities={handleSubmitActivityPreferences}
          onSkip={() => setOutingPreferencesOpen(false)}
        />
      );
    // }
    // if (partnerPreferencesOpen) {
    //   return (
    //     <PreferencesView
    //       title="Add partner preferences"
    //       subtitle="We’ll use your saved preferences and your partner preferences to make recommendations."
    //       onSubmitRestaurants={handleSelectPartnerRestaurantPreferences}
    //       onSubmitActivities={handleSelectPartnerActivityPreferences}
    //       onSkip={() => setPartnerPreferencesOpen(false)}
    //     />
    //   );
    // }
  }

  return (
    <PageContainer>
      <PageContentContainer>
        <CopyContainer>
          <TitleCopy variant="h1">One Click Date Picked</TitleCopy>
          <CityCopy>🌴 Los Angeles, California</CityCopy>
          <Typography variant="subtitle1">
            Your free date planner. We cover all the details, and you only pay for experiences you book.
          </Typography>
        </CopyContainer>
        <DateSurveyContainer>
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
        </DateSurveyContainer>
      </PageContentContainer>
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
