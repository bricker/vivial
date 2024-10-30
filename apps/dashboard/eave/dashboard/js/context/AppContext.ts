import { createContext } from "react";
import { SubmitReserverDetailsCtx } from "../graphql/submitReserverDetails";
import { SubmitSurveyCtx } from "../graphql/submitSurvey";

export type AppContextProps = SubmitSurveyCtx & SubmitReserverDetailsCtx;

export const AppContext = createContext<AppContextProps>({});
