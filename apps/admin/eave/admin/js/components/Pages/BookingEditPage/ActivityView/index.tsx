import LoadingButton from "$eave-dashboard/js/components/Buttons/LoadingButton";
import EnumDropdown from "$eave-dashboard/js/components/EnumDropdown";
import EditIcon from "$eave-dashboard/js/components/Icons/EditIcon";
import TrashIcon from "$eave-dashboard/js/components/Icons/TrashIcon";
import Input from "$eave-dashboard/js/components/Inputs/Input";
import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import Paper from "$eave-dashboard/js/components/Paper";
import DateTimeSelections from "$eave-dashboard/js/components/Selections/DateTimeSelections";
import {
  Activity,
  ActivitySource,
  AdminBookingInfo,
  AdminUpdateBookingFailureReason,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { useUpdateBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { Button, CircularProgress } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { enumKeyFromType, enumTypeFromValue, formatDate } from "../helper";

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
  const [activityStartTime, setActivityStartTime] = useState<Date | undefined>(undefined);
  const [error, setError] = useState("");
  const fallback = "[None]";

  const [updateBooking, { isLoading: updateBookingIsLoading }] = useUpdateBookingMutation();

  useEffect(() => {
    if (data?.activitySource) {
      setActivitySource(data.activitySource);
    }
    if (data?.activitySourceId) {
      setActivitySourceId(data.activitySourceId);
    }
    if (data?.activityStartTime) {
      setActivityStartTime(new Date(data.activityStartTime));
    }
  }, [data]);

  const updateBookingWrapper = async ({
    bookingId,
    newActivitySource,
    newActivitySourceId,
    newActivityStartTime,
  }: {
    bookingId: string;
    newActivitySource?: ActivitySource | null;
    newActivitySourceId?: string | null;
    newActivityStartTime?: string;
  }) => {
    setError("");

    const resp = await updateBooking({
      input: {
        bookingId,
        activitySource: newActivitySource,
        activitySourceId: newActivitySourceId,
        activityStartTimeUtc: newActivityStartTime,
      },
    });
    console.log(resp);

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
    const newActivitySourceId = activitySourceId !== data?.activitySourceId ? activitySourceId : undefined;
    let newActivitySource = undefined;
    if (newActivitySourceId) {
      // only set new source if source ID was also set
      newActivitySource = activitySource || undefined;
    }
    const newActivityStartTime =
      activityStartTime?.toISOString() !== data?.activityStartTime ? activityStartTime?.toISOString() : undefined;
    if (bookingId) {
      await updateBookingWrapper({
        bookingId,
        newActivitySource,
        newActivitySourceId,
        newActivityStartTime,
      });
    }
  }, [data, activitySource, activitySourceId, activityStartTime]);

  const bookingActivityExists =
    data?.activityBookingLink ||
    data?.activityName ||
    data?.activitySource ||
    data?.activitySourceId ||
    data?.activityStartTime;

  return (
    <Paper>
      <h2>Activity info</h2>
      <h3>Core internal details:</h3>
      {bookingActivityExists ? (
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
          {activityStartTime && (
            <div>
              {isEditing ? (
                <DateTimeSelections
                  cta="Save"
                  startDateTime={activityStartTime}
                  onSubmit={(newDate) => setActivityStartTime(newDate)}
                />
              ) : (
                <p>at time: {formatDate(activityStartTime)}</p>
              )}
            </div>
          )}
          <p>
            Website/booking link:{" "}
            {data.activityBookingLink ? (
              <ExternalLink to={data.activityBookingLink}>{data.activityBookingLink}</ExternalLink>
            ) : (
              fallback
            )}
          </p>
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
          <p>Location: {detailData.venue.name}</p>
          <p>{detailData.venue.location.address.formattedSingleline}</p>
          <p>{`(in region: ${detailData.venue.location.searchRegion.name})`}</p>
          <p>Category: {detailData.categoryGroup?.name || fallback}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </Paper>
  );
};

export default ActivityView;
