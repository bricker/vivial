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
  usePlanOutingAnonymousMutation,
  usePlanOutingAuthenticatedMutation,
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

import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { useMobile } from "$eave-dashboard/js/util/mobile";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { MAX_REROLLS, useReroll } from "$eave-dashboard/js/util/reroll";
import LoadingButton from "../../Buttons/LoadingButton";
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
    minWidth: 415,
    alignSelf: "center",
  },
}));

const SubmitButton = styled(LoadingButton)(() => ({
  marginTop: 16,
}));

const Error = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginTop: 16,
  textAlign: "left",
}));

const DateSurveyPage = () => {
  const { data: outingPreferencesData } = useGetOutingPreferencesQuery({});
  const { data: searchRegionsData, isLoading: searchRegionsAreLoading } = useGetSearchRegionsQuery({});
  const [searchParams, _] = useSearchParams();
  const [planOutingAnon, { data: planOutingAnonData, isLoading: planOutingAnonLoading }] =
    usePlanOutingAnonymousMutation();
  const [planOutingAuth, { data: planOutingAuthData, isLoading: planOutingAuthLoading }] =
    usePlanOutingAuthenticatedMutation();
  const planOutingLoading = planOutingAnonLoading || planOutingAuthLoading;
  const [updatePreferences] = useUpdateOutingPreferencesMutation();
  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [headcount, setHeadcount] = useState(2);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const [startTime, setStartTime] = useState(getInitialStartTime());
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [outingPreferences, setOutingPreferences] = useState<OutingPreferencesSelections | null>(null);
  const [partnerPreferences, setPartnerPreferences] = useState<OutingPreferencesSelections | null>(null);
  const [outingPreferencesOpen, setOutingPreferencesOpen] = useState(false);
  const [partnerPreferencesOpen, setPartnerPreferencesOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [rerolls, rerolled] = useReroll();
  const isMobile = useMobile();

  const handleSubmit = useCallback(async () => {
    // checking for mobile layout bcus the mobile layout needs
    // to handle the reroll cookie on its own, but the desktop
    // layout relys on the DateSelections component to handle
    // that internally.
    if (!isLoggedIn && isMobile) {
      if (rerolls >= MAX_REROLLS) {
        navigate(AppRoute.signupMultiReroll);
        return;
      }
      rerolled();
    }
    const groupPreferences = getPreferenceInputs(outingPreferences, partnerPreferences);
    const input = {
      startTime: startTime.toISOString(),
      groupPreferences,
      budget,
      headcount,
      searchAreaIds,
    };
    if (isLoggedIn) {
      await planOutingAuth({ input });
    } else {
      await planOutingAnon({ input });
    }
  }, [outingPreferences, partnerPreferences, budget, headcount, searchAreaIds, startTime, rerolls, isMobile]);

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
    let outing = undefined;

    switch (planOutingAnonData?.planOuting?.__typename) {
      case "PlanOutingSuccess": {
        outing = planOutingAnonData.planOuting.outing;
        break;
      }
      case "PlanOutingFailure": {
        setErrorMessage("There was an issue planning your outing. Reach out to friends@vivialapp.com for assistance.");
        break;
      }
      default:
        break;
    }
    switch (planOutingAuthData?.viewer?.__typename) {
      case "AuthenticatedViewerMutations":
        switch (planOutingAuthData.viewer.planOuting.__typename) {
          case "PlanOutingSuccess": {
            outing = planOutingAuthData.viewer.planOuting.outing;
            break;
          }
          case "PlanOutingFailure": {
            setErrorMessage(
              "There was an issue planning your outing. Reach out to friends@vivialapp.com for assistance.",
            );
            break;
          }
          default:
            break;
        }
        break;
      case "UnauthenticatedViewer":
        dispatch(loggedOut());
        window.location.assign(AppRoute.logout);
        break;
      default:
        break;
    }

    if (outing) {
      dispatch(plannedOuting({ outing }));
      dispatch(
        chosePreferences({
          user: outingPreferences,
          partner: partnerPreferences,
        }),
      );
      navigate(routePath(AppRoute.itinerary, { outingId: outing.id }));
    }
  }, [planOutingAuthData, planOutingAnonData, outingPreferences, partnerPreferences]);

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
      return;
    }
    if (searchParams.get(SearchParam.variant) === DateSurveyPageVariant.PreferencesOpen) {
      setOutingPreferencesOpen(true);
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
          <TitleCopy variant="h1">Your Free Date Planner</TitleCopy>
          <CityCopy>🌴 Los Angeles, California</CityCopy>
          <Typography variant="subtitle1">
            We handle all the details, and you only pay for experiences you want to book.
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

          {isMobile && (
            <>
              <SubmitButton onClick={handleSubmit} loading={planOutingLoading} fullWidth>
                🎲 Pick my date
              </SubmitButton>
              {errorMessage && <Error>ERROR: {errorMessage}</Error>}
            </>
          )}
        </CopyContainer>
        <DateSurveyContainer>
          <DateSelections
            cta={!isMobile ? "🎲 Pick my date" : undefined}
            headcount={headcount}
            budget={budget}
            startTime={startTime}
            searchAreaIds={searchAreaIds}
            onSubmit={!isMobile ? handleSubmit : undefined}
            onSelectHeadcount={handleSelectHeadcount}
            onSelectBudget={handleSelectBudget}
            onSelectStartTime={toggleDatePickerOpen}
            onSelectSearchArea={toggleAreasOpen}
            errorMessage={!isMobile ? errorMessage : undefined}
            loading={!isMobile ? planOutingLoading : undefined}
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
