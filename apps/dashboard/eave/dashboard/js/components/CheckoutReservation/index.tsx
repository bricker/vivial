import {
  SubmitReserverDetailsFailureReason,
  UpdateReserverDetailsFailureReason,
  type ItineraryFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { setBookingDetails } from "$eave-dashboard/js/store/slices/bookingSlice";
import {
  useConfirmBookingMutation,
  useInitiateBookingQuery,
  useListReserverDetailsQuery,
  useSubmitReserverDetailsMutation,
  useUpdateReserverDetailsMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { storeReserverDetails } from "$eave-dashboard/js/store/slices/reserverDetailsSlice";
import { colors } from "$eave-dashboard/js/theme/colors";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { myWindow } from "$eave-dashboard/js/types/window";
import { CircularProgress, Divider, Typography, styled } from "@mui/material";
import { Elements, useElements, useStripe } from "@stripe/react-stripe-js";
import { loadStripe, type Appearance, type CssFontSource, type CustomFontSource } from "@stripe/stripe-js";
import React, { FormEvent, useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import LoadingButton from "../Buttons/LoadingButton";
import CenteringContainer from "../CenteringContainer";
import InputError from "../Inputs/InputError";
import LogoPill, { logos } from "../LogoPill";
import Paper from "../Paper";
import CostBreakdown from "./CostBreakdown";
import PaymentForm from "./PaymentForm";
import ReservationDetailsForm, { ReserverFormFields } from "./ReservationDetailsForm";

const AltPageContainer = styled("div")(() => ({
  padding: "24px 16px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 32,
}));

const PaddedPrimaryButton = styled(LoadingButton)(() => ({
  width: "90%",
  alignSelf: "center",
  marginTop: 8,
}));

const PaddedCostBreakdown = styled(CostBreakdown)(() => ({
  padding: "24px 32px",
}));

const FormContainer = styled("form")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
  padding: "24px 16px",
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem(12),
  lineHeight: rem(16),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 8,
  padding: "0 16px",
}));

const FormPaper = styled(Paper)(({ theme }) => ({
  maxWidth: 450,
  [theme.breakpoints.down(Breakpoint.Medium)]: {
    padding: 24,
  },
}));

const PlainDiv = styled("div")(() => ({}));

const HeaderContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const FooterContainer = styled("div")(() => ({
  minWidth: 300,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 8,
}));

const FooterText = styled(Typography)(() => ({
  textAlign: "center",
}));

const TopDivider = styled(Divider)(({ theme }) => ({
  borderColor: theme.palette.primary.main,
}));

const ErrorText = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  textAlign: "center",
}));

function isPaidOuting(bookingDetails?: ItineraryFieldsFragment): boolean {
  if (!bookingDetails) {
    return false;
  }
  return bookingDetails.costBreakdown.totalCostCents > 0;
}

const CheckoutForm = ({
  showStripeBadge,
  showCostBreakdown,
}: {
  showStripeBadge?: boolean;
  showCostBreakdown?: boolean;
}) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  // https://docs.stripe.com/sdks/stripejs-react
  const stripeClient = useStripe();
  const stripeElements = useElements();

  const localReserverDetails = useSelector((state: RootState) => state.reserverDetails.reserverDetails);
  const bookingDetails = useSelector((state: RootState) => state.booking.bookingDetails);
  const account = useSelector((state: RootState) => state.auth.account);

  const { data: reserverDetailsData, isLoading: listDetailsIsLoading } = useListReserverDetailsQuery({});
  const [updateReserverDetails] = useUpdateReserverDetailsMutation();
  const [submitReserverDetails] = useSubmitReserverDetailsMutation();
  const [confirmBooking] = useConfirmBookingMutation();

  const [internalReserverDetailError, setInternalReserverDetailError] = useState<string | undefined>(undefined);
  const [externalReserverDetailError, setExternalReserverDetailError] = useState<string | undefined>(undefined);
  const [paymentError] = useState<string | undefined>(undefined);
  const [reserverDetails, setReserverDetails] = useState(
    localReserverDetails || { id: "", firstName: "", lastName: "", phoneNumber: "" },
  );

  const [submissionIsLoading, setSubmissionIsLoading] = useState(false);

  // only prevent submit on internalError since that can be fixed w/o another submit
  const submitButtonDisabled = !!(
    submissionIsLoading ||
    listDetailsIsLoading ||
    !reserverDetails.firstName ||
    !reserverDetails.lastName ||
    !reserverDetails.phoneNumber
  );
  const reserverDetailError = internalReserverDetailError || externalReserverDetailError;
  const error = [paymentError].filter((e) => e).join("\n");

  // set existing reservation details in form once we get them
  useEffect(() => {
    switch (reserverDetailsData?.viewer.__typename) {
      case "AuthenticatedViewerQueries": {
        // always prefer in-memory data (if available) over cached network resp
        if (!reserverDetails.id) {
          // NOTE: extracting and showing only the first one since we currently only
          // allow 1 reserverDetails row to be created
          const newDetails = reserverDetailsData?.viewer?.reserverDetails[0];
          if (newDetails) {
            setReserverDetails(newDetails);
          }
        }
        break;
      }
      case "UnauthenticatedViewer": {
        dispatch(loggedOut());
        window.location.assign(AppRoute.logout);
        break;
      }
      default: {
        break;
      }
    }
  }, [reserverDetailsData]);

  const handleReserverDetailChange = useCallback(
    (key: keyof ReserverFormFields, value: string) => {
      const newDetails = {
        ...reserverDetails,
        [key]: value,
      };
      setReserverDetails(newDetails);
      setInternalReserverDetailError(undefined);
    },
    [reserverDetails],
  );

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      if (!stripeClient || !stripeElements) {
        console.warn("stripe not loaded; must wrap in StripeElementsProvider");
        return;
      }
      setInternalReserverDetailError(undefined);
      setSubmissionIsLoading(true);

      try {
        if (bookingDetails?.reservation) {
          // if the reserver details dont have db ID yet, create a new entry
          if (reserverDetails.id.length === 0) {
            const submitDetailsResp = await submitReserverDetails({
              input: {
                firstName: reserverDetails.firstName,
                lastName: reserverDetails.lastName,
                phoneNumber: reserverDetails.phoneNumber,
              },
            });
            switch (submitDetailsResp.data?.viewer.__typename) {
              case "AuthenticatedViewerMutations": {
                const createdData = submitDetailsResp.data.viewer.submitReserverDetails;
                switch (createdData?.__typename) {
                  case "SubmitReserverDetailsSuccess": {
                    dispatch(storeReserverDetails({ details: createdData.reserverDetails }));
                    // allow success case to continue execution
                    break;
                  }
                  case "SubmitReserverDetailsFailure":
                    switch (createdData.failureReason) {
                      case SubmitReserverDetailsFailureReason.ValidationErrors: {
                        const invalidFields = createdData.validationErrors?.map((e) => e.field).join(", ");
                        setExternalReserverDetailError(`The following fields are invalid: ${invalidFields}`);
                        break;
                      }
                      default:
                        console.error("Unhandled case for SubmitReserverDetailsFailure", createdData.failureReason);
                        break;
                    }
                    return;
                  default:
                    console.error("Unexected Graphql result");
                    setSubmissionIsLoading(false);
                    return;
                }
                // allow success case to continue execution
                break;
              }
              case "UnauthenticatedViewer":
                dispatch(loggedOut());
                window.location.assign(AppRoute.logout);
                return;
              default:
                if (submitDetailsResp.error) {
                  // 500 error
                  console.error(submitDetailsResp.error);
                  setSubmissionIsLoading(false);
                  return;
                }
                break;
            }
          }
          // existing db entry needs to be updated
          else {
            const updateDetailsResp = await updateReserverDetails({
              input: {
                id: reserverDetails.id,
                firstName: reserverDetails.firstName,
                lastName: reserverDetails.lastName,
                phoneNumber: reserverDetails.phoneNumber,
              },
            });
            switch (updateDetailsResp.data?.viewer.__typename) {
              case "AuthenticatedViewerMutations": {
                const updatedData = updateDetailsResp.data.viewer.updateReserverDetails;
                switch (updatedData?.__typename) {
                  case "UpdateReserverDetailsSuccess":
                    dispatch(storeReserverDetails({ details: updatedData.reserverDetails }));
                    // allow success case to continue execution
                    break;
                  case "UpdateReserverDetailsFailure":
                    switch (updatedData.failureReason) {
                      case UpdateReserverDetailsFailureReason.ValidationErrors: {
                        const invalidFields = updatedData.validationErrors?.map((e) => e.field).join(", ");
                        setExternalReserverDetailError(`The following fields are invalid: ${invalidFields}`);
                        break;
                      }
                      default:
                        console.error("Unhandled case for UpdateReserverDetailsFailure", updatedData.failureReason);
                        break;
                    }
                    setSubmissionIsLoading(false);
                    return;
                  default:
                    console.error("Unexected Graphql result");
                    setSubmissionIsLoading(false);
                    return;
                }
                // allow success case to continue execution
                break;
              }
              case "UnauthenticatedViewer":
                dispatch(loggedOut());
                window.location.assign(AppRoute.logout);
                return;
              default:
                if (updateDetailsResp.error) {
                  // 500 error
                  console.error(updateDetailsResp.error);
                  setSubmissionIsLoading(false);
                  return;
                }
                break;
            }
          }
        }

        const returnPath = routePath({
          route: AppRoute.checkoutComplete,
          pathParams: { bookingId: bookingDetails!.id },
        });

        // execute the payment
        if (isPaidOuting(bookingDetails)) {
          const { error: confirmPaymentError } = await stripeClient.confirmPayment({
            elements: stripeElements,
            redirect: "if_required",
            confirmParams: {
              return_url: `${window.location.origin}${returnPath}`,
              save_payment_method: true,
              receipt_email: account?.email,
              payment_method_data: {
                allow_redisplay: "always",
              },
            },
          });

          if (confirmPaymentError) {
            setSubmissionIsLoading(false);
            console.error(confirmPaymentError.message, confirmPaymentError);
            setInternalReserverDetailError("There was an error submitting your payment.");
            return;
          }
        }

        const { data: confirmBookingData, error: confirmBookingError } = await confirmBooking({
          input: {
            bookingId: bookingDetails!.id,
          },
        });

        if (confirmBookingError || !confirmBookingData) {
          console.error(confirmBookingError);
          setInternalReserverDetailError("There was an error during booking.");
          setSubmissionIsLoading(false);
          return;
        }

        switch (confirmBookingData.viewer.__typename) {
          case "AuthenticatedViewerMutations": {
            switch (confirmBookingData.viewer.confirmBooking.__typename) {
              case "ConfirmBookingSuccess": {
                navigate(returnPath);
                break;
              }
              case "ConfirmBookingFailure": {
                console.error(`failure: ${confirmBookingData.viewer.confirmBooking.failureReason}`);
                setInternalReserverDetailError("There was an error during booking.");
                setSubmissionIsLoading(false);
                return;
              }
              default: {
                console.error("unexpected graphql response");
                setInternalReserverDetailError("There was an error during booking.");
                setSubmissionIsLoading(false);
                return;
              }
            }
            break;
          }
          case "UnauthenticatedViewer": {
            dispatch(loggedOut());
            window.location.assign(AppRoute.logout);
            return;
          }
          default: {
            console.error("unexpected graphql response");
            setInternalReserverDetailError("There was an error during booking.");
            setSubmissionIsLoading(false);
            return;
          }
        }
      } catch (e) {
        // network error
        console.error(e);
        setSubmissionIsLoading(false);
        setInternalReserverDetailError("Unable to book your outing. Please try again later.");
      }
    },
    [reserverDetails, stripeClient, stripeElements, bookingDetails],
  );

  const requiresPayment = isPaidOuting(bookingDetails);
  // when outing has been completely loaded into state & doesnt cost anything, use diff UI
  const usingAltUI = !requiresPayment;
  const Wrapper = usingAltUI ? FormPaper : PlainDiv;
  const PageContainer = usingAltUI ? AltPageContainer : PlainDiv;

  return (
    <PageContainer>
      {showCostBreakdown && requiresPayment && (
        <>
          <TopDivider />
          <PaddedCostBreakdown itinerary={bookingDetails!} />
        </>
      )}

      <Wrapper>
        {usingAltUI && (
          <HeaderContainer>
            <Typography variant="h2">Almost there!</Typography>
            <Typography variant="subtitle1">Submit your details to complete your reservation.</Typography>
          </HeaderContainer>
        )}
        <FormContainer onSubmit={handleSubmit}>
          <ReservationDetailsForm
            reserverDetails={reserverDetails}
            onChange={handleReserverDetailChange}
            error={reserverDetailError}
            isLoading={listDetailsIsLoading}
            showStripeBadge={showStripeBadge && requiresPayment}
          />

          {requiresPayment && <PaymentForm />}

          {error && (
            <InputErrorContainer>
              <InputError>{error}</InputError>
            </InputErrorContainer>
          )}

          <PaddedPrimaryButton type="submit" loading={submissionIsLoading} disabled={submitButtonDisabled}>
            Reserve
          </PaddedPrimaryButton>
        </FormContainer>
      </Wrapper>

      {usingAltUI && (
        <FooterContainer>
          <FooterText variant="body2">
            Reservations
            <br />
            powered by
          </FooterText>
          <LogoPill attrs={logos["opentable"]!} />
        </FooterContainer>
      )}
    </PageContainer>
  );
};

const stripePromise = loadStripe(myWindow.app.stripePublishableKey!);

const stripeElementsAppearance: Appearance = {
  theme: "night",
  labels: "floating",
  variables: {
    colorPrimary: colors.almostBlackBG,
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

const CheckoutFormStripeElementsProvider = ({ outingId }: { outingId: string }) => {
  const dispatch = useDispatch();

  const {
    data: initiateBookingData,
    isLoading: initiateBookingIsLoading,
    error: initiateBookingError,
  } = useInitiateBookingQuery({
    input: {
      outingId,
    },
  });

  useEffect(() => {
    if (
      initiateBookingData?.viewer.__typename === "AuthenticatedViewerMutations" &&
      initiateBookingData.viewer.initiateBooking.__typename === "InitiateBookingSuccess"
    ) {
      dispatch(setBookingDetails({ bookingDetails: initiateBookingData.viewer.initiateBooking.booking }));
    }
  }, [initiateBookingData]);

  if (initiateBookingIsLoading || !initiateBookingData) {
    return (
      <CenteringContainer>
        <CircularProgress color="secondary" />
      </CenteringContainer>
    );
  }

  const errorView = (
    <CenteringContainer>
      <ErrorText variant="h2">Unable to process payments right now. Please try again later.</ErrorText>
    </CenteringContainer>
  );

  if (initiateBookingError) {
    console.error(initiateBookingError);
    return errorView;
  }

  switch (initiateBookingData.viewer.__typename) {
    case "AuthenticatedViewerMutations": {
      break;
    }
    case "UnauthenticatedViewer": {
      console.error("unauthenticated user");
      dispatch(loggedOut());
      window.location.assign(AppRoute.logout);
      return;
    }
    default: {
      console.error("unexepected graphql response viewer type");
      return errorView;
    }
  }

  switch (initiateBookingData.viewer.initiateBooking.__typename) {
    case "InitiateBookingSuccess": {
      // Already handled in useEffect above
      break;
    }
    case "InitiateBookingFailure": {
      console.error(`failure: ${initiateBookingData.viewer.initiateBooking.failureReason}`);
      return errorView;
    }
    default: {
      console.error("unexepected graphql response InitiateBookingResult type");
      return errorView;
    }
  }

  let fonts: Array<CssFontSource | CustomFontSource> | undefined = undefined;

  // Get the CSS Font source from the <link> tag in the document header.
  const globalFontSrcElement = document.getElementById("global-font-src") as HTMLLinkElement;
  const fontUrl = globalFontSrcElement?.href;
  if (fontUrl) {
    fonts = [{ cssSrc: fontUrl }];
  }

  const clientSecret = initiateBookingData.viewer.initiateBooking.paymentIntent?.clientSecret;
  const customerSessionClientSecret = initiateBookingData.viewer.initiateBooking.customerSession?.clientSecret;

  return (
    <Elements
      stripe={stripePromise}
      options={{ clientSecret, customerSessionClientSecret, appearance: stripeElementsAppearance, fonts: fonts }}
    >
      <CheckoutForm showStripeBadge showCostBreakdown />
    </Elements>
  );
};

export default CheckoutFormStripeElementsProvider;
