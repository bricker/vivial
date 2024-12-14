import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import ExpandableSection from "../ExpandableSection";
import ActivityViewCondensed from "./ActivityViewCondensed";
import ActivityViewExpanded from "./ActivityViewExpanded";

const Section = styled(ExpandableSection)(() => ({
  marginBottom: 32,
}));

const ActivitySection = () => {
  const [expanded, setExpanded] = useState(false);
  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  return (
    <Section onExpand={toggleExpand} expanded={expanded}>
      {expanded ? <ActivityViewExpanded /> : <ActivityViewCondensed />}
    </Section>
  );
};

export default ActivitySection;
