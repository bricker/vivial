import { createContext } from "react";
import { CreateBookingCtx } from "../graphql/createBooking";
import { SubmitReserverDetailsCtx } from "../graphql/submitReserverDetails";
import { SubmitSurveyCtx } from "../graphql/submitSurvey";

export type AppContextProps = SubmitSurveyCtx & SubmitReserverDetailsCtx & CreateBookingCtx;

export const AppContext = createContext<AppContextProps>({});
