import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { styled } from "@mui/material";
import React from "react";

const BadgeImg = styled("img")(() => ({
  height: rem(24),
  maxHeight: 32,
}));

const StripeBadge = () => {
  return <BadgeImg src={imageUrl("powered-by-stripe.png")} alt="powered by Stripe" />;
};

export default StripeBadge;
