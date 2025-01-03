import {
  SubmitReserverDetailsFailureReason,
  UpdateReserverDetailsAccountFailureReason,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { loggedOut, updateEmail } from "$eave-dashboard/js/store/slices/authSlice";
import {
  useListReserverDetailsQuery,
  useSubmitReserverDetailsMutation,
  useUpdateReserverDetailsAccountMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { storeReserverDetails } from "$eave-dashboard/js/store/slices/reserverDetailsSlice";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { Button, CircularProgress, Typography, styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import AccountBookingInfoEditForm from "../../Forms/AccountBookingInfoEditForm";
import EditIcon from "../../Icons/EditIcon";
import Paper from "../../Paper";

const MainContainer = styled(Paper)(({ theme }) => ({
  padding: 24,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    padding: "24px 40px",
  },
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
  fontSize: rem(16),
  lineHeight: rem(30),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
}));

const ValueText = styled("p")(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: rem(16),
  lineHeight: rem(30),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
}));

const ShiftedButton = styled(Button)(() => ({
  position: "relative",
  right: -16,
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

const InfoDisplay = ({ name, email, phoneNumber }: { name?: string; email?: string; phoneNumber?: string }) => {
  const displayContent: Array<{ label: string; value: string }> = [];
  if (name) {
    displayContent.push({ label: "Name", value: name });
  }
  if (email) {
    displayContent.push({ label: "Email", value: email });
  }
  if (phoneNumber) {
    displayContent.push({ label: "Phone #", value: phoneNumber });
  }

  return (
    <>
      {displayContent.map((text) => (
        <LabeledInfoContainer key={text.label}>
          <LabelText>{text.label}</LabelText>
          <ValueText>{text.value}</ValueText>
        </LabeledInfoContainer>
      ))}
    </>
  );
};

const EditableContainer = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const dispatch = useDispatch();
  const [updateReserverDetailsAccount, { isLoading: updateDetailsIsLoading }] =
    useUpdateReserverDetailsAccountMutation();
  const [submitReserverDetails, { isLoading: submitReserverDetailsIsLoading }] = useSubmitReserverDetailsMutation();

  const reserverEmail = useSelector((state: RootState) => state.auth.account?.email);
  const localReserverDetails = useSelector((state: RootState) => state.reserverDetails.reserverDetails);

  const infoEditIsLoading = updateDetailsIsLoading || submitReserverDetailsIsLoading;

  const { data, isLoading: listDetailsIsLoading, isError: listDetailsIsError } = useListReserverDetailsQuery({});
  let reserverDetails = localReserverDetails;
  switch (data?.viewer.__typename) {
    case "AuthenticatedViewerQueries": {
      // always prefer in-memory data (if available) over cached network resp
      if (!reserverDetails) {
        // NOTE: extracting and showing only the first one since we currently only
        // allow 1 reserverDetails row to be created
        reserverDetails = data?.viewer?.reserverDetails[0] || null;
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

  const handleCancel = () => setIsEditing(false);
  const handleSubmit = useCallback(
    async ({
      firstName,
      lastName,
      phoneNumber,
      email,
    }: {
      firstName: string;
      lastName: string;
      phoneNumber: string;
      email: string;
    }) => {
      setError(undefined);

      let detailsId = reserverDetails?.id;

      try {
        // if reserverDetails doesnt have a db ID, create a db entry
        if (reserverDetails?.id === undefined) {
          const detailsResp = await submitReserverDetails({
            input: {
              firstName,
              lastName,
              phoneNumber,
            },
          });
          switch (detailsResp.data?.viewer.__typename) {
            case "AuthenticatedViewerMutations": {
              const createdData = detailsResp.data.viewer.submitReserverDetails;
              switch (createdData.__typename) {
                case "SubmitReserverDetailsSuccess": {
                  dispatch(storeReserverDetails({ details: createdData.reserverDetails }));
                  detailsId = createdData.reserverDetails.id;
                  break;
                }
                case "SubmitReserverDetailsFailure": {
                  switch (createdData.failureReason) {
                    case SubmitReserverDetailsFailureReason.ValidationErrors: {
                      const invalidFields = createdData.validationErrors?.map((e) => e.field).join(", ");
                      setError(`The following fields are invalid: ${invalidFields}`);
                      break;
                    }
                    default:
                      console.error("Unexpected case for SubmitReserverDetailsFailureReason");
                      break;
                  }
                  return;
                }
                default:
                  throw new Error("Unexected Graphql result");
              }
              break;
            }
            case "UnauthenticatedViewer":
              dispatch(loggedOut());
              window.location.assign(AppRoute.logout);
              return;
            default:
              if (detailsResp.error) {
                // 500 error
                throw new Error("Graphql error");
              }
              break;
          }
        }

        const resp = await updateReserverDetailsAccount({
          input: {
            id: detailsId!,
            firstName,
            lastName,
            phoneNumber,
            email,
          },
        });
        switch (resp.data?.viewer.__typename) {
          case "AuthenticatedViewerMutations": {
            const updatedData = resp.data?.viewer.updateReserverDetailsAccount;
            switch (updatedData?.__typename) {
              case "UpdateReserverDetailsAccountSuccess":
                dispatch(storeReserverDetails({ details: updatedData.reserverDetails }));
                dispatch(updateEmail({ email: updatedData.account.email }));
                // exit edit mode
                handleCancel();
                break;
              case "UpdateReserverDetailsAccountFailure":
                switch (updatedData.failureReason) {
                  case UpdateReserverDetailsAccountFailureReason.ValidationErrors: {
                    const invalidFields = updatedData.validationErrors?.map((e) => e.field).join(", ");
                    setError(`The following fields are invalid: ${invalidFields}`);
                    break;
                  }
                  default:
                    console.error("Unexpected case for UpdateReserverDetailsAccountFailure");
                    break;
                }
                break;
              default:
                throw new Error("Unexected Graphql result");
            }
            break;
          }
          case "UnauthenticatedViewer":
            dispatch(loggedOut());
            window.location.assign(AppRoute.logout);
            break;
          default:
            if (resp.error) {
              // 500 error
              throw new Error("Graphql error");
            }
            break;
        }
      } catch {
        // network error
        setError("Unable to update your booking info. Please try again later.");
      }
    },
    [data],
  );

  return (
    <MainContainer>
      <TitleContainer>
        <Typography variant="h2">Booking info</Typography>
        {!isEditing && reserverDetails && (
          <ShiftedButton onClick={() => setIsEditing(true)}>
            <EditIcon />
          </ShiftedButton>
        )}
      </TitleContainer>

      {reserverDetails ? (
        // we have details to display; show them
        <InfoContainer>
          {isEditing ? (
            <AccountBookingInfoEditForm
              initFirstName={reserverDetails?.firstName || ""}
              initLastName={reserverDetails?.lastName || ""}
              initEmail={reserverEmail || ""}
              initPhoneNumber={reserverDetails?.phoneNumber || ""}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              isLoading={infoEditIsLoading}
              externalError={error}
            />
          ) : (
            <InfoDisplay
              name={[reserverDetails?.firstName, reserverDetails?.lastName].filter((x) => x).join(" ")}
              email={reserverEmail}
              phoneNumber={reserverDetails?.phoneNumber}
            />
          )}
        </InfoContainer>
      ) : (
        <StateContainer>
          {listDetailsIsLoading ? (
            // loading state
            <CircularProgress color="secondary" />
          ) : (
            listDetailsIsError &&
            // error state
            "Oops! We encountered a problem, please try again later."
          )}
        </StateContainer>
      )}
    </MainContainer>
  );
};

export default EditableContainer;
