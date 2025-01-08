import { chosePreferences, plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { Button, IconButton, styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, routePath, type NavigationState } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { useGetSearchRegionsQuery, usePlanOutingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { getBudgetLabel } from "$eave-dashboard/js/util/budget";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { getMultiRegionLabel, getRegionImage } from "$eave-dashboard/js/util/region";

import CheckIcon from "$eave-dashboard/js/components/Icons/CheckIcon";
import SearchIcon from "$eave-dashboard/js/components/Icons/SearchIcon";
import ShareIcon from "$eave-dashboard/js/components/Icons/ShareIcon";
import Modal from "$eave-dashboard/js/components/Modal";
import DateAreaSelections from "$eave-dashboard/js/components/Selections/DateAreaSelections";
import DateSelections from "$eave-dashboard/js/components/Selections/DateSelections";
import DateTimeSelections from "$eave-dashboard/js/components/Selections/DateTimeSelections";
import { colors } from "$eave-dashboard/js/theme/colors";
import { getDateTimeLabelExtended } from "$eave-dashboard/js/util/date";
import Typography from "@mui/material/Typography";
import LogisticsBadge from "./LogisticsBadge";

interface LogisticsSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  bgImgUrl?: string;
}

const Section = styled("section", {
  shouldForwardProp: (prop: string) => prop !== "bgImgUrl",
})<LogisticsSectionProps>(({ theme, bgImgUrl }) => ({
  position: "relative",
  backgroundImage: `url("${bgImgUrl}")`,
  backgroundSize: "cover",
  width: "100%",
  height: 181,
  marginBottom: 47,
  padding: "16px 24px",
  "&:after": {
    content: `""`,
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: theme.palette.common.black,
    opacity: 0.5,
  },
}));

const LogisticsGradient = styled("div")(() => ({
  background: "linear-gradient(90deg, rgba(208,138,0,1) 0%, rgba(230,240,37,1) 100%)",
  position: "relative",
  zIndex: 1,
  height: 62,
  width: "100%",
  borderRadius: 40,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const Logistics = styled("div")<{ viewOnly?: boolean }>(({ theme, viewOnly }) => ({
  backgroundColor: theme.palette.field.secondary,
  display: "flex",
  alignItems: "center",
  padding: viewOnly ? "12px 32px" : "12px 16px",
  height: 58,
  width: "calc(100% - 4px)",
  borderRadius: 40,
  cursor: viewOnly ? "auto" : "pointer",
  transition: "background-color 0.1s",
  "&:hover, &:focus": viewOnly
    ? undefined
    : {
        backgroundColor: colors.fieldBackground.primary,
      },
}));

const SearchButton = styled(IconButton)(() => ({
  backgroundColor: colors.fieldBackground.primary,
}));

const TimeAndPlace = styled("div")(() => ({
  marginLeft: 8,
}));

const Time = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(16),
  lineHeight: rem(19),
  fontWeight: 600,
  marginBottom: 4,
}));

const Place = styled(Typography)(({ theme }) => ({
  display: "flex",
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(15),
}));

const Region = styled("span")(() => ({
  display: "inline-block",
  height: rem(15),
  maxWidth: 164,
  overflow: "hidden",
  whiteSpace: "nowrap",
  textOverflow: "ellipsis",
  padding: "0 3px",
}));

const ButtonContainer = styled("div")(() => ({
  display: "flex",
  width: "100%",
  justifyContent: "flex-end",
  marginTop: 110,
}));

const ShareButton = styled(Button)(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  gap: 8,
  color: theme.palette.text.primary,
  textDecorationLine: "underline",
  marginRight: -16,
}));

const LogisticsSection = ({ viewOnly }: { viewOnly?: boolean }) => {
  const [planOuting, { data: planOutingData, isLoading: planOutingLoading }] = usePlanOutingMutation();
  const { data: searchRegionsData } = useGetSearchRegionsQuery({}, { skip: viewOnly });
  const outing = useSelector((state: RootState) => state.outing.details);

  const userPreferences = useSelector((state: RootState) => state.outing.preferenes.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferenes.partner);
  const [startTime, setStartTime] = useState(new Date());
  const [copied, setCopied] = useState(false);
  const [headcount, setHeadcount] = useState(2);
  const [replanDisabled, setReplanDisabled] = useState(true);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleReplan = useCallback(async () => {
    const groupPreferences = getPreferenceInputs(userPreferences, partnerPreferences);
    await planOuting({
      input: {
        startTime: startTime.toISOString(),
        groupPreferences,
        budget,
        headcount,
        searchAreaIds,
        isReroll: true,
      },
    });
  }, [userPreferences, partnerPreferences, budget, headcount, searchAreaIds, startTime]);

  const handleSelectHeadcount = useCallback((value: number) => {
    setHeadcount(value);
    setReplanDisabled(false);
  }, []);

  const handleSelectBudget = useCallback((value: OutingBudget) => {
    setBudget(value);
    setReplanDisabled(false);
  }, []);

  const handleSelectSearchAreas = useCallback((value: string[]) => {
    setSearchAreaIds(value);
    setAreasOpen(false);
    setReplanDisabled(false);
  }, []);

  const handleSelectStartTime = useCallback((value: Date) => {
    setStartTime(value);
    setDatePickerOpen(false);
    setReplanDisabled(false);
  }, []);

  const toggleDetailsOpen = useCallback(() => {
    setDetailsOpen(!detailsOpen);
  }, [detailsOpen]);

  const toggleAreasOpen = useCallback(() => {
    setAreasOpen(!areasOpen);
  }, [areasOpen]);

  const toggleDatePickerOpen = useCallback(() => {
    setDatePickerOpen(!datePickerOpen);
  }, [datePickerOpen]);

  useEffect(() => {
    setCopied(false);

    if (outing) {
      setStartTime(new Date(outing.startTime));
      setHeadcount(outing.headcount);

      if (outing.survey) {
        setSearchAreaIds(outing.survey.searchRegions.map((r) => r.id));
        setBudget(outing.survey.budget);
      }
    }
  }, [outing]);

  useEffect(() => {
    if (planOutingData) {
      if (planOutingData.planOuting?.__typename === "PlanOutingSuccess") {
        const updatedOuting = planOutingData.planOuting.outing;
        setDetailsOpen(false);
        dispatch(plannedOuting({ outing: updatedOuting }));
        dispatch(chosePreferences({ user: userPreferences }));

        const navigationState: NavigationState = { scrollBehavior: "smooth" };
        navigate(routePath(AppRoute.itinerary, { outingId: updatedOuting.id }), { state: navigationState });
      } else {
        setErrorMessage("There was an issue updating this outing. Reach out to friends@vivialapp.com for assistance.");
      }
    }
  }, [planOutingData, userPreferences, partnerPreferences]);

  const handleShareClick = useCallback(async () => {
    try {
      await navigator.share({
        title: "Vivial",
        text: "Check out this itinerary from Vivial!",
        url: window.location.href,
      });
    } catch {
      // share API likely not supported by browser; fallback to copy to clipboard
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => {
        setCopied(false);
      }, 5000);
    }
  }, []);

  if (!outing) {
    return null;
  }

  return (
    <Section bgImgUrl={getRegionImage(outing.searchRegions)}>
      <LogisticsGradient>
        <Logistics viewOnly={viewOnly} onClick={viewOnly ? undefined : toggleDetailsOpen}>
          {!viewOnly && (
            <SearchButton>
              <SearchIcon />
            </SearchButton>
          )}
          <TimeAndPlace>
            <Time>{getDateTimeLabelExtended(startTime)}</Time>
            <Place>
              For {headcount} •<Region>{getMultiRegionLabel(searchAreaIds)}</Region>• {getBudgetLabel(budget)}
            </Place>
          </TimeAndPlace>
        </Logistics>
      </LogisticsGradient>
      <LogisticsBadge startTime={startTime} connect={!!outing.reservation} />

      {!viewOnly && (
        <>
          <ButtonContainer>
            <ShareButton onClick={handleShareClick}>
              <Typography variant="body1">{copied ? "URL Copied!" : "Share"}</Typography>
              {copied ? <CheckIcon color="white" /> : <ShareIcon color="white" />}
            </ShareButton>
          </ButtonContainer>

          <Modal title="Date Details" onClose={toggleDetailsOpen} open={detailsOpen}>
            <DateSelections
              cta="Update"
              headcount={headcount}
              budget={budget}
              startTime={startTime}
              searchAreaIds={searchAreaIds}
              onSubmit={handleReplan}
              onSelectHeadcount={handleSelectHeadcount}
              onSelectBudget={handleSelectBudget}
              onSelectStartTime={toggleDatePickerOpen}
              onSelectSearchArea={toggleAreasOpen}
              errorMessage={errorMessage}
              disabled={replanDisabled}
              loading={planOutingLoading}
            />
          </Modal>
          <Modal title="Where in LA?" onClose={toggleAreasOpen} open={areasOpen}>
            <DateAreaSelections
              cta="Update"
              onSubmit={handleSelectSearchAreas}
              regions={searchRegionsData?.searchRegions}
            />
          </Modal>
          <Modal title="When is your date?" onClose={toggleDatePickerOpen} open={datePickerOpen}>
            <DateTimeSelections cta="Update" onSubmit={handleSelectStartTime} startDateTime={startTime} />
          </Modal>
        </>
      )}
    </Section>
  );
};

export default LogisticsSection;
