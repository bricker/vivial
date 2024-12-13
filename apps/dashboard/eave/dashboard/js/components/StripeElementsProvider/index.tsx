import { useCreatePaymentIntentMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { colors } from "$eave-dashboard/js/theme/colors";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { myWindow } from "$eave-dashboard/js/types/window";
import { CircularProgress, Typography, styled } from "@mui/material";
import { Elements } from "@stripe/react-stripe-js";
import { Appearance, CssFontSource, CustomFontSource, loadStripe } from "@stripe/stripe-js";
import React, { useEffect } from "react";

const CenteringContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "24px 40px",
}));

const ErrorText = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  textAlign: "center",
}));

const stripePromise = loadStripe(myWindow.app.stripePublishableKey!);

const StripeElementsProvider = ({ children }: { children: React.ReactElement }) => {
  const [createPaymentIntent, { isLoading, data }] = useCreatePaymentIntentMutation();

  useEffect(() => {
    void createPaymentIntent({
      input: {
        outingId: "", // FIXME
      },
    });
  }, []);

  const errorView = (
    <CenteringContainer>
      <ErrorText variant="h2">Unable to process payments right now. Please try again later.</ErrorText>
    </CenteringContainer>
  );

  if (isLoading) {
    return (
      <CenteringContainer>
        <CircularProgress color="secondary" />
      </CenteringContainer>
    );
  }

  if (!data) {
    return errorView;
  }

  switch (data.viewer.__typename) {
    case "AuthenticatedViewerMutations": {
      break;
    }
    case "UnauthenticatedViewer": {
      console.debug("ERROR: unauthenticated user");
      return errorView;
    }
    default: {
      console.debug("ERROR: unexepected graphql response viewer type");
      return errorView;
    }
  }

  switch (data.viewer.createPaymentIntent.__typename) {
    case "CreatePaymentIntentSuccess": {
      break;
    }
    case "CreatePaymentIntentFailure": {
      console.debug(`ERROR: mutation failure: ${data.viewer.createPaymentIntent.failureReason}`);
      return errorView;
    }
    default: {
      console.debug("ERROR: unexepected graphql response CreatePaymentIntentResult type");
      return errorView;
    }
  }

  const clientSecret = data.viewer.createPaymentIntent.paymentIntent.clientSecret;

  if (!clientSecret) {
    console.debug("ERROR: Payment Intent clientSecret missing");
    return errorView;
  }

  // Appearance API: https://docs.stripe.com/elements/appearance-api?platform=web
  const appearance: Appearance = {
    theme: "night",
    labels: "floating",
    variables: {
      fontFamily: `${fontFamilies.inter}, system-ui, sans-serif`,
      gridColumnSpacing: "0px",
      gridRowSpacing: "0px",
      borderRadius: "0px",
      colorBackground: colors.fieldBackground.primary,
      colorText: colors.whiteText,
    },
    rules: {
      ".Error": {
        paddingBottom: "8px",
      },
    },
  };

  let fonts: Array<CssFontSource | CustomFontSource> | undefined = undefined;

  // Get the CSS Font source from the <link> tag in the document header.
  const globalFontSrcElement = document.getElementById("global-font-src") as HTMLLinkElement;
  const fontUrl = globalFontSrcElement?.href;
  if (fontUrl) {
    fonts = [{ cssSrc: fontUrl }];
  }

  return (
    <Elements stripe={stripePromise} options={{ clientSecret, appearance, fonts: fonts }}>
      {children}
    </Elements>
  );
};

export default StripeElementsProvider;
