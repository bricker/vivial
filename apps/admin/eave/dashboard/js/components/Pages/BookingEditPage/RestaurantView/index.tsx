import LoadingButton from "$eave-dashboard/js/components/Buttons/LoadingButton";
import EnumDropdown from "$eave-dashboard/js/components/EnumDropdown";
import EditIcon from "$eave-dashboard/js/components/Icons/EditIcon";
import TrashIcon from "$eave-dashboard/js/components/Icons/TrashIcon";
import Input from "$eave-dashboard/js/components/Inputs/Input";
import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import Paper from "$eave-dashboard/js/components/Paper";
import DateTimeSelections from "$eave-dashboard/js/components/Selections/DateTimeSelections";
import {
  AdminBookingInfo,
  AdminUpdateBookingFailureReason,
  Restaurant,
  RestaurantSource,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { useUpdateBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { Button, CircularProgress } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { enumKeyFromType, enumTypeFromValue, formatDate } from "../helper";

const RestaurantView = ({
  data,
  detailData,
  isLoading,
}: {
  data: AdminBookingInfo | undefined | null;
  detailData: Restaurant | undefined | null;
  isLoading: boolean;
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [restaurantSourceId, setRestaurantSourceId] = useState("(unset)");
  const [restaurantSource, setRestaurantSource] = useState<RestaurantSource | "">("");
  const [restaurantStartTime, setRestaurantStartTime] = useState<Date | undefined>(undefined);
  const [error, setError] = useState("");
  const fallback = "[None]";

  const [updateBooking, { isLoading: updateBookingIsLoading }] = useUpdateBookingMutation();

  useEffect(() => {
    if (data?.restaurantSource) {
      setRestaurantSource(data.restaurantSource);
    }
    if (data?.restaurantSourceId) {
      setRestaurantSourceId(data.restaurantSourceId);
    }
    if (data?.restaurantArrivalTime) {
      setRestaurantStartTime(new Date(data.restaurantArrivalTime));
    }
  }, [data]);

  const updateBookingWrapper = async ({
    bookingId,
    newRestaurantSource,
    newRestaurantSourceId,
    newRestaurantStartTime,
  }: {
    bookingId: string;
    newRestaurantSource?: RestaurantSource | null;
    newRestaurantSourceId?: string | null;
    newRestaurantStartTime?: string;
  }) => {
    setError("");

    const resp = await updateBooking({
      input: {
        bookingId,
        restaurantSource: newRestaurantSource,
        restaurantSourceId: newRestaurantSourceId,
        restaurantStartTimeUtc: newRestaurantStartTime,
      },
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
          case AdminUpdateBookingFailureReason.RestaurantSourceNotFound:
            setError("New restaurant indicated by source + source ID was not found");
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
        await updateBookingWrapper({ bookingId, newRestaurantSource: null, newRestaurantSourceId: null });
      }
    }
  }, [data]);

  const handleUpdateClick = useCallback(async () => {
    const bookingId = data?.id;
    const newRestaurantSourceId = restaurantSourceId !== data?.restaurantSourceId ? restaurantSourceId : undefined;
    let newRestaurantSource = undefined;
    if (newRestaurantSourceId) {
      // only send source if a new ID has also been set
      newRestaurantSource = restaurantSource || undefined;
    }
    const newRestaurantStartTime =
      restaurantStartTime?.toISOString() !== data?.restaurantArrivalTime
        ? restaurantStartTime?.toISOString()
        : undefined;
    if (bookingId) {
      await updateBookingWrapper({
        bookingId,
        newRestaurantSource,
        newRestaurantSourceId,
        newRestaurantStartTime,
      });
    }
  }, [data, restaurantSource, restaurantSourceId, restaurantStartTime]);

  const bookingRestaurantExists =
    data?.restaurantBookingLink ||
    data?.restaurantName ||
    data?.restaurantSource ||
    data?.restaurantSourceId ||
    data?.restaurantArrivalTime;

  return (
    <Paper>
      <h2>Restaurant info</h2>
      <h3>Core internal details:</h3>
      {bookingRestaurantExists ? (
        <div>
          <div>
            {isEditing ? (
              <Button onClick={() => setIsEditing(false)}>Stop editing</Button>
            ) : (
              <Button variant="contained" endIcon={<EditIcon color="black" />} onClick={() => setIsEditing(true)}>
                Edit Restaurant
              </Button>
            )}
          </div>
          <b>Name: {data.restaurantName}</b>
          {restaurantStartTime && (
            <div>
              {isEditing ? (
                <DateTimeSelections
                  cta="Save"
                  startDateTime={restaurantStartTime}
                  onSubmit={(newDate) => setRestaurantStartTime(newDate)}
                />
              ) : (
                <p>at time: {formatDate(restaurantStartTime)}</p>
              )}
            </div>
          )}
          <p>
            Website/booking link:{" "}
            {data.restaurantBookingLink ? (
              <ExternalLink to={data.restaurantBookingLink}>{data.restaurantBookingLink}</ExternalLink>
            ) : (
              fallback
            )}
          </p>
          <EnumDropdown
            enumType={RestaurantSource}
            label="Restaurant Source"
            disabled={!isEditing}
            initialValue={(() => {
              if (data?.restaurantSource) {
                return enumKeyFromType(RestaurantSource, data.restaurantSource);
              }
              return null;
            })()}
            onChange={(value) => {
              if (value) {
                const enumType = enumTypeFromValue(RestaurantSource, value);
                if (enumType) {
                  setRestaurantSource(enumType);
                }
              }
            }}
          />
          <div>
            <label>Source ID:</label>
            <Input
              disabled={!isEditing}
              value={restaurantSourceId}
              onChange={(e) => setRestaurantSourceId(e.target.value)}
            />
          </div>

          {isEditing && (
            <div style={{ display: "flex", justifyContent: "space-around" }}>
              <LoadingButton loading={updateBookingIsLoading} variant="contained" onClick={handleUpdateClick}>
                Update restaurant to new values
              </LoadingButton>
              <Button variant="contained" onClick={handleDeleteClick} endIcon={<TrashIcon color="black" />}>
                Delete Restaurant
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
          {detailData.reservable && <b>Reservation possible; Please reserve.</b>}

          <p>Location:</p>
          <p>{detailData.location.address.formattedSingleline}</p>
          <p>{`(in region: ${detailData.location.searchRegion.name})`}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </Paper>
  );
};

export default RestaurantView;
