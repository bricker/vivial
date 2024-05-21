
/**
 * This modifies the passed-in element!
 *
 * @param {Element} element
 */
function replaceHrefForCrossDomainLink(element) {
  if (!element) {
    return;
  }

  if (!query.hasNodeAttribute(element, "href")) {
    return;
  }

  let link = query.getAttributeValueFromNode(element, "href");

  if (!link || startsUrlWithTrackerUrl(link)) {
    return;
  }

  if (!trackerInstance.getVisitorId()) {
    return; // cookies are disabled.
  }

  // we need to remove the parameter and add it again if needed to make sure we have latest timestamp
  // and visitorId (eg userId might be set etc)
  link = h.removeUrlParameter(link, configVisitorIdUrlParameter);

  const crossDomainVisitorId = getCrossDomainVisitorId();

  link = h.addUrlParameter(
    link,
    configVisitorIdUrlParameter,
    crossDomainVisitorId,
  );

  query.setAnyAttribute(element, "href", link);
}

/**
 * @param {HTMLLinkElement} element
 *
 * @returns {boolean}
 */
function isLinkToDifferentDomainButSameEaveWebsite(element) {
  const targetLink = query.getAttributeValueFromNode(element, "href");

  if (!targetLink) {
    return false;
  }

  const url = new URL(targetLink);

  var isOutlink =
    targetLink.indexOf("//") === 0 ||
    targetLink.indexOf("http://") === 0 ||
    targetLink.indexOf("https://") === 0;

  if (!isOutlink) {
    return false;
  }

  const originalSourcePath = url.pathname || getPathName(element.href);
  const originalSourceHostName = (
    url.hostname || h.getHostName(element.href)
  ).toLowerCase();

  if (isSiteHostPath(originalSourceHostName, originalSourcePath)) {
    // we could also check against config cookie domain but this would require that other website
    // sets actually same cookie domain and we cannot rely on it.
    if (!h.isSameHost(domainAlias, h.domainFixup(originalSourceHostName))) {
      return true;
    }

    return false;
  }

  return false;
}

/**
 * Get anchor tag data if the link click is not to be ignored.
 *
 * @param {HTMLElement} sourceElement
 *
 * @returns {{type: string | number, href: string} | undefined}
 */
function getLinkIfShouldBeProcessed(sourceElement) {
  // @ts-ignore - force-cast to HTMLLinkElement
  const /** @type {HTMLLinkElement | undefined} */ _sourceElement = getTargetNode(isLinkNode, sourceElement);

  if (!_sourceElement) {
    return;
  }

  if (!query.hasNodeAttribute(_sourceElement, "href")) {
    return;
  }

  if (!h.isDefined(_sourceElement.href)) {
    return;
  }

  const url = new URL(_sourceElement.href);
  const originalSourcePath = url.pathname || getPathName(_sourceElement.href);

  // browsers, such as Safari, don't downcase hostname and href
  const originalSourceHostName = url.hostname || h.getHostName(_sourceElement.href);
  const sourceHostName = originalSourceHostName.toLowerCase();
  const sourceHref = _sourceElement.href.replace(
    originalSourceHostName,
    sourceHostName,
  );

  // browsers, such as Safari, don't downcase hostname and href
  const scriptProtocol = new RegExp(
    "^(javascript|vbscript|jscript|mocha|livescript|ecmascript|mailto|tel):",
    "i",
  );

  if (!scriptProtocol.test(sourceHref)) {
    if (!_sourceElement.className) {
      return;
    }
    // track outlinks and all downloads
    const linkType = getLinkType(
      _sourceElement.className,
      sourceHref,
      isSiteHostPath(sourceHostName, originalSourcePath),
      query.hasNodeAttribute(_sourceElement, "download"),
    );

    if (linkType) {
      return {
        type: linkType,
        href: sourceHref,
      };
    }
  }

  // track all link types (including internal)
  const linkType = getLinkType(
    sourceElement.className,
    sourceHref,
    isSiteHostPath(sourceHostName, originalSourcePath),
    query.hasNodeAttribute(sourceElement, "download"),
  );

  return {
    type: linkType,
    href: sourceHref,
  };
}


/**
 * Determines what type of link an anchor element is from various attributes.
 *
 * @param {string} className
 * @param {string} href
 * @param {boolean} isInLink
 * @param {boolean} hasDownloadAttribute
 *
 * @returns {number | string}
 */
function getLinkType(className, href, isInLink, hasDownloadAttribute) {
  if (isInLink) {
    return "internal";
  }

  // does class indicate whether it is an (explicit/forced) outlink or a download?
  const downloadPattern = getClassesRegExp(configDownloadClasses, "download");

  // does file extension indicate that it is a download?
  const downloadExtensionsPattern = new RegExp(
    "\\.(" + configDownloadExtensions.join("|") + ")([?&#]|$)",
    "i",
  );

  if (
    hasDownloadAttribute ||
    downloadPattern.test(className) ||
    downloadExtensionsPattern.test(href)
  ) {
    return "download";
  }

  // browsers, such as Safari, don't downcase hostname and href
  const scriptProtocol = new RegExp(
    "^(javascript|vbscript|jscript|mocha|livescript|ecmascript):",
    "i",
  );
  if (scriptProtocol.test(href)) {
    return "script";
  }

  const mailProtocol = new RegExp("^mailto:", "i");
  if (mailProtocol.test(href)) {
    return "email";
  }

  const telephoneProtocol = new RegExp("^tel:", "i");
  if (telephoneProtocol.test(href)) {
    return "telephone";
  }

  return "external";
}

/**
 * Manually log a click from your own code
 *
 * @param {string} sourceUrl
 * @param {string} linkType
 * @param {object} customData
 * @param {Types.RequestCallback | null} callback
 *
 * @noreturn
 */
this.trackLink = function (sourceUrl, linkType, customData, callback) {
  trackCallback(function () {
    logLink(sourceUrl, linkType, customData, undefined, callback);
  });
};

  /**
 * Track button element clicks
 *
 * @param {boolean} enable
 *
 * @noreturn
 */
this.enableButtonClickTracking = function (enable) {
  if (buttonClickTrackingEnabled) {
    return;
  }
  buttonClickTrackingEnabled = true;

  if (!clickListenerInstalled) {
    clickListenerInstalled = true;
    h.trackCallbackOnReady(function () {
      const element = document.body;
      addClickListener(element, enable, true);
    });
  }
};

/**
 * Track img element clicks
 */
this.enableImageClickTracking = function (enable) {
  if (imageClickTrackingEnabled) {
    return;
  }
  imageClickTrackingEnabled = true;

  if (!clickListenerInstalled) {
    clickListenerInstalled = true;
    h.trackCallbackOnReady(function () {
      var element = globalThis.eave.documentAlias.body;
      addClickListener(element, enable, true);
    });
  }
};

/**
 * Install link tracker.
 *
 * If you change the DOM of your website or web application eave will automatically detect links
 * that were added newly.
 *
 * The default behaviour is to use actual click events. However, some browsers
 * (e.g., Firefox, Opera, and Konqueror) don't generate click events for the middle mouse button.
 *
 * To capture more "clicks", the pseudo click-handler uses mousedown + mouseup events.
 * This is not industry standard and is vulnerable to false positives (e.g., drag events).
 *
 * There is a Safari/Chrome/Webkit bug that prevents tracking requests from being sent
 * by either click handler.  The workaround is to set a target attribute (which can't
 * be "_self", "_top", or "_parent").
 *
 * @see https://bugs.webkit.org/show_bug.cgi?id=54783
 *
 * @param {boolean} enable Defaults to true.
 *                    * If "true", use pseudo click-handler (treat middle click and open contextmenu as
 *                    left click). A right click (or any click that opens the context menu) on a link
 *                    will be tracked as clicked even if "Open in new tab" is not selected.
 *                    * If "false" (default), nothing will be tracked on open context menu or middle click.
 *                    The context menu is usually opened to open a link / download in a new tab
 *                    therefore you can get more accurate results by treat it as a click but it can lead
 *                    to wrong click numbers.
 *
 * @noreturn
 */
this.enableLinkTracking = function (enable) {
  if (linkTrackingEnabled) {
    return;
  }
  linkTrackingEnabled = true;

  if (!clickListenerInstalled) {
    clickListenerInstalled = true;
    h.trackCallbackOnReady(function () {
      const element = document.body;
      addClickListener(element, enable, true);
    });
  }
};

/**
 * Handle click event
 *
 * @param {boolean} enable
 *
 * @returns {(event: MouseEvent) => void}
 */
function clickHandler(enable) {
  /*
    List of element tracking to check for in priority order.
    This click handler will only fire 1 event per click, so higher
    priority tracked elements should appear earlier in the list.

    e.g.
    linkTracking comes before buttonClickTracking.
    Therefore, we expect clicking on the button element of
    `<a href="..."><button>click!</button></a>`
    Will trigger a link click event rather than a button click event.
    */
    const trackers = [
    {
      trackingEnabled: () => linkTrackingEnabled,
      nodeFilter: isLinkNode,
      clickProcessor: processLinkClick,
    },
    {
      trackingEnabled: () => buttonClickTrackingEnabled,
      nodeFilter: isButtonNode,
      clickProcessor: processButtonClick,
    },
    {
      trackingEnabled: () => imageClickTrackingEnabled,
      nodeFilter: (nodeName) => nodeName === "IMG",
      clickProcessor: (sourceElement) =>
        logEvent(
          "click",
          "img",
          "img tag clicked",
          sourceElement.id,
          {
            src: sourceElement.src,
            full_html: sourceElement.outerHTML,
          },
          undefined,
        ),
    },
  ];
  var activeTracker;

  /**
   * From a click listener callback event, get a target element we
   * are tracking, if any.
   *
   * @param {Event} event h.addEventListener callback param
   */
  function getClickTarget(event) {
    const initialTarget = getTargetElementFromEvent(event);

    /*
      loop over all enabled element trackers, returning the first
      (aka highest priority) node found
      */
    let targetNode = undefined;
    var i;
    for (i = 0; i < trackers.length; i++) {
      const targetTrackingEnabled = trackers[i].trackingEnabled();
      const targetNodeFilter = trackers[i].nodeFilter;
      if (targetTrackingEnabled) {
        targetNode = getTargetNode(targetNodeFilter, initialTarget);
        if (targetNode) {
          // TODO: separate this side affect
          activeTracker = trackers[i];
          break;
        }
      }
    }
    return targetNode;
  }

  return function (event) {
    const target = getClickTarget(event);
    // we arent tracking the clicked element(s)
    if (!target || !activeTracker) {
      return;
    }

    const button = getNameOfClickedMouseButton(event);

    if (event.type === "click") {
      let ignoreClick = false;
      if (enable && button === "middle") {
        // if enabled, we track middle clicks via mouseup
        // some browsers (eg chrome) trigger click and mousedown/up events when middle is clicked,
        // whereas some do not. This way we make "sure" to track them only once, either in click
        // (default) or in mouseup (if enable == true)
        ignoreClick = true;
      }

      if (target && !ignoreClick) {
        activeTracker.clickProcessor(target);
      }
    } else if (event.type === "mousedown") {
      if (button === "middle" && target) {
        lastButton = button;
        lastTarget = target;
      } else {
        lastButton = null;
        lastTarget = null;
      }
    } else if (event.type === "mouseup") {
      if (button === lastButton && target === lastTarget) {
        activeTracker.clickProcessor(target);
      }
      lastButton = null;
      lastTarget = null;
    } else if (event.type === "contextmenu") {
      activeTracker.clickProcessor(target);
    }
  };
}

/**
 * Add click listener to a DOM element
 *
 * @param {Element} element
 * @param {boolean} enable
 * @param {boolean} useCapture
 */
function addClickListener(element, enable, useCapture) {
  const enableType = typeof enable;
  if (enableType === "undefined") {
    enable = true;
  }

  element.addEventListener("click", clickHandler(enable), useCapture);

  if (enable) {
    element.addEventListener("mouseup", clickHandler(enable), useCapture);
    element.addEventListener(
      "mousedown",
      clickHandler(enable),
      useCapture,
    );
    element.addEventListener(
      "contextmenu",
      clickHandler(enable),
      useCapture,
    );
  }
}

/**
 * @param {string} nodeName
 *
 * @returns {boolean}
 */
function isLinkNode(nodeName) {
  return nodeName === "A" || nodeName === "AREA";
}

/**
 * @param {string} nodeName
 *
 * @returns {boolean}
 */
function isButtonNode(nodeName) {
  return nodeName === "BUTTON";
}

/**
 * Process clicks on button elements
 *
 * @param {HTMLElement} sourceElement
 */
function processButtonClick(sourceElement) {
  // TODO improve data values passed...
  // fire event
  logEvent(
    "button",
    "click",
    "button click",
    sourceElement.innerText,
    null,
    null,
  );
}

/**
 * Process clicks on link elements
 *
 * @param {HTMLElement} sourceElement
 */
function processLinkClick(sourceElement) {
  const link = getLinkIfShouldBeProcessed(sourceElement);
  if (link && link.type) {
    link.href = h.safeDecodeWrapper(link.href);
    logLink(link.href, link.type, undefined, sourceElement);
  }
}

/**
 * https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/button
 *
 * @param {MouseEvent} event
 *
 * @returns {string}
 */
function getNameOfClickedMouseButton(event) {
  switch (event.button) {
    case 0:
      return "primary";
    case 1:
      return "aux";
    case 2:
      return "secondary";
    case 3:
      return "fourth";
    case 4:
      return "fifth";
    default:
      return "unknown";
  }
}