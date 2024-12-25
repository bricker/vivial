import StarIcon from "$eave-dashboard/js/components/Icons/StarIcon";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React from "react";

const RatingContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "baseline",
}));

const Rating = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  lineHeight: rem(17),
  fontSize: "inherit",
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
  let ratingCounter = Math.round(rating * 2) / 2; // rating rounded to nearest .5
  for (let i = 0; i < 5; i++) {
    if (ratingCounter >= 1) {
      iterator.push(1);
      ratingCounter -= 1;
    } else if (ratingCounter === 0.5) {
      iterator.push(0.5);
      ratingCounter = 0;
    } else {
      iterator.push(0);
    }
  }
  return iterator;
}

interface RestaurantRatingProps extends React.HTMLAttributes<HTMLDivElement> {
  rating: number;
}

const RestaurantRating = ({ rating, ...props }: RestaurantRatingProps) => {
  return (
    <RatingContainer {...props}>
      <Rating>{rating}</Rating>
      <Stars>
        {starIterator(rating).map((starValue, i) => (
          <StarIcon key={i} half={starValue === 0.5} empty={starValue === 0} />
        ))}
      </Stars>
    </RatingContainer>
  );
};

export default RestaurantRating;
