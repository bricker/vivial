import { createContext } from "react";
import { SurveySubmitCtx } from "../graphql/survey.js";

export type AppContextProps = SurveySubmitCtx; // & union other types

export const AppContext = createContext<AppContextProps>({});
