import CopyableTextButton from "$eave-dashboard/js/components/Buttons/CopyableTextButton";
import { AdminBookingInfo } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";

const ReserverDetailsView = ({
  data,
  isLoading,
}: {
  data: AdminBookingInfo | undefined | null;
  isLoading: boolean;
}) => {
  const fallback = "[none]";
  return (
    <div>
      <h2>Reserver info:</h2>
      {data ? (
        <>
          <p>
            First name: <CopyableTextButton text={data.reserverDetails?.firstName || fallback} />
          </p>
          <p>
            Last name: <CopyableTextButton text={data.reserverDetails?.lastName || fallback} />
          </p>
          <p>
            Phone number: <CopyableTextButton text={data.reserverDetails?.phoneNumber || fallback} />
          </p>
          <div>
            <h4>Participating accounts:</h4>
            {data.accounts.map((account) => (
              <div>
                <p>
                  account id: <CopyableTextButton text={account.id} />
                </p>
                <p>
                  Email: <CopyableTextButton text={account.email} />
                </p>
              </div>
            ))}
          </div>
        </>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </div>
  );
};

export default ReserverDetailsView;
