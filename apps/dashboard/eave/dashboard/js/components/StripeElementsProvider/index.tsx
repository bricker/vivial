import { useCreatePaymentIntentMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { myWindow } from "$eave-dashboard/js/types/window";
import { Elements } from "@stripe/react-stripe-js";
import { Appearance, CssFontSource, CustomFontSource, loadStripe } from "@stripe/stripe-js";
import React, { useEffect } from "react";

const stripePromise = loadStripe(myWindow.app.stripePublishableKey!);

const StripeElementsProvider = ({ children }: { children: React.ReactElement }) => {
  const [createPaymentIntent, { isLoading, data }] = useCreatePaymentIntentMutation();

  useEffect(() => {
    void createPaymentIntent({});
  });

  if (isLoading) {
    return <div>**DEVELOPMENT**: Loading</div>;
  }

  if (!data) {
    return <div>**DEVELOPMENT**: Error (graphql response no data)</div>;
  }

  switch (data.viewer.__typename) {
    case "AuthenticatedViewerMutations": {
      break;
    }
    case "UnauthenticatedViewer": {
      return <div>**DEVELOPMENT**: Error (unauthenticated user)</div>;
    }
    default: {
      return <div>**DEVELOPMENT**: Error (graphql unexpected response type)</div>;
    }
  }

  switch (data.viewer.createPaymentIntent.__typename) {
    case "CreatePaymentIntentSuccess": {
      break;
    }
    case "CreatePaymentIntentFailure": {
      return <div>**DEVELOPMENT**: Error (mutation failure - {data.viewer.createPaymentIntent.failureReason})</div>;
    }
    default: {
      return <div>**DEVELOPMENT**: Error (graphql unexpected response type)</div>;
    }
  }

  const clientSecret = data.viewer.createPaymentIntent.paymentIntent.clientSecret;

  if (!clientSecret) {
    return <div>**DEVELOPMENT** Error (Payment Intent clientSecret missing)</div>;
  }

  // Appearance API: https://docs.stripe.com/elements/appearance-api?platform=web
  const appearance: Appearance = {
    theme: "night", // This is a pre-built theme to use as the base
    variables: {
      // fontFamily: "TODO Leilenah",
      // colorPrimary: "TODO Leilenabh",
      // colorText: "TODO Leilenah",
      // ...etc, there are many options
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
