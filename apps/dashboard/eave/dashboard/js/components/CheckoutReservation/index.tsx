import {
  CreateBookingFailureReason,
  Outing,
  SubmitReserverDetailsFailureReason,
  UpdateReserverDetailsFailureReason,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import {
  useCreateBookingMutation,
  useGetOutingAuthenticatedQuery,
  useListReserverDetailsQuery,
  useSubmitReserverDetailsMutation,
  useUpdateReserverDetailsMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { storeReserverDetails } from "$eave-dashboard/js/store/slices/reserverDetailsSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import { useElements, useStripe } from "@stripe/react-stripe-js";
import React, { FormEvent, useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import LoadingButton from "../Buttons/LoadingButton";
import InputError from "../Inputs/InputError";
import StripeElementsProvider from "../StripeElementsProvider";
import PaymentForm from "./PaymentForm";
import ReservationDetailsForm, { ReserverFormFields } from "./ReservationDetailsForm";

const PaddedPrimaryButton = styled(LoadingButton)(() => ({
  width: "90%",
  alignSelf: "center",
  marginBottom: 56,
}));

const FormContainer = styled("form")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
  padding: "24px 16px",
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 24,
  padding: "0 16px",
}));

function hasPaidActivity(outing: Outing | null) {
  const costData = outing?.activity?.ticketInfo;
  return costData?.cost || costData?.fee || costData?.tax;
}
const CheckoutForm = ({ outingId, showStripeBadge = false }: { outingId: string; showStripeBadge?: boolean }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  // https://docs.stripe.com/sdks/stripejs-react
  const stripeClient = useStripe();
  const stripeElements = useElements();

  const localOuting = useSelector((state: RootState) => state.outing.details);
  const localReserverDetails = useSelector((state: RootState) => state.reserverDetails.reserverDetails);

  const {
    data: reserverDetailsData,
    isLoading: listDetailsIsLoading,
    isError: listDetailsIsError,
  } = useListReserverDetailsQuery({});
  const {
    data: outingData,
    isLoading: outingIsLoading,
    isError: outingIsError,
  } = useGetOutingAuthenticatedQuery({ input: { id: outingId } });
  const [updateReserverDetails, { isLoading: updateDetailsIsLoading }] = useUpdateReserverDetailsMutation();
  const [createBooking, { isLoading: createBookingIsLoading }] = useCreateBookingMutation();
  const [submitReserverDetails, { isLoading: submitDetailsIsLoading }] = useSubmitReserverDetailsMutation();

  const [internalReserverDetailError, setInternalReserverDetailError] = useState<string | undefined>(undefined);
  const [externalReserverDetailError, setExternalReserverDetailError] = useState<string | undefined>(undefined);
  const [paymentError, setPaymentError] = useState<string | undefined>(undefined);
  const [bookingError, setBookingError] = useState<string | undefined>(undefined);
  const [isUsingNewCard, setIsUsingNewCard] = useState(false);
  const [reserverDetails, setReserverDetails] = useState(
    localReserverDetails || { id: "", firstName: "", lastName: "", phoneNumber: "" },
  );
  const [outing, setOuting] = useState<Outing | null>(localOuting);

  const submissionIsLoading = createBookingIsLoading || updateDetailsIsLoading || submitDetailsIsLoading;
  // only prevent submit on internalError since that can be fixed w/o another submit
  const submitButtonDisabled = !!(submissionIsLoading || internalReserverDetailError);
  const reserverDetailError = internalReserverDetailError || externalReserverDetailError;
  const error = [paymentError, bookingError].filter((e) => e).join("\n");

  function checkReserverDetailsInputs(details: ReserverFormFields) {
    if (details.firstName.length === 0) {
      setInternalReserverDetailError("First name required");
    } else if (details.lastName.length === 0) {
      setInternalReserverDetailError("Last name required");
    } else if (details.phoneNumber.length === 0) {
      setInternalReserverDetailError("Phone number required");
    } else {
      // all good
      setInternalReserverDetailError(undefined);
    }
  }

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

  useEffect(() => {
    switch (outingData?.viewer.__typename) {
      case "AuthenticatedViewerQueries": {
        // prefer in-memory data (if vailable)
        if (!outing) {
          setOuting(outingData.viewer.outing);
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
  }, [outingData]);

  const handleReserverDetailChange = useCallback(
    (key: keyof ReserverFormFields, value: string) => {
      const newDetails = {
        ...reserverDetails,
        [key]: value,
      };
      setReserverDetails(newDetails);
      checkReserverDetailsInputs(newDetails);
    },
    [reserverDetails],
  );

  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!stripeClient || !stripeElements) {
        console.warn("stripe not loaded; must wrap in StripeElementsProvider");
        return;
      }
      setInternalReserverDetailError(undefined);

      let bookingDetails = { ...reserverDetails };
      try {
        if (outing?.restaurant) {
          // if the reserver details dont have db ID yet, create a new entry
          if (reserverDetails.id.length == 0) {
            const submitDetailsResp = await submitReserverDetails({
              input: reserverDetails,
            });
            switch (submitDetailsResp.data?.viewer.__typename) {
              case "AuthenticatedViewerMutations": {
                const createdData = submitDetailsResp.data.viewer.submitReserverDetails;
                switch (createdData?.__typename) {
                  case "SubmitReserverDetailsSuccess": {
                    bookingDetails.id = createdData.reserverDetails.id;
                    dispatch(storeReserverDetails({ details: bookingDetails }));
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
                    // 500 error
                    setExternalReserverDetailError("Unable to book your outing. Please try again later.");
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
                return;
            }
          }
          // existing db entry needs to be updated
          else {
            const updateDetailsResp = await updateReserverDetails({
              input: reserverDetails,
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
                    return;
                  default:
                    // 500 error
                    setExternalReserverDetailError("Unable to book your outing. Please try again later.");
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
                return;
            }
          }
        }

        if (hasPaidActivity(outing)) {
          const serverHasNoPaymentDetails = false;
          if (serverHasNoPaymentDetails) {
            // TODO: create payment details
          } else {
            // TODO: update payment details
          }
        }

        const createBookingResp = await createBooking({
          input: {
            reserverDetailsId: bookingDetails.id,
            outingId,
          },
        });
        switch (createBookingResp.data?.viewer.__typename) {
          case "AuthenticatedViewerMutations": {
            const createdData = createBookingResp.data?.viewer.createBooking;
            switch (createdData?.__typename) {
              case "CreateBookingSuccess":
                navigate(AppRoute.checkoutComplete);
                // allow success case to continue execution
                break;
              case "CreateBookingFailure":
                switch (createdData.failureReason) {
                  case CreateBookingFailureReason.ValidationErrors: {
                    // TODO: when would this happen????
                    const invalidFields = createdData.validationErrors?.map((e) => e.field).join(", ");
                    setBookingError(`The following fields are invalid: ${invalidFields}`);
                    break;
                  }
                  default:
                    console.error("Unhandled case for CreateBookingFailure", createdData.failureReason);
                    break;
                }
                return;
              default:
                // 500 error
                setBookingError("Unable to book your outing. Please try again later.");
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
            return;
        }

        // execute the payment
        if (hasPaidActivity(outing)) {
          // TODO: send w/ existing payment details when not using new card
          if (isUsingNewCard) {
            const response = await stripeClient.confirmPayment({
              elements: stripeElements,
              clientSecret: "", // This property is required but already provided by stripeElements
              confirmParams: {
                return_url: `${window.location.origin}${AppRoute.checkoutComplete}`,
              },
            });

            if (response.error) {
              console.error(response.error);
              setPaymentError(response.error.message);
              return;
            }
          }
        }
      } catch {
        // network error
        setInternalReserverDetailError("Unable to book your outing. Please try again later.");
      }
    },
    [reserverDetails, stripeClient, stripeElements, outing],
  );

  // TODO: render cost header? opentable footer?
  return (
    <FormContainer onSubmit={handleSubmit}>
      <ReservationDetailsForm
        reserverDetails={reserverDetails}
        onChange={handleReserverDetailChange}
        error={reserverDetailError}
        isLoading={listDetailsIsLoading}
        showStripeBadge={showStripeBadge}
      />

      {/* TODO pass real payment data */}
      {hasPaidActivity(outing) && (
        <PaymentForm
          paymentDetails="Visa *1234"
          isUsingNewCard={isUsingNewCard}
          setIsUsingNewCard={setIsUsingNewCard}
        />
      )}

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}

      <PaddedPrimaryButton type="submit" loading={submissionIsLoading} disabled={submitButtonDisabled}>
        Save
      </PaddedPrimaryButton>
    </FormContainer>
  );
};

/**
 * This wrapper is necessary to make stripe hooks available inside the
 * CheckoutForm component where all the logic is.
 * The StripeElementsProvider can't be put in the App.tsx providers
 * component because it requires the user to be authed, which we don't want
 * in our App root.
 */
const CheckoutReservation = ({ outingId, showStripeBadge }: { outingId: string; showStripeBadge?: boolean }) => {
  return (
    <StripeElementsProvider>
      <CheckoutForm outingId={outingId} showStripeBadge={showStripeBadge} />
    </StripeElementsProvider>
  );
};

export default CheckoutReservation;
