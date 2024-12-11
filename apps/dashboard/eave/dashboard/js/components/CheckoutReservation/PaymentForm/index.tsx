import { colors } from "$eave-dashboard/js/theme/colors";
import { Button as MuiButton, Typography, styled } from "@mui/material";
import { PaymentElement } from "@stripe/react-stripe-js";
import React from "react";
import EditIcon from "../../Icons/EditIcon";

const PaymentContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

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
  display: collapsed ? "none" : "flex",
  flexDirection: "column",
  gap: 8,
}));

const PaymentForm = ({
  paymentDetails,
  isUsingNewCard,
  setIsUsingNewCard,
}: {
  isUsingNewCard: boolean;
  setIsUsingNewCard: (newValue: boolean) => void;
  paymentDetails?: string;
}) => {
  // Testing? See here: https://docs.stripe.com/testing#cards
  // TL;DR: Number: 4242 4242 4242 4242; Exp: 10/30; Code: 123; Zip: 12345
  const titleText = `Payment info${paymentDetails ? ": " : "rmation"}`;
  return (
    <PaymentContainer>
      <HeaderContainer>
        <Typography variant="subtitle2">
          {titleText}
          {paymentDetails && <BoldText variant="subtitle2">{paymentDetails}</BoldText>}
        </Typography>
        {!isUsingNewCard && paymentDetails && (
          <TextButton onClick={() => setIsUsingNewCard(true)}>
            Add new
            <EditIcon color={colors.mediumPurpleAccent} />
          </TextButton>
        )}
        {isUsingNewCard && paymentDetails && (
          <TextButton onClick={() => setIsUsingNewCard(false)}>Use existing card</TextButton>
        )}
      </HeaderContainer>
      <CollapsingContainer collapsed={!!(paymentDetails && !isUsingNewCard)}>
        {isUsingNewCard && <Typography variant="subtitle2">New payment information</Typography>}
        <PaymentElement options={{}} />
      </CollapsingContainer>
    </PaymentContainer>
  );
};

export default PaymentForm;
