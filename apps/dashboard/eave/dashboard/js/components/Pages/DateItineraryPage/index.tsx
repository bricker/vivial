import { useGetOutingAnonymousQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import { CookieId } from "$eave-dashboard/js/types/cookie";

import BookingSection from "./Sections/BookingSection";
import LogisticsSection from "./Sections/LogisticsSection";

const PageContainer = styled("div")(() => ({}));

const DateItineraryPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const outingId = params["outingId"] || "";
  const outing = useSelector((state: RootState) => state.outing.details);
  const [_cookies, _setCookie] = useCookies([CookieId.Reroll]);
  const [skipOutingQuery, setSkipOutingQuery] = useState(true);

  // TODO: Use the auth query when authed.
  const { data: outingData, isLoading: outingDataLoading } = useGetOutingAnonymousQuery(
    { input: { id: outingId } },
    { skip: skipOutingQuery },
  );

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
      <LogisticsSection />
      <BookingSection />
    </PageContainer>
  );
};

export default DateItineraryPage;
