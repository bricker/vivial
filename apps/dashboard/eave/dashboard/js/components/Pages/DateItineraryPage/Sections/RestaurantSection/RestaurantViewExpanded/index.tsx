import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import DirectionsButton from "$eave-dashboard/js/components/Buttons/DirectionsButton";
import TooltipButton from "$eave-dashboard/js/components/Buttons/TooltipButton";
import ImageCarousel from "$eave-dashboard/js/components/Carousels/ImageCarousel";
import Typography from "@mui/material/Typography";
import BaseRestaurantBadge from "../RestaurantBadge";
import BaseRestaurantRating from "../RestaurantRating";

import { getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getImgUrls } from "../../../helpers";

import { RESERVATION_WARNING } from "../constant";

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

const InfoContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
  marginBottom: 16,
}));

const ReservationInfo = styled("div")(() => ({
  paddingRight: 16,
}));

const TimeAndTableInfo = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  marginBottom: 8,
}));

const TimeAndTable = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(16),
  lineHeight: rem(18),
  fontWeight: 600,
  marginRight: 7,
}));

const RestaurantName = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(16),
  lineHeight: rem(19),
  marginBottom: 8,
}));

const RestaurantAddress = styled(Typography)(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem(10),
  lineHeight: rem(12),
}));

const ExtraInfo = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
}));

const RestaurantRating = styled(BaseRestaurantRating)(() => ({
  fontSize: rem(14),
  height: 17,
  marginBottom: 8,
}));

const RestaurantType = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(15),
  marginBottom: 8,
}));

const RestaurantDesc = styled(Typography)(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem(14),
  lineHeight: rem(17),
  marginBottom: 8,
}));

const RestaurantViewExpanded = () => {
  const outing = useSelector((state: RootState) => state.outing.details);

  if (!outing || !outing.reservation) {
    return null;
  }

  const restaurant = outing.reservation.restaurant;
  const arrivalTime = new Date(outing.reservation.arrivalTime);
  const address = restaurant.location.address;
  const directionsUri = restaurant.location.directionsUri;

  return (
    <ViewContainer>
      <RestaurantBadge />
      <CarouselContainer>
        <ImageCarousel imgUrls={getImgUrls(restaurant.photos)} />
      </CarouselContainer>
      <InfoContainer>
        <ReservationInfo>
          <TimeAndTableInfo>
            <TimeAndTable>
              {getTimeOfDay(arrivalTime, false)}
              {outing.reservation.restaurant.reservable ? ` | Table for ${outing.reservation.headcount}` : null}
            </TimeAndTable>
            <TooltipButton info={RESERVATION_WARNING} iconColor={colors.lightOrangeAccent} iconLarge />
          </TimeAndTableInfo>
          <RestaurantName>{restaurant.name}</RestaurantName>
          {address && (
            <div>
              <RestaurantAddress>
                {address.address1} {address.address2}
              </RestaurantAddress>
              <RestaurantAddress>
                {[address.city, address.state, address.zipCode].filter((k) => k).join(", ")}
              </RestaurantAddress>
            </div>
          )}
        </ReservationInfo>
        <ExtraInfo>
          <RestaurantRating rating={restaurant.rating} />
          <RestaurantType>{restaurant.primaryTypeName}</RestaurantType>
          {directionsUri && <DirectionsButton uri={directionsUri} />}
        </ExtraInfo>
      </InfoContainer>
      <RestaurantDesc>{restaurant.description}</RestaurantDesc>
      {restaurant.parkingTips && <RestaurantDesc>🚘 Parking Tips: {restaurant.parkingTips}</RestaurantDesc>}
      {restaurant.customerFavorites && (
        <RestaurantDesc>🍲 Customer favorites: {restaurant.customerFavorites}</RestaurantDesc>
      )}
    </ViewContainer>
  );
};

export default RestaurantViewExpanded;
