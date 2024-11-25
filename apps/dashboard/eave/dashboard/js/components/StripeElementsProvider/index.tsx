import { AppContext } from "$eave-dashboard/js/context";
import { myWindow } from "$eave-dashboard/js/types/window";
import { Elements } from "@stripe/react-stripe-js";
import { Appearance, CssFontSource, CustomFontSource, loadStripe } from "@stripe/stripe-js";
import React, { useContext, useEffect } from "react";

const stripePromise = loadStripe(myWindow.app.stripePublishableKey!);

const StripeElementsProvider = ({ children }: { children: React.ReactElement }) => {
  console.debug("StripeElementsProvider mounted");

  const { createPaymentIntentOperation } = useContext(AppContext)!;
  const [networkState] = createPaymentIntentOperation.networkState;

  useEffect(() => {
    console.debug("calling createPaymentIntent");

    void createPaymentIntentOperation.execute({
      input: {
        placeholder: "placeholder",
      },
    });
  }, []);

  if (networkState.loading) {
    return <div>Loading...</div>;
  }

  if (networkState.error || !networkState.data) {
    return <div>**DEVELOPMENT**: Error (createPaymentIntent mutation graphql errors)</div>;
  }

  if (networkState.data.viewer.__typename !== "AuthenticatedViewerMutations") {
    return <div>**DEVELOPMENT**: Error (Unauthenticated - TODO refresh token)</div>;
  }

  if (networkState.data.viewer.createPaymentIntent.__typename !== "CreatePaymentIntentSuccess") {
    return (
      <div>
        **DEVELOPMENT**: Error (mutation failure - {networkState.data.viewer.createPaymentIntent.failureReason})
      </div>
    );
  }

  const clientSecret = networkState.data.viewer.createPaymentIntent.paymentIntent.clientSecret;

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
