import { chosePreferences, plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import {
  useGetOutingPreferencesQuery,
  useGetSearchRegionsQuery,
  usePlanOutingMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { getRegionIds, getRegionImage } from "$eave-dashboard/js/util/region";
import { getPlaceLabel, getTimeLabel } from "../../helpers";

import SettingsButton from "$eave-dashboard/js/components/Buttons/SettingsButton";
import Modal from "$eave-dashboard/js/components/Modal";
import DateAreaSelections from "$eave-dashboard/js/components/Selections/DateAreaSelections";
import DateSelections from "$eave-dashboard/js/components/Selections/DateSelections";
import DateTimeSelections from "$eave-dashboard/js/components/Selections/DateTimeSelections";
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
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(15),
}));

const LogisticsSection = ({ viewOnly }: { viewOnly?: boolean }) => {
  const [planOuting, { data: planOutingData, isLoading: planOutingLoading }] = usePlanOutingMutation();
  const { data: outingPreferencesData } = useGetOutingPreferencesQuery({});
  const { data: searchRegionsData } = useGetSearchRegionsQuery({});
  const outing = useSelector((state: RootState) => state.outing.details);
  const userPreferences = useSelector((state: RootState) => state.outing.preferenes.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferenes.partner);
  const [startTime, setStartTime] = useState(new Date(outing?.restaurantArrivalTime || ""));
  const [headcount, setHeadcount] = useState(outing?.survey?.headcount || 2);
  const [replanDisabled, setReplanDisabled] = useState(true);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [budget, setBudget] = useState(outing?.survey?.budget || OutingBudget.Expensive);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>(getRegionIds(outing));
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleReplan = useCallback(async () => {
    const groupPreferences = getPreferenceInputs(
      userPreferences,
      partnerPreferences,
      outingPreferencesData?.activityCategoryGroups,
      outingPreferencesData?.restaurantCategories,
    );
    const input = {
      startTime: startTime.toISOString(),
      groupPreferences,
      budget,
      headcount,
      searchAreaIds,
    };
    await planOuting({ input });
  }, [outingPreferencesData, userPreferences, partnerPreferences, budget, headcount, searchAreaIds, startTime]);

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
    if (outing) {
      setStartTime(new Date(outing.restaurantArrivalTime || ""));
      setHeadcount(outing.survey?.headcount || 2);
      if (outing.survey) {
        setBudget(outing.survey.budget);
      }
      setSearchAreaIds(getRegionIds(outing));
    }
  }, [outing]);

  useEffect(() => {
    if (planOutingData) {
      if (planOutingData.planOuting?.__typename === "PlanOutingSuccess") {
        const updatedOuting = planOutingData.planOuting.outing;
        setDetailsOpen(false);
        dispatch(plannedOuting({ outing: updatedOuting }));
        dispatch(chosePreferences({ user: userPreferences }));
        navigate(`${AppRoute.itinerary}/${updatedOuting.id}`);
      } else {
        setErrorMessage("There was an issue updating this outing. Reach out to friends@vivialapp.com for assistance.");
      }
    }
  }, [planOutingData, userPreferences, partnerPreferences]);

  if (!outing) {
    return null;
  }

  return (
    <Section bgImgUrl={getRegionImage(outing.restaurant?.location.searchRegion.id)}>
      <LogisticsGradient>
        <Logistics viewOnly={viewOnly}>
          {!viewOnly && <SettingsButton onClick={toggleDetailsOpen} />}
          <TimeAndPlace>
            <Time>{getTimeLabel(startTime)}</Time>
            <Place>{getPlaceLabel(headcount, searchAreaIds, budget)}</Place>
          </TimeAndPlace>
        </Logistics>
      </LogisticsGradient>
      <LogisticsBadge startTime={startTime} connect={!!outing.restaurant} />
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
    </Section>
  );
};

export default LogisticsSection;
