import { createContext } from "react";
import { SurveySubmitCtx } from "../graphql/survey";
import { ReplanOutingCtx } from "../graphql/outing";

export type AppContextProps = SurveySubmitCtx & ReplanOutingCtx;

export const AppContext = createContext<AppContextProps>({});
