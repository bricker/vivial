import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getTimeOfDay } from "$eave-dashboard/js/util/date";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import TooltipButton from "$eave-dashboard/js/components/Buttons/TooltipButton";
import Typography from "@mui/material/Typography";
import RestaurantBadge from "../RestaurantBadge";
import BaseRestaurantRating from "../RestaurantRating";

import { RESERVATION_WARNING } from "../constant";

const ViewContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
}));

const ImgContainer = styled("div")(() => ({
  height: 102,
  width: 184,
  minWidth: 184,
  overflow: "hidden",
  borderRadius: 10,
  marginLeft: 16,
}));

const Img = styled("img")(() => ({
  objectFit: "cover",
  minHeight: "100%",
  width: "100%",
}));

const CopyContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  marginBottom: 12,
}));

const TimeAndTableInfo = styled("div")(() => ({
  marginLeft: 9,
}));

const TimeInfo = styled("div")(() => ({
  display: "flex",
}));

const Time = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  marginRight: 4,
  fontSize: rem(16),
  lineHeight: rem(19),
  fontWeight: 600,
}));

const TableInfo = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontsize: rem(14),
  lineHeight: rem(17),
}));

const RestaurantRating = styled(BaseRestaurantRating)(() => ({
  fontSize: rem(12),
  height: 15,
}));

const RestaurantName = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(14),
  lineHeight: rem(17),
  marginBottom: 4,
}));

const RestaurantType = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(15),
  marginBottom: 4,
}));

const RestaurantViewCondensed = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  if (!outing || !outing.reservation) {
    return null;
  }

  const arrivalTime = new Date(outing.reservation.arrivalTime);
  const restaurant = outing.reservation.restaurant;

  return (
    <ViewContainer>
      <div>
        <CopyContainer>
          <RestaurantBadge />
          <TimeAndTableInfo>
            <TimeInfo>
              <Time>{getTimeOfDay(arrivalTime, false)}</Time>
              <TooltipButton info={RESERVATION_WARNING} iconColor={colors.lightOrangeAccent} />
            </TimeInfo>
            {outing.reservation.restaurant.reservable && (
              <TableInfo>Table for {outing.reservation.headcount}</TableInfo>
            )}
          </TimeAndTableInfo>
        </CopyContainer>
        <div>
          <RestaurantName>{restaurant.name}</RestaurantName>
          <RestaurantType>{restaurant.primaryTypeName}</RestaurantType>
          <RestaurantRating rating={restaurant.rating} />
        </div>
      </div>
      {restaurant.photos.coverPhoto && (
        <ImgContainer>
          <Img src={restaurant.photos.coverPhoto.src} />
        </ImgContainer>
      )}
    </ViewContainer>
  );
};

export default RestaurantViewCondensed;
