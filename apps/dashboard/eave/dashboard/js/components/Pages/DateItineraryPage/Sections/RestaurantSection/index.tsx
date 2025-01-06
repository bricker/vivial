import { RootState } from "$eave-dashboard/js/store";
import { Button, Typography, styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useSelector } from "react-redux";

import CheckIcon from "$eave-dashboard/js/components/Icons/CheckIcon";
import ShareIcon from "$eave-dashboard/js/components/Icons/ShareIcon";
import ExpandableSection from "../ExpandableSection";
import RestaurantViewCondensed from "./RestaurantViewCondensed";
import RestaurantViewExpanded from "./RestaurantViewExpanded";

const Section = styled(ExpandableSection)(() => ({
  marginBottom: 32,
}));

const ShareButton = styled(Button)(({ theme }) => ({
  alignSelf: "flex-end",
  display: "flex",
  flexDirection: "row",
  gap: 8,
  color: theme.palette.text.primary,
  textDecorationLine: "underline",
  marginRight: 16,
}));

const Container = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
}));

const RestaurantSection = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const [expanded, setExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const toggleExpand = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded]);

  const handleShareClick = useCallback(async () => {
    try {
      await navigator.share({
        title: "Vivial",
        text: "Check out this itinerary from Vivial!",
        url: window.location.href,
      });
    } catch (error) {
      // fallback to copy to clipboard
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    }
  }, []);

  if (!outing?.reservation) {
    return null;
  }

  return (
    <Container>
      <ShareButton onClick={handleShareClick}>
        <Typography variant="body1">{copied ? "URL Copied!" : "Share"}</Typography>
        {copied ? <CheckIcon color="white" /> : <ShareIcon color="white" />}
      </ShareButton>
      <Section onExpand={toggleExpand} expanded={expanded}>
        {expanded ? <RestaurantViewExpanded /> : <RestaurantViewCondensed />}
      </Section>
    </Container>
  );
};

export default RestaurantSection;
