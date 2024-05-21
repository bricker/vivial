/**
 * Log all content pieces
 *
 * @param {any} contents
 * @param {Element[]} contentNodes
 * @returns {string[]}
 */
function buildContentImpressionsRequests(contents, contentNodes) {
  if (!contents || !contents.length) {
    return [];
  }

  let index;
  let request;

  for (index = 0; index < contents.length; index++) {
    if (wasContentImpressionAlreadyTracked(contents[index])) {
      contents.splice(index, 1);
      index--;
    } else {
      trackedContentImpressions.push(contents[index]);
    }
  }

  if (!contents || !contents.length) {
    return [];
  }

  setupInteractionsTracking(contentNodes);

  const requests = [];

  for (index = 0; index < contents.length; index++) {
    request = getRequest(
      content.buildImpressionRequestParams(
        contents[index].name,
        contents[index].piece,
        contents[index].target,
      ),
      undefined,
      "contentImpressions",
    );

    if (request) {
      requests.push(request);
    }
  }

  return requests;
}

/**
 * Log all content pieces
 *
 * @param {Element[]} contentNodes
 * @returns {string[]}
 */
function getContentImpressionsRequestsFromNodes(contentNodes) {
  const contents = content.collectContent(contentNodes);

  return buildContentImpressionsRequests(contents, contentNodes);
}

/**
 * Log currently visible content pieces
 *
 * @param {HTMLElement[]} contentNodes
 * @returns {string[]}
 */
function getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
  contentNodes,
) {
  if (!contentNodes || !contentNodes.length) {
    return [];
  }

  let index;

  for (index = 0; index < contentNodes.length; index++) {
    if (!content.isNodeVisible(contentNodes[index])) {
      contentNodes.splice(index, 1);
      index--;
    }
  }

  if (!contentNodes || !contentNodes.length) {
    return [];
  }

  return getContentImpressionsRequestsFromNodes(contentNodes);
}

/**
 * @param {string} contentName
 * @param {any} contentPiece
 * @param {any} contentTarget
 * @returns {string}
 */
function buildContentImpressionRequest(
  contentName,
  contentPiece,
  contentTarget,
) {
  const params = content.buildImpressionRequestParams(
    contentName,
    contentPiece,
    contentTarget,
  );

  return getRequest(params, null, "contentImpression");
}


/**
 * @param {any} contentBlock
 * @returns {boolean}
 */
function wasContentImpressionAlreadyTracked(contentBlock) {
  if (!trackedContentImpressions || !trackedContentImpressions.length) {
    return false;
  }

  var index, trackedContent;

  for (index = 0; index < trackedContentImpressions.length; index++) {
    trackedContent = trackedContentImpressions[index];

    if (
      trackedContent &&
      trackedContent.name === contentBlock.name &&
      trackedContent.piece === contentBlock.piece &&
      trackedContent.target === contentBlock.target
    ) {
      return true;
    }
  }

  return false;
}

/**
 * Scans the entire DOM for all content blocks and tracks all impressions once the DOM ready event has
 * been triggered.
 *
 * If you only want to track visible content impressions have a look at `trackVisibleContentImpressions()`.
 * We do not track an impression of the same content block twice if you call this method multiple times
 * unless `trackPageView()` is called meanwhile. This is useful for single page applications.
 *
 * @noreturn
 */
this.trackAllContentImpressions = function () {
  trackCallback(function () {
    h.trackCallbackOnReady(function () {
      // we have to wait till DOM ready
      const contentNodes = content.findContentNodes();
      const requests = getContentImpressionsRequestsFromNodes(contentNodes);

      requestQueue.pushMultiple(requests);
    });
  });
};

/**
 * Scans the entire DOM for all content blocks as soon as the page is loaded. It tracks an impression
 * only if a content block is actually visible. Meaning it is not hidden and the content is or was at
 * some point in the viewport.
 *
 * If you want to track all content blocks have a look at `trackAllContentImpressions()`.
 * We do not track an impression of the same content block twice if you call this method multiple times
 * unless `trackPageView()` is called meanwhile. This is useful for single page applications.
 *
 * Once you have called this method you can no longer change `checkOnScroll` or `timeIntervalInMs`.
 *
 * If you do want to only track visible content blocks but not want us to perform any automatic checks
 * as they can slow down your frames per second you can call `trackVisibleContentImpressions()` or
 * `trackContentImpressionsWithinNode()` manually at  any time to rescan the entire DOM for newly
 * visible content blocks.
 * o Call `trackVisibleContentImpressions(false, 0)` to initially track only visible content impressions
 * o Call `trackVisibleContentImpressions()` at any time again to rescan the entire DOM for newly visible content blocks or
 * o Call `trackContentImpressionsWithinNode(node)` at any time to rescan only a part of the DOM for newly visible content blocks
 *
 * @param {boolean} [checkOnScroll=true] Optional, you can disable rescanning the entire DOM automatically
 *                                     after each scroll event by passing the value `false`. If enabled,
 *                                     we check whether a previously hidden content blocks became visible
 *                                     after a scroll and if so track the impression.
 *                                     Note: If a content block is placed within a scrollable element
 *                                     (`overflow: scroll`), we can currently not detect when this block
 *                                     becomes visible.
 * @param {number} [timeIntervalInMs=750] Optional, you can define an interval to rescan the entire DOM
 *                                     for new impressions every X milliseconds by passing
 *                                     for instance `timeIntervalInMs=500` (rescan DOM every 500ms).
 *                                     Rescanning the entire DOM and detecting the visible state of content
 *                                     blocks can take a while depending on the browser and amount of content.
 *                                     In case your frames per second goes down you might want to increase
 *                                     this value or disable it by passing the value `0`.
 *
 * @noreturn
 */
this.trackVisibleContentImpressions = function (
  checkOnScroll = true,
  timeIntervalInMs = 750,
) {

  enableTrackOnlyVisibleContent(checkOnScroll, timeIntervalInMs, this);

  trackCallback(function () {
    h.trackCallbackOnLoad(function () {
      // we have to wait till CSS parsed and applied
      const contentNodes = content.findContentNodes();
      const requests =
        getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
          contentNodes,
        );

      requestQueue.pushMultiple(requests);
    });
  });
};

/**
 * Tracks a content impression using the specified values. You should not call this method too often
 * as each call causes an XHR tracking request and can slow down your site or your server.
 *
 * @param {string} contentName  For instance "Ad Sale".
 * @param {string} [contentPiece='Unknown'] For instance a path to an image or the text of a text ad.
 * @param {string} [contentTarget] For instance the URL of a landing page.
 * @noreturn
 */
this.trackContentImpression = function (
  contentName,
  contentPiece,
  contentTarget,
) {
  contentName = h.trim(contentName);
  contentPiece = h.trim(contentPiece);
  contentTarget = h.trim(contentTarget);

  if (!contentName) {
    return;
  }

  contentPiece = contentPiece || "Unknown";

  trackCallback(function () {
    const request = buildContentImpressionRequest(
      contentName,
      contentPiece,
      contentTarget,
    );
    requestQueue.push(request);
  });
};

/**
 * Scans the given DOM node and its children for content blocks and tracks an impression for them if
 * no impression was already tracked for it. If you have called `trackVisibleContentImpressions()`
 * upfront only visible content blocks will be tracked. You can use this method if you, for instance,
 * dynamically add an element using JavaScript to your DOM after we have tracked the initial impressions.
 *
 * @param {Element} domNode
 * @noreturn
 */
this.trackContentImpressionsWithinNode = function (domNode) {
  trackCallback(function () {
    if (isTrackOnlyVisibleContentEnabled) {
      h.trackCallbackOnLoad(function () {
        // we have to wait till CSS parsed and applied
        const contentNodes = content.findContentNodesWithinNode(domNode);

        const requests =
          getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
            contentNodes,
          );
        requestQueue.pushMultiple(requests);
      });
    } else {
      h.trackCallbackOnReady(function () {
        // we have to wait till DOM ready
        const contentNodes = content.findContentNodesWithinNode(domNode);

        const requests = getContentImpressionsRequestsFromNodes(contentNodes);
        requestQueue.pushMultiple(requests);
      });
    }
  });
};