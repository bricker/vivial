import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { useGetOutingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";

import Modal from "../../Modal";

const PageContainer = styled("div")(() => ({}));

const DateItineraryPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const outingId = params["outingId"] || "";
  const outing = useSelector((state: RootState) => state.outing.details);
  // const [cookies, setCookie] = useCookies([CookieId.Reroll]);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [skipOutingQuery, setSkipOutingQuery] = useState(true);
  const { data: outingData, isLoading: outingDataLoading } = useGetOutingQuery({ outingId }, { skip: skipOutingQuery });

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

  return (
    <PageContainer>
      <Modal title="Booking Info" onClose={toggleBookingOpen} open={bookingOpen}>
        TODO: Booking modal content goes here (pending Liam).
      </Modal>
      <button onClick={toggleBookingOpen}>TEMP: Open Booking Modal</button>
    </PageContainer>
  );
};

export default DateItineraryPage;
