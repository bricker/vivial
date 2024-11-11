import { createContext } from "react";
import { CreateBookingCtx } from "../graphql/hooks/createBooking";
import { ReplanOutingCtx } from "../graphql/hooks/replanOuting";
import { SubmitReserverDetailsCtx } from "../graphql/hooks/submitReserverDetails";
import { SubmitSurveyCtx } from "../graphql/hooks/submitSurvey";

// TODO: Detele file (potentially).
export type AppContextProps = SubmitSurveyCtx & SubmitReserverDetailsCtx & CreateBookingCtx & ReplanOutingCtx;

export const AppContext = createContext<AppContextProps>({});
