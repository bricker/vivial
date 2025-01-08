import { OutingBudget, PlanOutingInput } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, SearchParam, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";

import {
  useGetOutingPreferencesQuery,
  useGetSearchRegionsQuery,
  usePlanOutingAnonymousMutation,
  usePlanOutingAuthenticatedMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";

import {
  OutingPreferencesSelections,
  chosePreferences,
  plannedOuting,
} from "$eave-dashboard/js/store/slices/outingSlice";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { keyframes, styled } from "@mui/material";

import Typography from "@mui/material/Typography";

import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { MAX_REROLLS, useReroll } from "$eave-dashboard/js/util/reroll";
import LoadingButton from "../../Buttons/LoadingButton";
import ArrowRightIcon from "../../Icons/ArrowRightIcon";
import LoadingView from "./Views/LoadingView";
import { getInitialStartTime } from "./helpers";

const PageContainer = styled("div")(() => ({
  height: "100%",
  padding: "24px 16px",
}));

const PageContentContainer = styled("div")(() => ({
  height: "100%",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
}));

const CopyContainer = styled("div")(({ theme }) => ({
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
  color: theme.palette.text.primary,
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

const SubmitButton = styled(LoadingButton)(() => ({
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  marginTop: 16,
}));

const pulse = keyframes`
0% {
  transform: scale(1);
}
50% {
  transform: scale(1.2);
}
100% {
  transform: scale(1);
}
`;

const AnimatedDiv = styled("div")(() => ({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  animation: `${pulse} 2s linear infinite`,
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
  const budget = OutingBudget.Expensive;
  const headcount = 2;
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const startTime = getInitialStartTime();
  const [errorMessage, setErrorMessage] = useState("");
  const [outingPreferences, setOutingPreferences] = useState<OutingPreferencesSelections | null>(null);
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [rerolls, rerolled] = useReroll();

  const handleSubmit = useCallback(async () => {
    if (!isLoggedIn) {
      if (rerolls >= MAX_REROLLS) {
        navigate(AppRoute.signupMultiReroll);
        return;
      }
      rerolled();
    }
    const groupPreferences = getPreferenceInputs(outingPreferences, null);
    const input: PlanOutingInput = {
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
  }, [outingPreferences, budget, headcount, searchAreaIds, startTime, rerolls]);

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
        }),
      );
      navigate(routePath(AppRoute.itinerary, { outingId: outing.id }));
    }
  }, [planOutingAuthData, planOutingAnonData, outingPreferences]);

  useEffect(() => {
    if (searchRegionsData?.searchRegions) {
      setSearchAreaIds(searchRegionsData.searchRegions.map((region) => region.id));
    }
  }, [searchRegionsData]);

  useEffect(() => {
    const redirectPath = searchParams.get(SearchParam.redirect);
    if (redirectPath) {
      navigate(redirectPath);
      return;
    }
  }, [searchParams]);

  if (searchRegionsAreLoading) {
    return <LoadingView />;
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
          <SubmitButton onClick={handleSubmit} loading={planOutingLoading} fullWidth>
            <Typography variant="button">Plan my date</Typography>
            <AnimatedDiv>
              <ArrowRightIcon color="black" width={16} height={16} />
            </AnimatedDiv>
          </SubmitButton>
          {errorMessage && <Error>ERROR: {errorMessage}</Error>}
        </CopyContainer>
      </PageContentContainer>
    </PageContainer>
  );
};

export default DateSurveyPage;
