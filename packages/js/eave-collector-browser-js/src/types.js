// @ts-check
import { Tracker } from "./tracker.mjs";

/**
 * @typedef EaveConfiguration
 * @property {string} [eaveClientId]
 */

// /**
//  * @typedef Tracker
//  * this.xx = function() ...
//  * @property {(hookName: string) => ??} getHook
//  * @property {() => ??} getQuery
//  * @property {() => ??} getContent
//  * @property {() => ??} isUsingAlwaysUseSendBeacon
//  * @property {() => ??} getDomains
//  * @property {() => ??} getExcludedReferrers
//  * @property {() => ??} getConfigIdPageView
//  * @property {() => ??} getConfigDownloadExtensions
//  * @property {() => void} clearTrackedContentImpressions
//  * @property {() => ??} getTrackedContentImpressions
//  * @property {() => void} clearEnableTrackOnlyVisibleContent
//  * @property {() => void} disableLinkTracking
//  * @property {() => ??} getCustomPagePerformanceTiming
//  * @property {() => void} removeAllAsyncTrackersButFirst
//  * @property {() => ??} getConsentRequestsQueue
//  * @property {() => ??} getRequestQueue
//  * @property {() => ??} getJavascriptErrors
//  * @property {() => void} unsetPageIsUnloading
//  * @property {() => boolean} hasConsent
//  * @property {() => string} getVisitorId
//  * @property {(clientId: string) => ??} setEaveClientId
//  * @property {(trackerUrl: string) => void} setTrackerUrl
//  * @property {() => string} getTrackerUrl
//  * @property {() => string} getEaveUrl
//  * @property {(eaveUrl, siteId) => ??} addTracker
//  * @property {() => number} getSiteId
//  * @property {(siteId: number) => void} setSiteId
//  * @property {(key_or_obj, opt_value) => void} setCustomData
//  * @property {() => ??} getCustomData
//  * @property {(queryString) => ??} appendToTrackingUrl
//  * @property {(request) => ??} getRequest
//  * @property {(pluginName, pluginObj) => ??} addPlugin
//  * @property {(customDimensionId, value) => ??} setCustomDimension
//  * @property {(customDimensionId) => ??} getCustomDimension
//  * @property {(customDimensionId) => ??} deleteCustomDimension
//  * @property {(index, name, value, scope) => ??} setCustomVariable
//  * @property {(index, scope) => ??} getCustomVariable
//  * @property {(index, scope) => ??} deleteCustomVariable
//  * @property {(scope) => ??} deleteCustomVariables
//  * @property {() => ??} storeCustomVariablesInCookie
//  * @property {(delay) => ??} setLinkTrackingTimer
//  * @property {() => ??} getLinkTrackingTimer
//  * @property {(extensions) => ??} setDownloadExtensions
//  * @property {(extensions) => ??} addDownloadExtensions
//  * @property {(extensions) => ??} removeDownloadExtensions
//  * @property {(hostsAlias) => ??} setDomains
//  * @property {(excludedReferrers) => ??} setExcludedReferrers
//  * @property {() => ??} enableCrossDomainLinking
//  * @property {() => ??} disableCrossDomainLinking
//  * @property {() => ??} isCrossDomainLinkingEnabled
//  * @property {() => ??} getCrossDomainLinkingUrlParameter
//  * @property {(ignoreClasses) => ??} setIgnoreClasses
//  * @property {(method) => ??} setRequestMethod
//  * @property {(requestContentType) => ??} setRequestContentType
//  * @property {(title) => ??} setDocumentTitle
//  * @property {(pageView) => ??} setPageViewId
//  * @property {() => ??} getPageViewId
//  * @property {(downloadClasses) => ??} setDownloadClasses
//  * @property {(linkClasses) => ??} setLinkClasses
//  * @property {(excludedQueryParams) => ??} setExcludedQueryParams
//  * @property {() => ??} hasCookies
//  * @property {(cookieName) => ??} getCookie
//  * @property {() => ??} disableCookies
//  * @property {() => ??} areCookiesEnabled
//  * @property {() => ??} setCookieConsentGiven
//  * @property {() => ??} requireCookieConsent
//  * @property {() => ??} getRememberedCookieConsent
//  * @property {() => ??} forgetCookieConsentGiven
//  * @property {(hoursToExpire) => ??} rememberCookieConsentGiven
//  * @property {() => ??} deleteCookies
//  * @property {(enable) => ??} setDoNotTrack
//  * @property {() => ??} disableCampaignParameters
//  * @property {() => ??} enableCampaignParameters
//  * @property {() => ??} alwaysUseSendBeacon
//  * @property {() => ??} disableAlwaysUseSendBeacon
//  * @property {(element, enable) => ??} addListener
//  * @property {(enable) => ??} enableLinkTracking
//  * @property {(enable) => ??} enableButtonClickTracking
//  * @property {() => ??} enableRouteHistoryTracking
//  * @property {() => ??} enableJSErrorTracking
//  * @property {() => ??} disablePerformanceTracking
//  * @property {(heartBeatDelayInSeconds) => ??} enableHeartBeatTimer
//  * @property {() => ??} disableHeartBeatTimer
//  * @property {() => ??} killFrame
//  * @property {(url) => ??} redirectFile
//  * @property {(enable) => ??} setCountPreRendered
//  * @property {(idGoal, customRevenue, customData, callback) => ??} trackGoal
//  * @property {(sourceUrl, linkType, customData, callback) => ??} trackLink
//  * @property {() => ??} getNumTrackedPageViews
//  * @property {(customTitle, customData, callback) => ??} trackPageView
//  * @property {() => ??} disableBrowserFeatureDetection
//  * @property {() => ??} enableBrowserFeatureDetection
//  * @property {() => ??} trackAllContentImpressions
//  * @property {(domNode) => ??} trackContentImpressionsWithinNode
//  * @property {(domNode, contentInteraction) => ??} trackContentInteractionNode
//  * @property {() => ??} logAllContentBlocksOnPage
//  * @property {(sku, name, category, price) => ??} setEcommerceView
//  * @property {() => ??} enableFormTracking
//  * @property {() => ??} getEcommerceItems
//  * @property {(sku, name, category, price, quantity) => ??} addEcommerceItem
//  * @property {(sku) => ??} removeEcommerceItem
//  * @property {() => ??} clearEcommerceCart
//  * @property {(grandTotal) => ??} trackEcommerceCartUpdate
//  * @property {(request, customData, callback, pluginMethod) => ??} trackRequest
//  * @property {() => ??} ping
//  * @property {() => ??} disableQueueRequest
//  * @property {(interval) => ??} setRequestQueueInterval
//  * @property {(request, isFullRequest) => ??} queueRequest
//  * @property {() => ??} isConsentRequired
//  * @property {() => ??} getRememberedConsent
//  * @property {() => ??} hasRememberedConsent
//  * @property {() => ??} requireConsent
//  * @property {(setCookieConsent) => ??} setConsentGiven
//  * @property {(hoursToExpire) => ??} rememberConsentGiven
//  * @property {(hoursToExpire) => ??} forgetConsentGiven
//  * @property {() => ??} isUserOptedOut
//  * @property {() => ??} forgetUserOptOut
//  * @property {() => ??} enableFileTracking
//  *
//  * function xxx() ...
//  * @property {(checkOnScroll, timeIntervalInMs) => ??} enableTrackOnlyVisibleContent
//  * @property {(customRequestContentProcessingLogic)  => ??} setCustomRequestProcessing
//  * @property {(networkTimeInMs, serverTimeInMs, transferTimeInMs, domProcessingTimeInMs, domCompletionTimeInMs, onloadTimeInMs) => ??} setPagePerformanceTiming
//  * @property {(checkOnScroll, timeIntervalInMs) => ??} trackVisibleContentImpressions
//  * @property {(contentName, contentPiece, contentTarget) => ??} trackContentImpression
//  * @property {(contentInteraction, contentName, contentPiece, contentTarget) => ??} trackContentInteraction
//  * @property {(category, action, name, value, customData, callback) => ??} trackEvent
//  * @property {(keyword, category, resultsCount, customData) => ??} trackSiteSearch
//  * @property {(callback) => ??} makeSureThereIsAGapAfterFirstTrackingRequestToPreventMultipleVisitorCreation
//  * @property {(anyNode, interaction, fallbackTarget) => ??} getContentInteractionToRequestIfPossible
//  * @property {(contentNodes) => ??} getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet
//  * @property {(contentName, contentPiece, contentTarget) => ??} buildContentImpressionRequest
//  * @property {(checkOnScroll, timeIntervalInMs, tracker) => ??} enableTrackOnlyVisibleContent
//  * @property {(url: string) => string} getPathName
//  * @property {(referrerUrl: string) => boolean} isReferrerExcluded
//  * @property {(request: string) => boolean} shouldForcePost
//  * @property {(request: string, callback: function, fallbackToGet: boolean) => boolean} sendPostRequestViaSendBeacon
//  * @property {(request, callback, fallbackToGet) => ??} sendXmlHttpRequest
//  * @property {(delay) => ??} setExpireDateTime
//  * @property {() => ??} heartBeatOnFocus
//  * @property {() => ??} hadWindowMinimalFocusToConsiderViewed
//  * @property {() => ??} heartBeatOnBlur
//  * @property {() => ??} heartBeatOnVisible
//  * @property {() => ??} setUpHeartBeat
//  * @property {() => ??} processClientHintsQueue
//  * @property {() => ??} detectBrowserFeatures
//  * @property {(request) => ??} injectBrowserFeaturesAndClientHints
//  * @property {() => ??} supportsClientHints
//  * @property {(callback) => ??} detectClientHints
//  * @property {() => ??} generateBrowserSpecificId
//  * @property {() => ??} makeCrossDomainDeviceId
//  * @property {(hostName) => ??} isSiteHostName
//  * @property {(host, path) => ??} isSiteHostPath
//  * @property {(url) => ??} purify
//  * @property {(request, delay, callback) => ??} sendRequest
//  * @property {(requests) => ??} canSendBulkRequest
//  * @property {(requests, delay) => ??} sendBulkRequest
//  * @property {(request) => ??} appendAvailablePerformanceMetrics
//  * @property {(url) => ??} hasIgnoreReferrerParameter
//  * @property {() => ??} maybeSetReferrerAttribution
//  * @property {(customData) => ??} buildRequest
//  * @property {(request, customData, pluginMethod) => ??} getRequest
//  * @property {(customTitle, customData, callback) => ??} logPageView
//  * @property {(configClasses, defaultClass) => ??} getClassesRegExp
//  * @property {(url) => ??} startsUrlWithTrackerUrl
//  * @property {(className, href, isInLink, hasDownloadAttribute) => ??} getLinkType
//  * @property {(isTargetNode, target) => ??} getTargetNode
//  * @property {(sourceElement) => ??} getLinkIfShouldBeProcessed
//  * @property {(interaction, name, piece, target) => ??} buildContentInteractionRequest
//  * @property {(contentNode, interactedNode) => ??} isNodeAuthorizedToTriggerInteraction
//  * @property {(contentBlock) => ??} wasContentImpressionAlreadyTracked
//  * @property {(targetNode) => ??} trackContentImpressionClickInteraction
//  * @property {(contentNodes) => ??} setupInteractionsTracking
//  * @property {(contents, contentNodes) => ??} buildContentImpressionsRequests
//  * @property {(contentNodes) => ??} getContentImpressionsRequestsFromNodes
//  * @property {(node, contentInteraction) => ??} buildContentInteractionRequestNode
//  * @property {(category, action, name, value) => ??} buildEventRequest
//  * @property {(category, action, name, value, customData, callback) => ??} logEvent
//  * @property {(keyword, category, resultsCount, customData) => ??} logSiteSearch
//  * @property {(idGoal, customRevenue, customData, callback) => ??} logGoal
//  * @property {(url, linkType, customData, callback, sourceElement) => ??} logLink
//  * @property {(prefix, propertyName) => ??} prefixPropertyName
//  * @property {(callback) => ??} trackCallback
//  * @property {() => ??} getCrossDomainVisitorId
//  * @property {(element) => ??} replaceHrefForCrossDomainLink
//  * @property {(element) => ??} isLinkToDifferentDomainButSameEaveWebsite
//  * @property {(sourceElement) => ??} processButtonClick
//  * @property {(sourceElement) => ??} processLinkClick
//  * @property {(event) => ??} getKeyCodeFromEvent
//  * @property {(event) => ??} getNameOfClickedMouseButton
//  * @property {(event) => ??} getTargetElementFromEvent
//  * @property {(nodeName) => ??} isLinkNode
//  * @property {(nodeName) => ??} isButtonNode
//  * @property {(enable) => ??} clickHandler
//  * @property {(element, enable, useCapture) => ??} addClickListener
//  * @property {(hookName, userHook) => ??} registerHook
//  * @property {() => ??} getAttributionReferrerTimestamp
//  * @property {() => ??} getAttributionReferrerUrl
//  * @property {() => ??} getAttributionReferrerQueryParams
//  * @property {() => ??} loadCustomVariables
//  * @property {() => ??} getCurrentUrl
//  * @property {() => ??} refreshConsentStatus
//  * @property {() => ??} setTrackingCookies
//  *
//  * this.xx = xxx;
//  * @property {} hook
//  * @property {() => ??} buildContentImpressionRequest
//  * @property {() => ??} buildContentInteractionRequest
//  * @property {() => ??} buildContentInteractionRequestNode
//  * @property {() => ??} buildContentImpressionsRequests
//  * @property {(callback: function) => void} trackCallbackOnLoad
//  * @property {(callback: function) => void} trackCallbackOnReady
//  * @property {() => ??} wasContentImpressionAlreadyTracked
//  * @property {() => ??} setupInteractionsTracking
//  * @property {() => ??} internalIsNodeVisible
//  * @property {() => string} getAttributionReferrerTimestamp
//  * @property {() => string} getAttributionReferrerUrl
//  * @property {() => string} getAttributionReferrerQueryParams
//  * @property {} getCurrentUrl
//  * @property {} optUserOut
//  * @property {} setTrackingCookies
//  * @property {} getContentImpressionsRequestsFromNodes
//  * @property {() => ??} getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet
//  * @property {() => ??} appendContentInteractionToRequestIfPossible
//  * @property {} trackContentImpressionClickInteraction
//  * @property {() => ??} isNodeAuthorizedToTriggerInteraction
// */

/**
 * @typedef EaveTrackerManager
 * @property {boolean} initialized
 * @property {(event: string, handler: function) => void} on
 * @property {(event: string, handler: function) => void} off
 * @property {(event: string, extraParameters?: object, context?: object) => void} trigger
 * @property {(pluginName: string, pluginObj: object) => void} addPlugin
 * @property {(eaveUrl?: string, siteId?: number) => Tracker} getTracker
 * @property {() => Tracker[]} getAsyncTrackers
 * @property {(eaveUrl: string, siteId: number) => Tracker} addTracker
 * @property {(eaveUrl?: string, siteId?: number) => Tracker} getAsyncTracker
 * @property {() => void} retryMissedPluginCalls
 */

/**
 * @typedef EaveDOMManager
 * @property {(element: HTMLElement, eventType: string, eventHandler: function, useCapture: boolean) => void} addEventListener
 * @property {(callback: function) => void} onLoad
 * @property {(callback: function) => void} onReady
 * @property {(node: HTMLElement) => boolean} isNodeVisible
 * @property {(node: HTMLElement) => boolean} isOrWasNodeVisible
 */

/**
 * @typedef GlobalEaveProperties
 * @property {number} [expireDateTime]
 * @property {string[][]} settings
 * @property {{[key: string]: any}} plugins
 * @property {{[key: string]: any}} [eventHandlers]
 * @property {any[]} asyncTrackers
 * @property {any[]} missedPluginTrackerCalls
 * @property {number} coreConsentCounter
 * @property {number} coreHeartBeatCounter
 * @property {number} trackerIdCounter
 * @property {boolean} isPageUnloading
 * @property {string} trackerInstallCheckNonce
 * @property {any[]} [trackerPluginAsyncInit]
 * @property {any} [tracker]
 * @property {() => void} [trackerAsyncInit]
 * @property {EaveTrackerManager} [eave]
 */

/**
 *  @typedef {Window & EaveConfiguration & { eave: GlobalEaveProperties }} GlobalEaveWindow
 */

/**
 * @typedef {(p: { request: string, trackerUrl: string, success: boolean, isSendBeacon?: boolean, xhr?: any }) => void} RequestCallback
 */
export const Types  = {};