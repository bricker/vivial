import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";

import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

const Description = styled("div")<{ height: string }>(({ theme, height }) => ({
  position: "relative",
  color: theme.palette.grey[400],
  fontSize: rem(14),
  lineHeight: rem(17),
  overflow: "hidden",
  marginBottom: 8,
  height,
}));

const ExpandButtonContainer = styled("div")<{ isExpanded: boolean }>(({ theme, isExpanded }) => ({
  display: "inline",
  backgroundColor: theme.palette.background.paper,
  position: isExpanded ? "relative" : "absolute",
  bottom: 0,
  right: 0,
}));

const ExpandButton = styled(Button)(({ theme }) => ({
  color: theme.palette.accent[4],
  display: "inline",
  fontSize: rem(14),
  lineHeight: rem(17),
  fontWeight: 700,
  minWidth: 0,
  padding: 0,
  marginLeft: 5,
}));

const Ellipses = styled(Typography)(() => ({
  display: "inline",
  fontSize: rem(14),
  lineHeight: rem(17),
  marginLeft: 5,
}));

const LongDescription = ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const isLong = (children as string).length > 320;
  const height = isExpanded || !isLong ? "auto" : "68px";
  const cta = isExpanded ? "Read less" : "Read more";

  const toggleExpand = useCallback(() => {
    setIsExpanded(!isExpanded);
  }, [isExpanded]);

  return (
    <Description {...props} height={height}>
      {children}
      {isLong && (
        <ExpandButtonContainer isExpanded={isExpanded}>
          {!isExpanded && <Ellipses>...</Ellipses>}
          <ExpandButton onClick={toggleExpand}>{cta}</ExpandButton>
        </ExpandButtonContainer>
      )}
    </Description>
  );
};

export default LongDescription;
