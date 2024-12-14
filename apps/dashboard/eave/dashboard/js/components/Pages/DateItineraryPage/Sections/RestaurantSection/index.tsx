import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import ExpandableSection from "../ExpandableSection";
import CondensedView from "./Views/CondensedView";
import ExpandedView from "./Views/ExpandedView";

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
      {expanded ? <ExpandedView /> : <CondensedView />}
    </Section>
  );
};

export default RestaurantSection;
