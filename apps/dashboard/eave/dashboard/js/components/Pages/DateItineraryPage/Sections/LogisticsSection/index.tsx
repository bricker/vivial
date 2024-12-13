import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useSelector } from "react-redux";

import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { RootState } from "$eave-dashboard/js/store";
import { useGetSearchRegionsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { getBackgroundImgUrl, getPlaceLabel, getTimeLabel } from "../../helpers";

import SettingsButton from "$eave-dashboard/js/components/Buttons/SettingsButton";
import Modal from "$eave-dashboard/js/components/Modal";
import DateAreaSelections from "$eave-dashboard/js/components/Selections/DateAreaSelections";
import DateSelections from "$eave-dashboard/js/components/Selections/DateSelections";
import DateTimeSelections from "$eave-dashboard/js/components/Selections/DateTimeSelections";
import Typography from "@mui/material/Typography";
import LogisticsBadge from "./LogisticsBadge";

interface LogisticsSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  bgImgUrl: string;
}

const Section = styled("section", {
  shouldForwardProp: (prop: string) => prop !== "bgImgUrl",
})<LogisticsSectionProps>(({ theme, bgImgUrl }) => ({
  position: "relative",
  backgroundImage: `url("${bgImgUrl}")`,
  backgroundSize: "cover",
  width: "100%",
  height: 181,
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

const Logistics = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.field.secondary,
  display: "flex",
  alignItems: "center",
  padding: "12px 16px",
  height: 58,
  width: "calc(100% - 4px)",
  borderRadius: 40,
}));

const TimeAndPlace = styled("div")(() => ({
  marginLeft: 8,
}));

const Time = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem("16px"),
  lineHeight: rem("19px"),
  fontWeight: 600,
  marginBottom: 4,
}));

const Place = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("12px"),
  lineHeight: rem("15px"),
}));

const LogisticsSection = () => {
  const { data: searchRegionsData } = useGetSearchRegionsQuery({});
  const outing = useSelector((state: RootState) => state.outing.details);
  const [startTime, setStartTime] = useState(new Date(outing?.restaurantArrivalTime || ""));
  const [headcount, setHeadcount] = useState(outing?.headcount || 2);
  const [replanDisabled, setReplanDisabled] = useState(true);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [areasOpen, setAreasOpen] = useState(false);
  const [datePickerOpen, setDatePickerOpen] = useState(false);

  // TODO: get budget from outing object (pending).
  // TODO: get search area Ids from outing object (pending).
  const [budget, setBudget] = useState(OutingBudget.Expensive);
  const [searchAreaIds, setSearchAreaIds] = useState<string[]>([
    "354c2020-6227-46c1-be04-6f5965ba452d",
    "94d05616-887a-440e-a2c5-c06ece510877",
  ]);

  const handleReplan = useCallback(async () => {
    // TODO: Replan outing.
  }, []);

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
    if (searchRegionsData?.searchRegions) {
      setSearchAreaIds(searchRegionsData.searchRegions.map((region) => region.id));
    }
  }, [searchRegionsData]);

  useEffect(() => {
    if (outing) {
      setStartTime(new Date(outing?.restaurantArrivalTime || ""));
      setHeadcount(outing?.headcount || 2);

      // TODO: get budget from outing object (pending).
      // TODO: get search area Ids from outing object (pending).
      setBudget(OutingBudget.Expensive);
      setSearchAreaIds(["354c2020-6227-46c1-be04-6f5965ba452d", "94d05616-887a-440e-a2c5-c06ece510877"]);
    }
  }, [outing]);

  if (outing) {
    return (
      <Section bgImgUrl={getBackgroundImgUrl(outing)}>
        <LogisticsGradient>
          <Logistics>
            <SettingsButton onClick={toggleDetailsOpen} />
            <TimeAndPlace>
              <Time>{getTimeLabel(startTime)}</Time>
              <Place>{getPlaceLabel(headcount, searchAreaIds, budget)}</Place>
            </TimeAndPlace>
          </Logistics>
        </LogisticsGradient>
        <LogisticsBadge startTime={startTime} />
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
            disabled={replanDisabled}
            loading={false}
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
  }
  return null;
};

export default LogisticsSection;
