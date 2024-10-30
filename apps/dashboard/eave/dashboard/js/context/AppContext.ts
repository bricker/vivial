import { createContext } from "react";
import { ReplanOutingCtx } from "../graphql/outing";
import { SurveySubmitCtx } from "../graphql/survey";

export type AppContextProps = SurveySubmitCtx & ReplanOutingCtx;

export const AppContext = createContext<AppContextProps>({});
