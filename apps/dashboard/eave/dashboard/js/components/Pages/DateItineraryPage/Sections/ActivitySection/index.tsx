import { RootState } from "$eave-dashboard/js/store";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useSelector } from "react-redux";

import ExpandableSection from "../ExpandableSection";
import ActivityViewCondensed from "./ActivityViewCondensed";
import ActivityViewExpanded from "./ActivityViewExpanded";

const Section = styled(ExpandableSection)(() => ({
  marginBottom: 32,
}));

const ActivitySection = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const [expanded, setExpanded] = useState(false);
  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  if (outing?.activity) {
    return (
      <Section onExpand={toggleExpand} expanded={expanded}>
        {expanded ? <ActivityViewExpanded /> : <ActivityViewCondensed />}
      </Section>
    );
  }
  return null;
};

export default ActivitySection;
