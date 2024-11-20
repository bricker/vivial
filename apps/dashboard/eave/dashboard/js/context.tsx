import React, { createContext } from "react";
import { CreatePaymentIntentOperation, makeCreatePaymentIntentOperation } from "./graphql/hooks/createPaymentIntent";
import { makeCreateBookingOperation, type CreateBookingOperation } from "./graphql/hooks/createBooking";
import { makePlanOutingOperation, type PlanOutingOperation } from "./graphql/hooks/planOuting";
import { makeReplanOutingOperation, type ReplanOutingOperation } from "./graphql/hooks/replanOuting";
import { makeSubmitReserverDetailsOperation, type SubmitReserverDetailsOperation } from "./graphql/hooks/submitReserverDetails";

export type AppContextProps =
  | undefined
  | {
      createPaymentIntentOperation: CreatePaymentIntentOperation;
      createBookingOperation: CreateBookingOperation;
      planOutingOperation: PlanOutingOperation;
      replanOutingOperation: ReplanOutingOperation;
      submitReserverDetailsOperation: SubmitReserverDetailsOperation;
    };

export const AppContext = createContext<AppContextProps>(undefined);

export const AppContextProvider = ({ children }: { children: React.ReactElement }) => {
  const context: AppContextProps = {
    createPaymentIntentOperation: makeCreatePaymentIntentOperation(),
    createBookingOperation: makeCreateBookingOperation(),
    planOutingOperation: makePlanOutingOperation(),
    replanOutingOperation: makeReplanOutingOperation(),
    submitReserverDetailsOperation: makeSubmitReserverDetailsOperation(),
  };

  return <AppContext.Provider value={context}>{children}</AppContext.Provider>;
};
