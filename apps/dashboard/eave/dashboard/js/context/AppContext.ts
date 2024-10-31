import { createContext } from "react";
import { CreateBookingCtx } from "../graphql/createBooking";
import { ReplanOutingCtx } from "../graphql/replanOuting";
import { SubmitReserverDetailsCtx } from "../graphql/submitReserverDetails";
import { SubmitSurveyCtx } from "../graphql/submitSurvey";

export type AppContextProps = SubmitSurveyCtx & SubmitReserverDetailsCtx & CreateBookingCtx & ReplanOutingCtx;

export const AppContext = createContext<AppContextProps>({});
