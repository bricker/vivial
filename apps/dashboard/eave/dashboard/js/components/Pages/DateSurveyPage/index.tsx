import {
  OutingBudget,
  type ActivityCategoryFieldsFragment,
  type RestaurantCategoryFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, DateSurveyPageVariant, SearchParam, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";

import {
  useGetOutingPreferencesQuery,
  useGetSearchRegionsQuery,
  usePlanOutingMutation,
  useUpdateOutingPreferencesMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";

import {
  chosePreferences,
  plannedOuting,
  type OutingPreferencesSelections,
} from "$eave-dashboard/js/store/slices/outingSlice";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import Typography from "@mui/material/Typography";
import Modal from "../../Modal";
import Paper from "../../Paper";
import DateAreaSelections from "../../Selections/DateAreaSelections";
import DateSelections from "../../Selections/DateSelections";
import DateTimeSelections from "../../Selections/DateTimeSelections";
import EditPreferencesOption from "./Options/EditPreferencesOption";
import LoadingView from "./Views/LoadingView";
import PreferencesView from "./Views/PreferencesView";

import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { getInitialStartTime } from "./helpers";

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
  fontSize: rem(14),
  lineHeight: rem(18),
  marginBottom: 8,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    border: `1px solid ${theme.palette.primary.main}`,
    color: theme.palette.text.primary,
    display: "inline-block",
    borderRadius: "92.929px",
    fontSize: rem(18.586),
    lineHeight: rem(23),
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
  const { data: outingPreferencesData } = useGetOutingPreferencesQuery({});
  const { data: searchRegionsData, isLoading: searchRegionsAreLoading } = useGetSearchRegionsQuery({});
  const [searchParams, _] = useSearchParams();
  const [planOuting, { data: planOutingData, isLoading: planOutingLoading }] = usePlanOutingMutation();

  const [updatePreferences] = useUpdateOutingPreferencesMutation();
  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [headcount, setHeadcount] = useState(2);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const [startTime, setStartTime] = useState(getInitialStartTime());
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [outingPreferences, setOutingPreferences] = useState<OutingPreferencesSelections | null>(null);
  const [partnerPreferences, setPartnerPreferences] = useState<OutingPreferencesSelections | null>(null);
  const [outingPreferencesOpen, setOutingPreferencesOpen] = useState(
    searchParams.get(SearchParam.variant) === DateSurveyPageVariant.PreferencesOpen,
  );
  const [partnerPreferencesOpen, setPartnerPreferencesOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleSubmit = useCallback(async () => {
    const groupPreferences = getPreferenceInputs(outingPreferences, partnerPreferences);
    await planOuting({
      input: {
        startTime: startTime.toISOString(),
        groupPreferences,
        budget,
        headcount,
        searchAreaIds,
      },
    });
  }, [outingPreferences, partnerPreferences, budget, headcount, searchAreaIds, startTime]);

  const handleSubmitPreferences = useCallback(async (selections: OutingPreferencesSelections) => {
    setOutingPreferences(selections);
    await updatePreferences({
      input: {
        restaurantCategoryIds: selections.restaurantCategories?.map((c) => c.id),
        activityCategoryIds: selections.activityCategories?.map((c) => c.id),
      },
    });
  }, []);

  const handlePartnerPreferences = useCallback((selections: OutingPreferencesSelections) => {
    setPartnerPreferences(selections);
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
    if (planOutingData) {
      if (planOutingData.planOuting?.__typename === "PlanOutingSuccess") {
        const outing = planOutingData.planOuting.outing;
        dispatch(plannedOuting({ outing }));
        dispatch(
          chosePreferences({
            user: outingPreferences,
            partner: partnerPreferences,
          }),
        );
        navigate(routePath(AppRoute.itinerary, { outingId: outing.id }));
      } else {
        setErrorMessage("There was an issue planning your outing. Reach out to friends@vivialapp.com for assistance.");
      }
    }
  }, [planOutingData, outingPreferences, partnerPreferences]);

  useEffect(() => {
    if (searchRegionsData?.searchRegions) {
      setSearchAreaIds(searchRegionsData.searchRegions.map((region) => region.id));
    }
  }, [searchRegionsData]);

  useEffect(() => {
    const viewer = outingPreferencesData?.viewer;
    if (viewer?.__typename === "AuthenticatedViewerQueries") {
      const preferences = viewer.outingPreferences;
      if (preferences.activityCategories || preferences.restaurantCategories) {
        setOutingPreferences({
          restaurantCategories: preferences.restaurantCategories as RestaurantCategoryFieldsFragment[],
          activityCategories: preferences.activityCategories as ActivityCategoryFieldsFragment[],
        });
      }
    }
  }, [outingPreferencesData]);

  useEffect(() => {
    const redirectPath = searchParams.get(SearchParam.redirect);
    if (redirectPath) {
      navigate(redirectPath);
    }
  }, [searchParams]);

  if (searchRegionsAreLoading) {
    return <LoadingView />;
  }

  if (isLoggedIn) {
    if (outingPreferencesOpen) {
      return (
        <PreferencesView
          title="Get personalized recommendations"
          subtitle="Your saved preferences are used to make more personalized recommendations."
          outingPreferences={outingPreferences}
          onSubmit={handleSubmitPreferences}
          onClose={() => setOutingPreferencesOpen(false)}
        />
      );
    }
    if (partnerPreferencesOpen) {
      return (
        <PreferencesView
          title="Add partner preferences"
          subtitle="We’ll use your saved preferences and your partner preferences to make recommendations."
          outingPreferences={partnerPreferences}
          onSubmit={handlePartnerPreferences}
          onClose={() => setPartnerPreferencesOpen(false)}
        />
      );
    }
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
          {isLoggedIn && (
            <>
              <EditPreferencesOption
                label="Your preferences"
                editable={!outingPreferences}
                onClickEdit={() => setOutingPreferencesOpen(true)}
              />
              {headcount === 2 && (
                <EditPreferencesOption
                  label="Partner preferences (optional)"
                  editable={!partnerPreferences}
                  onClickEdit={() => setPartnerPreferencesOpen(true)}
                />
              )}
            </>
          )}
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
            errorMessage={errorMessage}
            loading={planOutingLoading}
          />
        </DateSurveyContainer>
      </PageContentContainer>
      <Modal title="Where in LA?" onClose={toggleAreasOpen} open={areasOpen}>
        <DateAreaSelections cta="Save" onSubmit={handleSelectSearchAreas} regions={searchRegionsData?.searchRegions} />
      </Modal>
      <Modal title="When is your date?" onClose={toggleDatePickerOpen} open={datePickerOpen}>
        <DateTimeSelections cta="Save" onSubmit={handleSelectStartTime} startDateTime={startTime} />
      </Modal>
    </PageContainer>
  );
};

export default DateSurveyPage;
