import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import ExpandableSection from "../ExpandableSection";
import RestaurantViewCondensed from "./RestaurantViewCondensed";
import RestaurantViewExpanded from "./RestaurantViewExpanded";

const Section = styled(ExpandableSection)(() => ({
  marginBottom: 32,
}));

const RestaurantSection = () => {
  const [expanded, setExpanded] = useState(false);
  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  return (
    <Section onExpand={toggleExpand} expanded={expanded}>
      {expanded ? <RestaurantViewExpanded /> : <RestaurantViewCondensed />}
    </Section>
  );
};

export default RestaurantSection;
