import { RootState } from "$eave-dashboard/js/store";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import ImageCarousel from "$eave-dashboard/js/components/Carousels/ImageCarousel";
import BaseRestaurantBadge from "../../RestaurantBadge";

import { getRestaurantImgUrls } from "../../../../helpers";

const ViewContainer = styled("div")(() => ({
  position: "relative",
}));

const CarouselContainer = styled("div")(() => ({
  marginBottom: 16,
}));

const RestaurantBadge = styled(BaseRestaurantBadge)(() => ({
  position: "absolute",
  top: 0,
  left: 0,
}));

const ExpandedView = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const restaurant = outing?.restaurant;

  if (restaurant) {
    return (
      <ViewContainer>
        <RestaurantBadge />
        <CarouselContainer>
          <ImageCarousel imgUrls={getRestaurantImgUrls(restaurant)} />
        </CarouselContainer>
      </ViewContainer>
    );
  }
  return null;
};

export default ExpandedView;
