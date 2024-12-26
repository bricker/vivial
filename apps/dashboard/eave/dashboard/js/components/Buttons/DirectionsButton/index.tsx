import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import React, { useCallback } from "react";
import DirectionsIcon from "../../Icons/DirectionsIcon";

const CustomButton = styled(IconButton)(() => ({
  border: "1px solid #8AB4F7", // one-off color
  borderRadius: 20,
  padding: "4px 8px",
}));

const CTA = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: rem(12),
  lineHeight: rem(15),
  marginLeft: 4,
}));

interface DirectionsButtonProps {
  uri: string;
}

const DirectionsButton = ({ uri }: DirectionsButtonProps) => {
  const handleClick = useCallback(() => {
    window.location.assign(uri);
  }, [uri]);

  return (
    <CustomButton onClick={handleClick}>
      <DirectionsIcon />
      <CTA>Directions</CTA>
    </CustomButton>
  );
};

export default DirectionsButton;
