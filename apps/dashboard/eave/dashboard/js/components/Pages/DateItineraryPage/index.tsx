import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";

import { useGetOutingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import CheckoutReservation from "../../CheckoutReservation";
import Modal from "../../Modal";

const PageContainer = styled("div")(() => ({}));

const BadgeImg = styled("img")(() => ({
  height: rem("24px"),
  maxHeight: 32,
}));

const DateItineraryPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const outingId = params["outingId"] || "";
  const outing = useSelector((state: RootState) => state.outing.details);
  // const [cookies, setCookie] = useCookies([CookieId.Reroll]);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [skipOutingQuery, setSkipOutingQuery] = useState(true);
  // TODO: should we use the auth query when authed? how do that...?
  const { data: outingData, isLoading: outingDataLoading } = useGetOutingQuery(
    { input: { id: outingId } },
    { skip: skipOutingQuery },
  );

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  useEffect(() => {
    if (outing === null) {
      setSkipOutingQuery(false);
    }
  }, [outing]);

  useEffect(() => {
    if (outingData?.outing) {
      dispatch(plannedOuting({ outing: outingData.outing }));
    }
  }, [outingData]);

  // TODO: Handle Reroll cookie.
  // const rerollCookie = cookies[CookieId.Reroll] as RerollCookie;
  //   if (rerollCookie) {
  //     const rerolls = rerollCookie.rerolls + 1;
  //     const updated = new Date();
  //     const hoursSinceUpdate = getHoursDiff(updated, new Date(rerollCookie.updated));
  //     setCookie(CookieId.Reroll, { rerolls, updated });
  //     if (rerolls >= 4 && hoursSinceUpdate < 24) {
  //       navigate(AppRoute.signupMultiReroll);
  //     }
  //   }
  // }

  // useEffect(() => {
  //   if (!cookies[CookieId.Reroll]) {
  //     setCookie(CookieId.Reroll, {
  //       updated: new Date(),
  //       rerolls: 0,
  //     });
  //   }
  // }, [cookies]);

  // TODO: Loading View
  if (outingDataLoading === true) {
    return "Loading...";
  }

  const stripeBadge = <BadgeImg src={imageUrl("powered-by-stripe.png")} alt="powered by Stripe" />;

  return (
    <PageContainer>
      <Modal title="Booking Info" onClose={toggleBookingOpen} open={bookingOpen} badge={stripeBadge} thinPadding>
        <CheckoutReservation outingId={outingId} />
      </Modal>
      <button onClick={toggleBookingOpen}>TEMP: Open Booking Modal</button>
    </PageContainer>
  );
};

export default DateItineraryPage;
