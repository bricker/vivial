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
import React, { ReactNode, useCallback, useEffect, useRef, useState } from "react";
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

import { imageUrl } from "$eave-dashboard/js/util/asset";
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
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  gap: 16,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    flexDirection: "row",
  },
}));

const CopyContainer = styled(Paper)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    padding: "16px 0 0",
    background: "transparent",
    maxWidth: 426,
    boxShadow: "none",
  },
}));

const TitleCopy = styled(Typography)(({ theme }) => ({
  maxWidth: 250,
  color: theme.palette.text.primary,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    maxWidth: "none",
    marginBottom: 16,
  },
}));

const CityCopy = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(14),
  lineHeight: rem(18),
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    border: `1px solid ${theme.palette.primary.main}`,
    color: theme.palette.text.primary,
    display: "inline-block",
    borderRadius: "92.929px",
    fontSize: rem(18.586),
    lineHeight: rem(23),
    padding: "10px 20px",
    marginBottom: 16,
    fontWeight: 700,
  },
}));

const DateSurveyContainer = styled(Paper)(({ theme }) => ({
  marginTop: 8,
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
  marginTop: 8,
}));

const Error = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginTop: 8,
  textAlign: "left",
}));

const TextButton = styled(Button)(({ theme }) => ({
  fontFamily: fontFamilies.inter,
  textDecorationLine: "underline",
  alignSelf: "flex-end",
  color: theme.palette.text.secondary,
  fontWeight: 500,
}));

const AddPrefsContainer = styled(Paper)(({ theme }) => ({
  width: "100%",
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    maxWidth: 426,
  },
}));

const AddPrefsTitle = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
}));

const FadeInOutContainer = styled("div")(() => ({
  position: "relative",
  width: "100%",
  overflow: "hidden",
}));

const PrefsListContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  gap: 8,
  width: "100%",
  overflowX: "auto",
  padding: "4px 0px",
  scrollBehavior: "smooth",
}));

const PrefPill = styled(Typography, { shouldForwardProp: (prop) => prop !== "bgColor" })<{ bgColor: string }>(
  ({ bgColor, theme }) => ({
    backgroundColor: bgColor,
    color: theme.palette.common.black,
    padding: "8px 16px",
    whiteSpace: "nowrap",
    fontWeight: 600,
  }),
);

const AddPrefsButton = styled(Button)(({ theme }) => ({
  marginTop: 16,
  backgroundColor: theme.palette.background.default,
  borderStyle: "solid",
  borderColor: theme.palette.primary.main,
  borderWidth: 1,
  borderRadius: 100,
  color: theme.palette.primary.main,
  paddingTop: 16,
  paddingBottom: 16,
}));

enum FaderSide {
  Left,
  Right,
}

const Fader = ({ side, visible }: { side: FaderSide; visible: boolean }) => {
  const [r, g, b] = hexToRGB(colors.almostBlackBG);
  const style: { [key: string]: any } = {
    // zIndex: 1,
    position: "absolute",
    top: 0,
    bottom: 0,
    width: 15,
    display: visible ? "block" : "none",
    transition: "opacity 0.3s ease, transform 0.3s ease",
  };
  switch (side) {
    case FaderSide.Left:
      style["left"] = 0;
      style["background"] = `linear-gradient(to right, rgba(${r}, ${g}, ${b}, 1), rgba(${r}, ${g}, ${b}, 0))`;
      break;
    case FaderSide.Right:
      style["right"] = 0;
      style["background"] = `linear-gradient(to left, rgba(${r}, ${g}, ${b}, 1), rgba(${r}, ${g}, ${b}, 0))`;
      break;
    default:
      break;
  }
  return <div style={style} />;
};

const FadingScrollContainer = ({ children }: { children: ReactNode }) => {
  const scrollContainerRef = useRef(null);
  const [leftFaderVisible, setLeftFaderVisible] = useState(false);
  const [rightFaderVisible, setRightFaderVisible] = useState(true);

  const handleScroll = useCallback(() => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      if (scrollLeft === 0) {
        setLeftFaderVisible(false);
      } else if (scrollLeft + clientWidth === scrollWidth) {
        setRightFaderVisible(false);
      } else {
        setLeftFaderVisible(true);
        setRightFaderVisible(true);
      }
    }
  }, [scrollContainerRef]);

  return (
    <FadeInOutContainer>
      <PrefsListContainer ref={scrollContainerRef} onScroll={handleScroll}>
        <Fader side={FaderSide.Left} visible={leftFaderVisible} />
        {children}
        <Fader side={FaderSide.Right} visible={rightFaderVisible} />
      </PrefsListContainer>
    </FadeInOutContainer>
  );
};

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
        navigate(
          routePath({ route: AppRoute.signup, searchParams: { [SearchParam.variant]: SignUpPageVariant.MultiReroll } }),
        );
        return;
      }
      rerolled();
    }
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
