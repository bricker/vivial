import {
  CreateBookingFailureReason,
  UpdateReserverDetailsFailureReason,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import {
  useCreateBookingMutation,
  useListReserverDetailsQuery,
  useUpdateReserverDetailsMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { storeReserverDetails } from "$eave-dashboard/js/store/slices/reserverDetailsSlice";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { CircularProgress, Typography, styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import LoadingButton from "../../Buttons/LoadingButton";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";
import LogoPill, { logos } from "../../LogoPill";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 32,
}));

const FormPaper = styled(Paper)(() => ({
  maxWidth: 450,
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

const FieldsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
  marginBottom: 24,
}));

const BoldInput = styled(Input)(() => ({
  padding: "5px 16px",
  fontFamily: fontFamilies.inter,
  fontWeight: 600,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
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

const PaddedPrimaryButton = styled(LoadingButton)(() => ({
  padding: "10px 14px",
  minWidth: rem("76px"),
}));

const TitleContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const InfoContainer = styled("div")(() => ({
  marginTop: 24,
}));

const StateContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 32,
}));

interface ReserverFormFields {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
}

const ReservationDetailsForm = () => {
  const localReserverDetails = useSelector((state: RootState) => state.reserverDetails.reserverDetails);
  const params = useParams();
  const outingId = params["outingId"];
  // TODO: if outing id is empty/not a uuid, show some error screen

  const [reserverDetails, setReserverDetails] = useState<ReserverFormFields>(
    localReserverDetails || { id: "", firstName: "", lastName: "", phoneNumber: "" },
  );
  const [internalError, setInternalError] = useState<string | undefined>(undefined);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [createBooking, { isLoading: createBookingIsLoading, isError: createBookingIsError }] =
    useCreateBookingMutation();
  const [updateReserverDetails, { isLoading: updateDetailsIsLoading, isError: updateDetailsIsError }] =
    useUpdateReserverDetailsMutation();
  const {
    data: reserverDetailsData,
    isLoading: listDetailsIsLoading,
    isError: listDetailsIsError,
  } = useListReserverDetailsQuery({});
  const error = internalError || listDetailsIsError || createBookingIsError || updateDetailsIsError;
  const submissionIsLoading = createBookingIsLoading || updateDetailsIsLoading;
  // only prevent submit on internalError since that can be fixed w/o another submit
  const submitButtonDisabled = !!(submissionIsLoading || internalError);
  const reserverDetailsHasValues = !!reserverDetails.id;

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

  function checkInputs(details: ReserverFormFields) {
    if (details.firstName.length === 0) {
      setInternalError("First name required");
    } else if (details.lastName.length === 0) {
      setInternalError("Last name required");
    } else if (details.phoneNumber.length === 0) {
      setInternalError("Phone number required");
    } else {
      // all good
      setInternalError(undefined);
    }
  }

  const handleFirstNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newDetails = {
        ...reserverDetails,
        firstName: e.target.value,
      };
      setReserverDetails(newDetails);
      checkInputs(newDetails);
    },
    [reserverDetails],
  );
  const handleLastNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newDetails = {
        ...reserverDetails,
        lastName: e.target.value,
      };
      setReserverDetails(newDetails);
      checkInputs(newDetails);
    },
    [reserverDetails],
  );
  const handlePhoneNumberChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newDetails = {
        ...reserverDetails,
        phoneNumber: e.target.value,
      };
      setReserverDetails(newDetails);
      checkInputs(newDetails);
    },
    [reserverDetails],
  );
  const handleSubmit = useCallback(async () => {
    setInternalError(undefined);

    try {
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
          const updatedData = updateDetailsResp.data?.viewer.updateReserverDetails;
          switch (updatedData?.__typename) {
            case "UpdateReserverDetailsSuccess":
              dispatch(storeReserverDetails({ details: updatedData.reserverDetails }));
              // allow success case to continue execution
              break;
            case "UpdateReserverDetailsFailure":
              switch (updatedData.failureReason) {
                case UpdateReserverDetailsFailureReason.ValidationErrors: {
                  const invalidFields = updatedData.validationErrors?.map((e) => e.field).join(", ");
                  setInternalError(`The following fields are invalid: ${invalidFields}`);
                  break;
                }
                default:
                  console.error("Unhandled case for UpdateReserverDetailsFailure", updatedData.failureReason);
                  break;
              }
              return;
            default:
              // 500 error
              setInternalError("Unable to book your outing. Please try again later.");
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

      const createBookingResp = await createBooking({
        input: {
          reserverDetailsId: reserverDetails!.id,
          outingId: outingId!,
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
                  const invalidFields = createdData.validationErrors?.map((e) => e.field).join(", ");
                  setInternalError(`The following fields are invalid: ${invalidFields}`);
                  break;
                }
                default:
                  console.error("Unhandled case for CreateBookingFailure", createdData.failureReason);
                  break;
              }
              return;
            default:
              // 500 error
              setInternalError("Unable to book your outing. Please try again later.");
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
    } catch {
      // network error
      setInternalError("Unable to book your outing. Please try again later.");
    }
  }, [reserverDetails]);

  return (
    <PageContainer>
      <FormPaper>
        <TitleContainer>
          <Typography variant="h2">Almost there!</Typography>
          <Typography variant="subtitle1">Submit your details to complete your reservation.</Typography>
        </TitleContainer>

        {reserverDetailsHasValues ? (
          // we have details to display; show them
          <InfoContainer>
            <FieldsContainer>
              <BoldInput placeholder="First name" value={reserverDetails.firstName} onChange={handleFirstNameChange} />
              <BoldInput placeholder="Last name" value={reserverDetails.lastName} onChange={handleLastNameChange} />
              <BoldInput placeholder="Phone #" value={reserverDetails.phoneNumber} onChange={handlePhoneNumberChange} />
            </FieldsContainer>

            {error && (
              <InputErrorContainer>
                <InputError>{error}</InputError>
              </InputErrorContainer>
            )}

            <PaddedPrimaryButton
              onClick={handleSubmit}
              loading={submissionIsLoading}
              disabled={submitButtonDisabled}
              fullWidth
            >
              Reserve
            </PaddedPrimaryButton>
          </InfoContainer>
        ) : (
          <StateContainer>
            {listDetailsIsLoading ? (
              // loading state
              <CircularProgress color="secondary" />
            ) : listDetailsIsError ? (
              // error state
              "Oops! We encountered a problem, please try again later."
            ) : (
              // TODO: this isnt good enough here... we'd need to offer ability to create fresh reserver details to fix this case
              "There is no booking info to display."
            )}
          </StateContainer>
        )}
      </FormPaper>
      <FooterContainer>
        <FooterText variant="body2">
          Reservations
          <br />
          powered by
        </FooterText>
        <LogoPill attrs={logos["opentable"]!} />
      </FooterContainer>
    </PageContainer>
  );
};

export default ReservationDetailsForm;
