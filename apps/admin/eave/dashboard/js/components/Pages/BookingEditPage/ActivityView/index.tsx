import LoadingButton from "$eave-dashboard/js/components/Buttons/LoadingButton";
import EnumDropdown from "$eave-dashboard/js/components/EnumDropdown";
import EditIcon from "$eave-dashboard/js/components/Icons/EditIcon";
import TrashIcon from "$eave-dashboard/js/components/Icons/TrashIcon";
import Input from "$eave-dashboard/js/components/Inputs/Input";
import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import {
  Activity,
  ActivitySource,
  AdminBookingInfo,
  AdminUpdateBookingFailureReason,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { useUpdateBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { Button, CircularProgress } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { enumKeyFromType, enumTypeFromValue, formatDateString } from "../helper";

const ActivityView = ({
  data,
  detailData,
  isLoading,
}: {
  data: AdminBookingInfo | undefined | null;
  detailData: Activity | undefined | null;
  isLoading: boolean;
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [activitySourceId, setActivitySourceId] = useState("(unset)");
  const [activitySource, setActivitySource] = useState<ActivitySource | "">("");
  const [error, setError] = useState("");
  const fallback = "[None]";

  const [updateBooking, { isLoading: updateBookingIsLoading }] = useUpdateBookingMutation();

  useEffect(() => {
    if (data?.activitySourceId) {
      setActivitySourceId(data.activitySourceId);
    }
    if (data?.activitySource) {
      setActivitySource(data.activitySource);
    }
  }, [data]);

  const updateBookingWrapper = async ({
    bookingId,
    newActivitySource,
    newActivitySourceId,
  }: {
    bookingId: string;
    newActivitySource?: ActivitySource | null;
    newActivitySourceId?: string | null;
  }) => {
    setError("");

    const resp = await updateBooking({
      input: { bookingId, activitySource: newActivitySource, activitySourceId: newActivitySourceId },
    });

    switch (resp.data?.adminUpdateBooking?.__typename) {
      case "AdminUpdateBookingSuccess": {
        // const data = resp.data.adminUpdateBooking.booking.id
        // yay we done it
        setIsEditing(false);
        break;
      }
      case "AdminUpdateBookingFailure": {
        switch (resp.data.adminUpdateBooking.failureReason) {
          case AdminUpdateBookingFailureReason.ActivitySourceNotFound:
            setError("New activity indicated by source + source ID was not found");
            break;
          case AdminUpdateBookingFailureReason.BookingNotFound:
            setError("The booking can no longer be found");
            break;
          case AdminUpdateBookingFailureReason.ValidationErrors:
            setError(
              `Validation failed for following: ${resp.data.adminUpdateBooking.validationErrors
                ?.map((e) => e.field)
                .join(", ")}`,
            );
            break;
          default:
            setError(`unhandled AdminUpdateBookingFailureReason: ${resp.data.adminUpdateBooking.failureReason}`);
            break;
        }
        break;
      }
      default:
        // some kind of error?
        if (resp.error) {
          setError(JSON.stringify(resp.error));
        }
    }
  };

  const handleDeleteClick = useCallback(async () => {
    const bookingId = data?.id;
    if (bookingId) {
      const resp = confirm("Really permanantly delete event right now?");

      if (resp) {
        // submit delete
        await updateBookingWrapper({ bookingId, newActivitySource: null, newActivitySourceId: null });
      }
    }
  }, [data]);

  const handleUpdateClick = useCallback(async () => {
    const bookingId = data?.id;
    if (bookingId) {
      await updateBookingWrapper({
        bookingId,
        newActivitySource: activitySource || undefined,
        newActivitySourceId: activitySourceId,
      });
    }
  }, [data, activitySource, activitySourceId]);

  return (
    <div>
      <h2>Activity info</h2>
      <h3>Core internal details:</h3>
      {data ? (
        <div>
          <div>
            {isEditing ? (
              <Button onClick={() => setIsEditing(false)}>Stop editing</Button>
            ) : (
              <Button variant="contained" endIcon={<EditIcon color="black" />} onClick={() => setIsEditing(true)}>
                Edit Activity
              </Button>
            )}
          </div>
          <b>Name: {data.activityName}</b>
          <p>at time: {formatDateString(data.activityStartTime)}</p>
          <p>
            Website/booking link:{" "}
            {data.activityBookingLink ? (
              <ExternalLink to={data.activityBookingLink}>{data.activityBookingLink}</ExternalLink>
            ) : (
              fallback
            )}
          </p>
          {/* <Input contentEditable={isEditing} value={`Source: ${data.activitySource}`} /> */}
          <EnumDropdown
            enumType={ActivitySource}
            label="Activity Source"
            disabled={!isEditing}
            initialValue={(() => {
              if (data?.activitySource) {
                return enumKeyFromType(ActivitySource, data.activitySource);
              }
              return null;
            })()}
            onChange={(value) => {
              if (value) {
                const enumType = enumTypeFromValue(ActivitySource, value);
                if (enumType) {
                  setActivitySource(enumType);
                }
              }
            }}
          />
          <div>
            <label>Source ID:</label>
            <Input
              disabled={!isEditing}
              value={activitySourceId}
              onChange={(e) => setActivitySourceId(e.target.value)}
            />
          </div>

          {isEditing && (
            <div style={{ display: "flex", justifyContent: "space-around" }}>
              <LoadingButton loading={updateBookingIsLoading} variant="contained" onClick={handleUpdateClick}>
                Update activity to new values
              </LoadingButton>
              <Button variant="contained" onClick={handleDeleteClick} endIcon={<TrashIcon color="black" />}>
                Delete Activity
              </Button>
            </div>
          )}
          {error && <h4 style={{ color: "red" }}>ERROR: {error}</h4>}
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
      <h3>Extra details:</h3>
      {detailData ? (
        <div>
          {/* <p>
            Description:
            {detailData.description}
          </p> */}
          <p>
            Location: {detailData.venue.name}
            {detailData.venue.location.address.formattedMultiline}
          </p>
          <p>{`(in region: ${detailData.venue.location.searchRegion.name})`}</p>
          <p>Category: {detailData.categoryGroup?.name}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </div>
  );
};

export default ActivityView;
