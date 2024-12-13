import StarIcon from "$eave-dashboard/js/components/Icons/StarIcon";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React from "react";

const RatingContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "baseline",
}));

const Rating = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: "inherit",
  lineHeight: "inherit",
  fontWeight: 500,
  marginRight: 5,
}));

const Stars = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
  width: 73,
}));

function starIterator(rating: number): number[] {
  const iterator: number[] = [];
  let counter = Math.round(rating * 2) / 2; // rating rounded to nearest .5
  while (counter >= 1) {
    counter -= 1;
    iterator.push(1);
  }
  if (counter) {
    iterator.push(counter);
  }
  return iterator;
}

const RestaurantRating = ({ rating }: { rating: number }) => {
  return (
    <RatingContainer>
      <Rating>{rating}</Rating>
      <Stars>
        {starIterator(rating).map((starValue, i) => (
          <StarIcon key={i} half={starValue === 0.5} />
        ))}
      </Stars>
    </RatingContainer>
  );
};

export default RestaurantRating;
