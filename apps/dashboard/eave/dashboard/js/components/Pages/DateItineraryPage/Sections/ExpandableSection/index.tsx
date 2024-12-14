import { styled } from "@mui/material";
import React from "react";

import BaseExpandButton from "$eave-dashboard/js/components/Buttons/ExpandButton";

const Section = styled("section")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  position: "relative",
  width: "calc(100% - 32px)",
  padding: "16px",
  margin: "0 16px",
  borderRadius: "15px",
  minHeight: 139,
}));

const ExpandButton = styled(BaseExpandButton)(() => ({
  position: "absolute",
  right: 9,
  bottom: -13,
}));

interface ExpandableSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  expanded: boolean;
  onExpand: () => void;
}

const ExpandableSection = ({ children, expanded, onExpand, ...props }: ExpandableSectionProps) => {
  return (
    <Section {...props}>
      {children}
      <ExpandButton onClick={onExpand} expanded={expanded} />
    </Section>
  );
};

export default ExpandableSection;
