import './globals.mjs';
import * as h from "./helpers.mjs";
import query from "./query.mjs";
import { isVisible } from "./visibility.mjs";

export default {
  CONTENT_ATTR: "data-track-content",
  CONTENT_CLASS: "eaveTrackContent",
  CONTENT_NAME_ATTR: "data-content-name",
  CONTENT_PIECE_ATTR: "data-content-piece",
  CONTENT_PIECE_CLASS: "eaveContentPiece",
  CONTENT_TARGET_ATTR: "data-content-target",
  CONTENT_TARGET_CLASS: "eaveContentTarget",
  CONTENT_IGNOREINTERACTION_ATTR: "data-content-ignoreinteraction",
  CONTENT_IGNOREINTERACTION_CLASS: "eaveContentIgnoreInteraction",
  location: undefined,

  findContentNodes: function () {
    var cssSelector = "." + this.CONTENT_CLASS;
    var cssSelector2 = "." + this.LEGACY_CONTENT_CLASS;
    var attrSelector = "[" + this.CONTENT_ATTR + "]";
    var contentNodes = query.findMultiple([
      cssSelector,
      cssSelector2,
      attrSelector,
    ]);

    return contentNodes;
  },
  findContentNodesWithinNode: function (node) {
    if (!node) {
      return [];
    }

    // NOTE: we do not use query.findMultiple here as querySelectorAll would most likely not deliver the result we want

    var nodes1 = query.findNodesHavingCssClass(node, this.CONTENT_CLASS);
    nodes1 = query.findNodesHavingCssClass(
      node,
      this.LEGACY_CONTENT_CLASS,
      nodes1,
    );
    var nodes2 = query.findNodesHavingAttribute(node, this.CONTENT_ATTR);

    if (nodes2 && nodes2.length) {
      var index;
      for (index = 0; index < nodes2.length; index++) {
        nodes1.push(nodes2[index]);
      }
    }

    if (query.hasNodeAttribute(node, this.CONTENT_ATTR)) {
      nodes1.push(node);
    } else if (query.hasNodeCssClass(node, this.CONTENT_CLASS)) {
      nodes1.push(node);
    } else if (query.hasNodeCssClass(node, this.LEGACY_CONTENT_CLASS)) {
      nodes1.push(node);
    }

    nodes1 = query.makeNodesUnique(nodes1);

    return nodes1;
  },

  /**
   * @param {Node} anyNode
   * @returns {Node | undefined}
   */
  findParentContentNode: function (anyNode) {
    if (!anyNode) {
      return;
    }

    let node = anyNode;
    let counter = 0;

    while (node && node !== document && node.parentNode) {
      if (query.hasNodeAttribute(node, this.CONTENT_ATTR)) {
        return node;
      }
      if (query.hasNodeCssClass(node, this.CONTENT_CLASS)) {
        return node;
      }
      if (query.hasNodeCssClass(node, this.LEGACY_CONTENT_CLASS)) {
        return node;
      }

      node = node.parentNode;

      if (counter > 1000) {
        break; // prevent loop, should not happen anyway but better we do this
      }
      counter++;
    }
  },
  findPieceNode: function (node) {
    var contentPiece;

    contentPiece = query.findFirstNodeHavingAttribute(
      node,
      this.CONTENT_PIECE_ATTR,
    );

    if (!contentPiece) {
      contentPiece = query.findFirstNodeHavingClass(
        node,
        this.CONTENT_PIECE_CLASS,
      );
    }
    if (!contentPiece) {
      contentPiece = query.findFirstNodeHavingClass(
        node,
        this.LEGACY_CONTENT_PIECE_CLASS,
      );
    }

    if (contentPiece) {
      return contentPiece;
    }

    return node;
  },
  findTargetNodeNoDefault: function (node) {
    if (!node) {
      return;
    }

    var target = query.findFirstNodeHavingAttributeWithValue(
      node,
      this.CONTENT_TARGET_ATTR,
    );
    if (target) {
      return target;
    }

    target = query.findFirstNodeHavingAttribute(node, this.CONTENT_TARGET_ATTR);
    if (target) {
      return target;
    }

    target = query.findFirstNodeHavingClass(node, this.CONTENT_TARGET_CLASS);
    if (target) {
      return target;
    }

    target = query.findFirstNodeHavingClass(
      node,
      this.LEGACY_CONTENT_TARGET_CLASS,
    );
    if (target) {
      return target;
    }
  },
  findTargetNode: function (node) {
    var target = this.findTargetNodeNoDefault(node);
    if (target) {
      return target;
    }

    return node;
  },
  findContentName: function (node) {
    if (!node) {
      return;
    }

    var nameNode = query.findFirstNodeHavingAttributeWithValue(
      node,
      this.CONTENT_NAME_ATTR,
    );

    if (nameNode) {
      return query.getAttributeValueFromNode(nameNode, this.CONTENT_NAME_ATTR);
    }

    var contentPiece = this.findContentPiece(node);
    if (contentPiece) {
      return this.removeDomainIfIsInLink(contentPiece);
    }

    if (query.hasNodeAttributeWithValue(node, "title")) {
      return query.getAttributeValueFromNode(node, "title");
    }

    var clickUrlNode = this.findPieceNode(node);

    if (query.hasNodeAttributeWithValue(clickUrlNode, "title")) {
      return query.getAttributeValueFromNode(clickUrlNode, "title");
    }

    var targetNode = this.findTargetNode(node);

    if (query.hasNodeAttributeWithValue(targetNode, "title")) {
      return query.getAttributeValueFromNode(targetNode, "title");
    }
  },
  findContentPiece: function (node) {
    if (!node) {
      return;
    }

    var nameNode = query.findFirstNodeHavingAttributeWithValue(
      node,
      this.CONTENT_PIECE_ATTR,
    );

    if (nameNode) {
      return query.getAttributeValueFromNode(nameNode, this.CONTENT_PIECE_ATTR);
    }

    var contentNode = this.findPieceNode(node);

    var media = this.findMediaUrlInNode(contentNode);
    if (media) {
      return this.toAbsoluteUrl(media);
    }
  },
  findContentTarget: function (node) {
    if (!node) {
      return;
    }

    var targetNode = this.findTargetNode(node);

    if (query.hasNodeAttributeWithValue(targetNode, this.CONTENT_TARGET_ATTR)) {
      return query.getAttributeValueFromNode(
        targetNode,
        this.CONTENT_TARGET_ATTR,
      );
    }

    var href;
    if (query.hasNodeAttributeWithValue(targetNode, "href")) {
      href = query.getAttributeValueFromNode(targetNode, "href");
      return this.toAbsoluteUrl(href);
    }

    var contentNode = this.findPieceNode(node);

    if (query.hasNodeAttributeWithValue(contentNode, "href")) {
      href = query.getAttributeValueFromNode(contentNode, "href");
      return this.toAbsoluteUrl(href);
    }
  },
  isSameDomain: function (url) {
    if (!url || !url.indexOf) {
      return false;
    }

    if (0 === url.indexOf(this.getLocation().origin)) {
      return true;
    }

    var posHost = url.indexOf(this.getLocation().host);
    if (8 >= posHost && 0 <= posHost) {
      return true;
    }

    return false;
  },
  removeDomainIfIsInLink: function (text) {
    // we will only remove if domain === location.origin meaning is not an outlink
    var regexContainsProtocol = "^https?://[^/]+";
    var regexReplaceDomain = "^.*//[^/]+";

    if (
      text &&
      text.search &&
      -1 !== text.search(new RegExp(regexContainsProtocol)) &&
      this.isSameDomain(text)
    ) {
      text = text.replace(new RegExp(regexReplaceDomain), "");
      if (!text) {
        text = "/";
      }
    }

    return text;
  },
  findMediaUrlInNode: function (node) {
    if (!node) {
      return;
    }

    var mediaElements = ["img", "embed", "video", "audio"];
    var elementName = node.nodeName.toLowerCase();

    if (
      -1 !== h.indexOfArray(mediaElements, elementName) &&
      query.findFirstNodeHavingAttributeWithValue(node, "src")
    ) {
      var sourceNode = query.findFirstNodeHavingAttributeWithValue(node, "src");

      return query.getAttributeValueFromNode(sourceNode, "src");
    }

    if (
      elementName === "object" &&
      query.hasNodeAttributeWithValue(node, "data")
    ) {
      return query.getAttributeValueFromNode(node, "data");
    }

    if (elementName === "object") {
      var params = query.findNodesByTagName(node, "param");
      if (params && params.length) {
        var index;
        for (index = 0; index < params.length; index++) {
          if (
            "movie" ===
              query.getAttributeValueFromNode(params[index], "name") &&
            query.hasNodeAttributeWithValue(params[index], "value")
          ) {
            return query.getAttributeValueFromNode(params[index], "value");
          }
        }
      }

      var embed = query.findNodesByTagName(node, "embed");
      if (embed && embed.length) {
        return this.findMediaUrlInNode(embed[0]);
      }
    }
  },

  /**
   * @param {string} text
   * @returns {string}
   */
  trim: function (text) {
    return h.trim(text);
  },

  /**
   * @param {HTMLElement} node
   * @returns {boolean}
   */
  isOrWasNodeInViewport: function (node) {
    if (!node || !node.getBoundingClientRect || node.nodeType !== 1) {
      return true;
    }

    var rect = node.getBoundingClientRect();
    var html = document.documentElement || {};

    var wasVisible = rect.top < 0;
    if (wasVisible && node.offsetTop) {
      wasVisible = node.offsetTop + rect.height > 0;
    }

    var docWidth = html.clientWidth; // The clientWidth attribute returns the viewport width excluding the size of a rendered scroll bar

    if (
      window.innerWidth &&
      docWidth > window.innerWidth
    ) {
      docWidth = window.innerWidth; // The innerWidth attribute must return the viewport width including the size of a rendered scroll bar
    }

    var docHeight = html.clientHeight; // The clientWidth attribute returns the viewport width excluding the size of a rendered scroll bar

    if (
      window.innerHeight &&
      docHeight > window.innerHeight
    ) {
      docHeight = window.innerHeight; // The innerWidth attribute must return the viewport width including the size of a rendered scroll bar
    }

    return (
      (rect.bottom > 0 || wasVisible) &&
      rect.right > 0 &&
      rect.left < docWidth &&
      (rect.top < docHeight || wasVisible) // rect.top < 0 we assume user has seen all the ones that are above the current viewport
    );
  },

  /**
   * @param {HTMLElement} node
   * @returns {boolean}
   */
  isNodeVisible: function (node) {
    var isItVisible = isVisible(node);
    var isInViewport = this.isOrWasNodeInViewport(node);
    return isItVisible && isInViewport;
  },

  buildInteractionRequestParams: function (interaction, name, piece, target) {
    var params = "";

    if (interaction) {
      params += "c_i=" + encodeURIComponent(interaction);
    }
    if (name) {
      if (params) {
        params += "&";
      }
      params += "c_n=" + encodeURIComponent(name);
    }
    if (piece) {
      if (params) {
        params += "&";
      }
      params += "c_p=" + encodeURIComponent(piece);
    }
    if (target) {
      if (params) {
        params += "&";
      }
      params += "c_t=" + encodeURIComponent(target);
    }

    if (params) {
      params += "&ca=1";
    }

    return params;
  },
  buildImpressionRequestParams: function (name, piece, target) {
    var params =
      "c_n=" +
      encodeURIComponent(name) +
      "&c_p=" +
      encodeURIComponent(piece);

    if (target) {
      params += "&c_t=" + encodeURIComponent(target);
    }

    if (params) {
      params += "&ca=1";
    }

    return params;
  },
  buildContentBlock: function (node) {
    if (!node) {
      return;
    }

    var name = this.findContentName(node);
    var piece = this.findContentPiece(node);
    var target = this.findContentTarget(node);

    name = this.trim(name);
    piece = this.trim(piece);
    target = this.trim(target);

    return {
      name: name || "Unknown",
      piece: piece || "Unknown",
      target: target || "",
    };
  },
  collectContent: function (contentNodes) {
    if (!contentNodes || !contentNodes.length) {
      return [];
    }

    var contents = [];

    var index, contentBlock;
    for (index = 0; index < contentNodes.length; index++) {
      contentBlock = this.buildContentBlock(contentNodes[index]);
      if (h.isDefined(contentBlock)) {
        contents.push(contentBlock);
      }
    }

    return contents;
  },
  setLocation: function (location) {
    this.location = location;
  },
  getLocation: function () {
    var locationAlias = this.location || window.location;

    if (!locationAlias.origin) {
      locationAlias.origin =
        locationAlias.protocol +
        "//" +
        locationAlias.hostname +
        (locationAlias.port ? ":" + locationAlias.port : "");
    }

    return locationAlias;
  },
  toAbsoluteUrl: function (url) {
    if ((!url || String(url) !== url) && url !== "") {
      // we only handle strings
      return url;
    }

    if ("" === url) {
      return this.getLocation().href;
    }

    // Eg //example.com/test.jpg
    if (url.search(/^\/\//) !== -1) {
      return this.getLocation().protocol + url;
    }

    // Eg http://example.com/test.jpg
    if (url.search(/:\/\//) !== -1) {
      return url;
    }

    // Eg #test.jpg
    if (0 === url.indexOf("#")) {
      return this.getLocation().origin + this.getLocation().pathname + url;
    }

    // Eg ?x=5
    if (0 === url.indexOf("?")) {
      return this.getLocation().origin + this.getLocation().pathname + url;
    }

    // Eg mailto:x@y.z tel:012345, ... market:... sms:..., javascript:... ecmascript: ... and many more
    if (0 === url.search("^[a-zA-Z]{2,11}:")) {
      return url;
    }

    // Eg /test.jpg
    if (url.search(/^\//) !== -1) {
      return this.getLocation().origin + url;
    }

    // Eg test.jpg
    var regexMatchDir = "(.*/)";
    var base =
      this.getLocation().origin +
      this.getLocation().pathname.match(new RegExp(regexMatchDir))[0];
    return base + url;
  },
  isUrlToCurrentDomain: function (url) {
    var absoluteUrl = this.toAbsoluteUrl(url);

    if (!absoluteUrl) {
      return false;
    }

    var origin = this.getLocation().origin;
    if (origin === absoluteUrl) {
      return true;
    }

    if (0 === String(absoluteUrl).indexOf(origin)) {
      if (":" === String(absoluteUrl).substr(origin.length, 1)) {
        return false; // url has port whereas origin has not => different URL
      }

      return true;
    }

    return false;
  },
  setHrefAttribute: function (node, url) {
    if (!node || !url) {
      return;
    }

    query.setAnyAttribute(node, "href", url);
  },

  /**
   * @param {Node} targetNode
   * @returns {boolean}
   */
  shouldIgnoreInteraction: function (targetNode) {
    if (
      query.hasNodeAttribute(targetNode, this.CONTENT_IGNOREINTERACTION_ATTR)
    ) {
      return true;
    }
    if (
      query.hasNodeCssClass(targetNode, this.CONTENT_IGNOREINTERACTION_CLASS)
    ) {
      return true;
    }
    if (
      query.hasNodeCssClass(
        targetNode,
        this.LEGACY_CONTENT_IGNOREINTERACTION_CLASS,
      )
    ) {
      return true;
    }
    return false;
  },
};
