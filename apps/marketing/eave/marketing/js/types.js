/**
 * @typedef {import("@material-ui/core").Theme} Theme
 */

/**
 * @typedef {Window & typeof globalThis & { eave: { cookieDomain: string, apiBase: string, assetBase: string } }} GlobalEave
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/github-repos.js").GithubRepo} GithubRepo
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/github-repos.js").GetGithubReposResponseBody} GetGithubReposResponseBody
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/github-repos.js").UpdateGithubReposRequestBody} UpdateGithubReposRequestBody
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/github-repos.js").GithubRepoUpdateInput} GithubRepoUpdateInput
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/github-documents.js").GetGithubDocumentsResponseBody} GetGithubDocumentsResponseBody
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/github-documents.js").GithubDocument} GithubDocument
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/team.js").Team} Team
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/account.js").AuthenticatedAccount} AuthenticatedAccount
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/integrations.js").Integrations} Integrations
 */

/**
 * @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/team.js").GetTeamResponseBody} GetTeamResponseBody
 */

/** @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/models/api-documentation-jobs.js").ApiDocumentationJob} ApiDocumentationJob */

/** @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/api-documentation-jobs.js").GetApiDocumentationJobsResponseBody} GetApiDocumentationJobsResponseBody */

/** @typedef {import("../../../../../libs/eave-stdlib-ts/src/core-api/operations/api-documentation-jobs.js").GetApiDocumentationJobsRequestBody} GetApiDocumentationJobsRequestBody */

/**
 * @typedef {object} DashboardTeam
 * @property {boolean} [inlineCodeDocsEnabled]
 * @property {boolean} [apiDocsEnabled]
 * @property {string} [id]
 * @property {string} [name]
 * @property {GithubDocument[]} [apiDocs]
 * @property {Integrations} [integrations]
 * @property {GithubRepo[]} [repos]
 * @property {ApiDocumentationJob[]} [apiDocsJobs]
 */

/**
 * @typedef {object} DashboardNetworkState
 * @property {boolean} accountIsLoading
 * @property {boolean} accountIsErroring
 * @property {boolean} teamIsLoading
 * @property {boolean} teamIsErroring
 * @property {boolean} reposAreLoading
 * @property {boolean} reposAreErroring
 * @property {boolean} apiDocsLoading
 * @property {boolean} apiDocsErroring
 * @property {boolean} apiDocsJobStatusLoading
 * @property {boolean} apiDocsJobStatusErroring
 * @property {number} apiDocsFetchCount
 * @property {boolean} teamRequestHasSucceededAtLeastOnce
 * @property {boolean} reposRequestHasSucceededAtLeastOnce
 * @property {boolean} apiDocsRequestHasSucceededAtLeastOnce
 */

/**
 * @typedef {object} DashboardUser
 * @property {AuthenticatedAccount} [account]
 */

/**
 * @typedef {object} AuthModal
 * @property {boolean} isOpen
 * @property {string} mode
 */

/** @typedef {{ teamRepoIds: string[], enabledRepoIds: string[], feature: string }} FeatureStateParams */

/**
 * @typedef {object} FeatureDescriptionContent
 * @property {string} [title]
 * @property {string} [subtitle]
 * @property {string | null} [supportSubheader]
 * @property {string[]} [languages]
 */

export const Types = {};
