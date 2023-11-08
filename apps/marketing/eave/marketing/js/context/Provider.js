// @ts-check
import React, { createContext, useState } from "react";
import { AUTH_MODAL_STATE } from "../constants.js";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars

export const AppContext = createContext(null);

/**
 * @typedef {[Types.AuthModal, React.Dispatch<React.SetStateAction<Types.AuthModal>>]} AuthModalContext
 */

/**
 * @typedef {[Types.DashboardUser, React.Dispatch<React.SetStateAction<Types.DashboardUser>>]} UserContext
 */

/**
 * @typedef {[Types.DashboardTeam, React.Dispatch<React.SetStateAction<Types.DashboardTeam>>]} TeamContext
 */

/**
 * @typedef {[Types.DashboardNetworkState, React.Dispatch<React.SetStateAction<Types.DashboardNetworkState>>]} NetworkStateContext
 */

/**
 * @typedef {object} AppContextProps
 * @property {AuthModalContext} authModalCtx
 * @property {UserContext} userCtx
 * @property {TeamContext} teamCtx
 * @property {NetworkStateContext} dashboardNetworkStateCtx
 */

const AppContextProvider = ({ children }) => {
  /** @type {AuthModalContext} */
  const authModalCtx = useState({
    isOpen: false,
    mode: AUTH_MODAL_STATE.SIGNUP,
  });

  /** @type {UserContext} */
  const userCtx = useState();

  /** @type {TeamContext} */
  const teamCtx = useState()

  /** @type {NetworkStateContext} */
  const dashboardNetworkStateCtx = useState({
    accountIsLoading: true,
    accountIsErroring: false,
    teamIsLoading: true,
    teamIsErroring: false,
    reposAreLoading: true,
    reposAreErroring: false,
    apiDocsLoading: true,
    apiDocsErroring: false,
    confluenceSpacesLoading: false,
    confluenceSpacesErroring: false,
    confluenceSpaceUpdateLoading: false,
    confluenceSpaceUpdateErroring: false,
    apiDocsFetchCount: 0,
    teamRequestHasSucceededAtLeastOnce: false,
    reposRequestHasSucceededAtLeastOnce: false,
    apiDocsRequestHasSucceededAtLeastOnce: false,
  });

  /** @type {AppContextProps} */
  const ctx = {
    authModalCtx,
    userCtx,
    teamCtx,
    dashboardNetworkStateCtx,
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
