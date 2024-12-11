import { colors } from "$eave-dashboard/js/theme/colors";
import { Button as MuiButton, Typography, styled } from "@mui/material";
import { PaymentElement } from "@stripe/react-stripe-js";
import React, { useState } from "react";
import EditIcon from "../../Icons/EditIcon";

const PaymentContainer = styled("div")(() => ({}));

const BoldText = styled(Typography)(() => ({
  display: "inline",
  fontWeight: "bold",
}));

const TextButton = styled(MuiButton)(() => ({
  color: colors.mediumPurpleAccent,
}));

const HeaderContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
}));

const CollapsingContainer = styled("div")<{ collapsed: boolean }>(({ collapsed }) => ({
  display: collapsed ? "none" : "auto",
}));

const PaymentForm = ({ paymentDetails }: { paymentDetails?: string }) => {
  const [isEditing, setIsEditing] = useState(false);
  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  const titleText = `Payment info${paymentDetails ? ":" : "rmation"}`;
  return (
    <PaymentContainer>
      <HeaderContainer>
        <Typography variant="subtitle2">
          {titleText}
          {paymentDetails && <BoldText variant="subtitle2">{paymentDetails}</BoldText>}
        </Typography>
        {!isEditing && paymentDetails && (
          <TextButton onClick={() => setIsEditing(true)}>
            Add new
            <EditIcon color={colors.mediumPurpleAccent} />
          </TextButton>
        )}
        {isEditing && paymentDetails && <TextButton onClick={() => setIsEditing(false)}>Cancel</TextButton>}
      </HeaderContainer>
      <CollapsingContainer collapsed={!!(paymentDetails && !isEditing)}>
        <PaymentElement options={{}} />
      </CollapsingContainer>
    </PaymentContainer>
  );
};

export default PaymentForm;
