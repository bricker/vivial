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
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
}));

const FieldsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
  marginBottom: 24,
}));

const NameInputContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  gap: 8,
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
  flexDirection: "row",
  justifyContent: "space-between",
}));

const LabeledInfoContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const LabelText = styled("p")(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
}));

const ValueText = styled("p")(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
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

const ReservationDetailsForm = () => {
  const localReserverDetails = useSelector((state: RootState) => state.reserverDetails.reserverDetails);
  let reserverDetails = localReserverDetails;
  const params = useParams();
  const outingId = params["outingId"];
  // TODO: if outing id is empty/not a uuid, show some error screen

  const [firstName, setFirstName] = useState(reserverDetails?.firstName || "");
  const [lastName, setLastName] = useState(reserverDetails?.lastName || "");
  const [phoneNumber, setPhoneNumber] = useState(reserverDetails?.phoneNumber || "");
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

  switch (reserverDetailsData?.viewer.__typename) {
    case "AuthenticatedViewerQueries": {
      // always prefer in-memory data (if available) over cached network resp
      if (!reserverDetails) {
        // NOTE: extracting and showing only the first one since we currently only
        // allow 1 reserverDetails row to be created
        reserverDetails = reserverDetailsData?.viewer?.reserverDetails[0] || null;
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

  // set existing reservation details in form once we get them
  useEffect(() => {
    if (reserverDetails) {
      setFirstName(reserverDetails.firstName);
      setLastName(reserverDetails.lastName);
      setPhoneNumber(reserverDetails.phoneNumber);
    }
  }, [reserverDetailsData]);

  function checkInputs({ first, last, phone }: { first: string; last: string; phone: string }) {
    if (first.length === 0) {
      setInternalError("First name required");
    } else if (last.length === 0) {
      setInternalError("Last name required");
    } else if (phone.length === 0) {
      setInternalError("Phone number required");
    } else {
      // all good
      setInternalError(undefined);
    }
  }

  const handleFirstNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newFirst = e.target.value;
      setFirstName(newFirst);
      checkInputs({ first: newFirst, last: lastName, phone: phoneNumber });
    },
    [firstName, lastName, phoneNumber],
  );
  const handleLastNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newLast = e.target.value;
      setLastName(newLast);
      checkInputs({ first: firstName, last: newLast, phone: phoneNumber });
    },
    [firstName, lastName, phoneNumber],
  );
  const handlePhoneNumberChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newPhone = e.target.value;
      setPhoneNumber(newPhone);
      checkInputs({ first: firstName, last: lastName, phone: newPhone });
    },
    [firstName, lastName, phoneNumber],
  );
  const handleSubmit = useCallback(async () => {
    setInternalError(undefined);

    try {
      const updateDetailsResp = await updateReserverDetails({
        input: {
          id: reserverDetails!.id,
          firstName,
          lastName,
          phoneNumber,
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
                  console.error("Unexpected case for UpdateReserverDetailsFailure");
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
                  console.error("Unexpected case for CreateBookingFailure");
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
  }, [reserverDetailsData]);

  return (
    <PageContainer>
      <Paper>
        <TitleContainer>
          <Typography variant="h2">Almost there!</Typography>
          <Typography variant="subtitle1">Submit your details to complete your reservation.</Typography>
        </TitleContainer>

        {reserverDetails ? (
          // we have details to display; show them
          <InfoContainer>
            <FieldsContainer>
              <BoldInput placeholder="First name" value={firstName} onChange={handleFirstNameChange} />
              <BoldInput placeholder="Last name" value={lastName} onChange={handleLastNameChange} />
              <BoldInput placeholder="Phone #" value={phoneNumber} onChange={handlePhoneNumberChange} />
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
      </Paper>
      TODO opentable footer
    </PageContainer>
  );
};

export default ReservationDetailsForm;
