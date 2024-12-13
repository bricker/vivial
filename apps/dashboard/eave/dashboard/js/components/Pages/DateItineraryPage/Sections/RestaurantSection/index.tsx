import React, { useCallback, useState } from "react";
import ExpandableSection from "../ExpandableSection";
import CondensedView from "./Views/CondensedView";
import ExpandedView from "./Views/ExpandedView";

const RestaurantSection = () => {
  const [expanded, setExpanded] = useState(false);
  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  return (
    <ExpandableSection onExpand={toggleExpand} expanded={expanded}>
      {expanded ? <ExpandedView /> : <CondensedView />}
    </ExpandableSection>
  );
};

export default RestaurantSection;
