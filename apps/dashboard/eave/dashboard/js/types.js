/**
 * @typedef {import("@material-ui/core").Theme} Theme
 */

/**
 * @typedef {Window & typeof globalThis & { eave: { cookieDomain: string, rootDomain: string, apiBase: string, assetBase: string } }} GlobalEaveWindow
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/team.js").Team} Team
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/account.js").AuthenticatedAccount} AuthenticatedAccount
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/team.js").GetTeamResponseBody} GetTeamResponseBody
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/virtual-event.js").GetVirtualEventsResponseBody} GetVirtualEventsResponseBody
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/virtual-event.js").VirtualEvent} VirtualEvent
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/virtual-event.js").VirtualEventQueryInput} VirtualEventQueryInput
 */

/**
 * @typedef {object} DashboardTeam
 * @property {string} [id]
 * @property {string} [name]
 * @property {VirtualEvent[]} [virtualEvents]
 */

/**
 * @typedef {object} DashboardNetworkState
 * @property {boolean} teamIsLoading
 * @property {boolean} teamIsErroring
 * @property {boolean} teamRequestHasSucceededAtLeastOnce
 */

/**
 * @typedef {object} GlossaryNetworkState
 * @property {boolean} virtualEventsAreLoading
 * @property {boolean} virtualEventsAreErroring
 */

/**
 * @typedef {object} VirtualEvent
 * @property {string} name
 * @property {string} description
 * @property {string[]} fields
 */

export const Types = {};
