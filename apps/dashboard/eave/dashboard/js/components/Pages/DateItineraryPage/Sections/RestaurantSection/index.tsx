import { RootState } from "$eave-dashboard/js/store";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useSelector } from "react-redux";

import ExpandableSection from "../ExpandableSection";
import RestaurantViewCondensed from "./RestaurantViewCondensed";
import RestaurantViewExpanded from "./RestaurantViewExpanded";

const Section = styled(ExpandableSection)(() => ({
  marginBottom: 32,
}));

const RestaurantSection = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const [expanded, setExpanded] = useState(true);
  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  if (!outing?.reservation) {
    return null;
  }

  return (
    <Section onExpand={toggleExpand} expanded={expanded}>
      {expanded ? <RestaurantViewExpanded /> : <RestaurantViewCondensed />}
    </Section>
  );
};

export default RestaurantSection;
