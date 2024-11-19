import React, { createContext } from "react";
import { CreatePaymentIntentCtx, createCreatePaymentIntentCtx } from "./graphql/hooks/createPaymentIntent";

export type AppContextProps =
  | undefined
  | {
      createPaymentIntent: CreatePaymentIntentCtx;
    };

export const AppContext = createContext<AppContextProps>(undefined);

export const AppContextProvider = ({ children }: { children: React.ReactElement }) => {
  const context: AppContextProps = {
    createPaymentIntent: createCreatePaymentIntentCtx(),
  };

  return <AppContext.Provider value={context}>{children}</AppContext.Provider>;
};
