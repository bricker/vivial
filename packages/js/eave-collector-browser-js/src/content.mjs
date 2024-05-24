// // @ts-check

// import './main.mjs';
// import * as h from "./helpers.mjs";
// import * as query from "./query.mjs";
// import { isVisible } from "./visibility.mjs";

// export const CONTENT_ATTR = "data-track-content";
// export const CONTENT_CLASS = "eaveTrackContent";
// export const CONTENT_NAME_ATTR = "data-content-name";
// export const CONTENT_PIECE_ATTR = "data-content-piece";
// export const CONTENT_PIECE_CLASS = "eaveContentPiece";
// export const CONTENT_TARGET_ATTR = "data-content-target";
// export const CONTENT_TARGET_CLASS = "eaveContentTarget";
// export const CONTENT_IGNOREINTERACTION_ATTR = "data-content-ignoreinteraction";
// export const CONTENT_IGNOREINTERACTION_CLASS = "eaveContentIgnoreInteraction";

// /**
//  * @returns {Node[]}
//  */
// export function findContentNodes() {
//   const cssSelector = "." + CONTENT_CLASS;
//   const cssSelector2 = "." + LEGACY_CONTENT_CLASS;
//   const attrSelector = "[" + CONTENT_ATTR + "]";
//   const contentNodes = query.findMultiple([
//     cssSelector,
//     cssSelector2,
//     attrSelector,
//   ]);

//   return contentNodes;
// }

// /**
//  * @param {Node} node
//  *
//  * @returns {Node[]}
//  */
// export function findContentNodesWithinNode(node) {
//   if (!node) {
//     return [];
//   }

//   // NOTE: we do not use query.findMultiple here as querySelectorAll would most likely not deliver the result we want

//   let nodes1 = query.findNodesHavingCssClass(node, CONTENT_CLASS);
//   nodes1 = query.findNodesHavingCssClass(
//     node,
//     LEGACY_CONTENT_CLASS,
//     nodes1,
//   );
//   const nodes2 = query.findNodesHavingAttribute(node, CONTENT_ATTR);

//   if (nodes2 && nodes2.length) {
//     nodes1.push(...nodes2);
//   }

//   if (query.hasNodeAttribute(node, CONTENT_ATTR)) {
//     nodes1.push(node);
//   } else if (query.hasNodeCssClass(node, CONTENT_CLASS)) {
//     nodes1.push(node);
//   } else if (query.hasNodeCssClass(node, LEGACY_CONTENT_CLASS)) {
//     nodes1.push(node);
//   }

//   nodes1 = query.makeNodesUnique(nodes1);

//   return nodes1;
// }

// /**
//  * @param {Node} anyNode
//  *
//  * @returns {Node | undefined}
//  */
// export function findParentContentNode(anyNode) {
//   if (!anyNode) {
//     return;
//   }

//   let node = anyNode;
//   let counter = 0;

//   while (node && node !== document && node.parentNode) {
//     if (query.hasNodeAttribute(node, CONTENT_ATTR)) {
//       return node;
//     }
//     if (query.hasNodeCssClass(node, CONTENT_CLASS)) {
//       return node;
//     }
//     if (query.hasNodeCssClass(node, LEGACY_CONTENT_CLASS)) {
//       return node;
//     }

//     node = node.parentNode;

//     if (counter > 1000) {
//       break; // prevent loop, should not happen anyway but better we do this
//     }
//     counter++;
//   }
// }

// export function findPieceNode(node) {
//   let contentPiece = query.findFirstNodeHavingAttribute(
//     node,
//     CONTENT_PIECE_ATTR,
//   );

//   if (!contentPiece) {
//     contentPiece = query.findFirstNodeHavingClass(
//       node,
//       CONTENT_PIECE_CLASS,
//     );
//   }
//   if (!contentPiece) {
//     contentPiece = query.findFirstNodeHavingClass(
//       node,
//       LEGACY_CONTENT_PIECE_CLASS,
//     );
//   }

//   if (contentPiece) {
//     return contentPiece;
//   }

//   return node;
// }

// export function findTargetNodeNoDefault(node) {
//   if (!node) {
//     return;
//   }

//   let target = query.findFirstNodeHavingAttributeWithValue(
//     node,
//     CONTENT_TARGET_ATTR,
//   );
//   if (target) {
//     return target;
//   }

//   target = query.findFirstNodeHavingAttribute(node, CONTENT_TARGET_ATTR);
//   if (target) {
//     return target;
//   }

//   target = query.findFirstNodeHavingClass(node, CONTENT_TARGET_CLASS);
//   if (target) {
//     return target;
//   }

//   target = query.findFirstNodeHavingClass(
//     node,
//     LEGACY_CONTENT_TARGET_CLASS,
//   );
//   if (target) {
//     return target;
//   }
// }

// export function findTargetNode(node) {
//   return findTargetNodeNoDefault(node) || node;
// }

// export function findContentName(node) {
//   if (!node) {
//     return;
//   }

//   const nameNode = query.findFirstNodeHavingAttributeWithValue(
//     node,
//     CONTENT_NAME_ATTR,
//   );

//   if (nameNode) {
//     return query.getAttributeValueFromNode(nameNode, CONTENT_NAME_ATTR);
//   }

//   const contentPiece = findContentPiece(node);
//   if (contentPiece) {
//     return removeDomainIfIsInLink(contentPiece);
//   }

//   if (query.hasNodeAttributeWithValue(node, "title")) {
//     return query.getAttributeValueFromNode(node, "title");
//   }

//   const clickUrlNode = findPieceNode(node);

//   if (query.hasNodeAttributeWithValue(clickUrlNode, "title")) {
//     return query.getAttributeValueFromNode(clickUrlNode, "title");
//   }

//   const targetNode = findTargetNode(node);

//   if (query.hasNodeAttributeWithValue(targetNode, "title")) {
//     return query.getAttributeValueFromNode(targetNode, "title");
//   }
// }

// export function findContentPiece(node) {
//   if (!node) {
//     return;
//   }

//   const nameNode = query.findFirstNodeHavingAttributeWithValue(
//     node,
//     CONTENT_PIECE_ATTR,
//   );

//   if (nameNode) {
//     return query.getAttributeValueFromNode(nameNode, CONTENT_PIECE_ATTR);
//   }

//   const contentNode = findPieceNode(node);

//   const media = findMediaUrlInNode(contentNode);
//   if (media) {
//     return toAbsoluteUrl(media);
//   }
// }

// export function findContentTarget(node) {
//   if (!node) {
//     return;
//   }

//   const targetNode = findTargetNode(node);

//   if (query.hasNodeAttributeWithValue(targetNode, CONTENT_TARGET_ATTR)) {
//     return query.getAttributeValueFromNode(
//       targetNode,
//       CONTENT_TARGET_ATTR,
//     );
//   }

//   let href;
//   if (query.hasNodeAttributeWithValue(targetNode, "href")) {
//     href = query.getAttributeValueFromNode(targetNode, "href");
//     return toAbsoluteUrl(href);
//   }

//   const contentNode = findPieceNode(node);

//   if (query.hasNodeAttributeWithValue(contentNode, "href")) {
//     href = query.getAttributeValueFromNode(contentNode, "href");
//     return toAbsoluteUrl(href);
//   }
// }

// export function isSameDomain(url) {
//   if (!url || !url.indexOf) {
//     return false;
//   }

//   if (0 === url.indexOf(window.location.origin)) {
//     return true;
//   }

//   var posHost = url.indexOf(window.location.host);
//   if (8 >= posHost && 0 <= posHost) {
//     return true;
//   }

//   return false;
// }


// export function removeDomainIfIsInLink(text) {
//   // we will only remove if domain === location.origin meaning is not an outlink
//   const regexContainsProtocol = "^https?://[^/]+";
//   const regexReplaceDomain = "^.*//[^/]+";

//   if (
//     text &&
//     text.search &&
//     -1 !== text.search(new RegExp(regexContainsProtocol)) &&
//     isSameDomain(text)
//   ) {
//     text = text.replace(new RegExp(regexReplaceDomain), "");
//     if (!text) {
//       text = "/";
//     }
//   }

//   return text;
// }


// export function findMediaUrlInNode(node) {
//   if (!node) {
//     return;
//   }

//   const mediaElements = ["img", "embed", "video", "audio"];
//   const elementName = node.nodeName.toLowerCase();

//   if (
//     -1 !== h.indexOfArray(mediaElements, elementName) &&
//     query.findFirstNodeHavingAttributeWithValue(node, "src")
//   ) {
//     const sourceNode = query.findFirstNodeHavingAttributeWithValue(node, "src");
//     if (sourceNode) {
//       return query.getAttributeValueFromNode(sourceNode, "src");
//     } else {
//       return null;
//     }
//   }

//   if (
//     elementName === "object" &&
//     query.hasNodeAttributeWithValue(node, "data")
//   ) {
//     return query.getAttributeValueFromNode(node, "data");
//   }

//   if (elementName === "object") {
//     const params = query.findNodesByTagName(node, "param");
//     if (params && params.length) {
//       for (const param of params) {
//         if (
//           "movie" ===
//             query.getAttributeValueFromNode(param, "name") &&
//           query.hasNodeAttributeWithValue(param, "value")
//         ) {
//           return query.getAttributeValueFromNode(param, "value");
//         }
//       }
//     }

//     const embed = query.findNodesByTagName(node, "embed");
//     if (embed && embed.length) {
//       return findMediaUrlInNode(embed[0]);
//     }
//   }
// }

// /**
//  * @param {Node} node
//  *
//  * @returns {boolean}
//  */
// export function isOrWasNodeInViewport(node) {
//   const element = h.castNodeToHtmlElement(node);
//   if (!element) {
//     return true;
//   }

//   const rect = element.getBoundingClientRect();
//   const html = document.documentElement || {};

//   let wasVisible = rect.top < 0;
//   if (wasVisible && element.offsetTop) {
//     wasVisible = element.offsetTop + rect.height > 0;
//   }

//   let docWidth = html.clientWidth; // The clientWidth attribute returns the viewport width excluding the size of a rendered scroll bar

//   if (
//     window.innerWidth &&
//     docWidth > window.innerWidth
//   ) {
//     docWidth = window.innerWidth; // The innerWidth attribute must return the viewport width including the size of a rendered scroll bar
//   }

//   let docHeight = html.clientHeight; // The clientWidth attribute returns the viewport width excluding the size of a rendered scroll bar

//   if (
//     window.innerHeight &&
//     docHeight > window.innerHeight
//   ) {
//     docHeight = window.innerHeight; // The innerWidth attribute must return the viewport width including the size of a rendered scroll bar
//   }

//   return (
//     (rect.bottom > 0 || wasVisible) &&
//     rect.right > 0 &&
//     rect.left < docWidth &&
//     (rect.top < docHeight || wasVisible) // rect.top < 0 we assume user has seen all the ones that are above the current viewport
//   );
// }

// /**
//  * @param {Node} node
//  *
//  * @returns {boolean}
//  */
// export function isNodeVisible(node) {
//   const isItVisible = isVisible(node);
//   const isInViewport = isOrWasNodeInViewport(node);
//   return isItVisible && isInViewport;
// }

// export function buildInteractionRequestParams(interaction, name, piece, target) {
//   var params = "";

//   if (interaction) {
//     params += "c_i=" + encodeURIComponent(interaction);
//   }
//   if (name) {
//     if (params) {
//       params += "&";
//     }
//     params += "c_n=" + encodeURIComponent(name);
//   }
//   if (piece) {
//     if (params) {
//       params += "&";
//     }
//     params += "c_p=" + encodeURIComponent(piece);
//   }
//   if (target) {
//     if (params) {
//       params += "&";
//     }
//     params += "c_t=" + encodeURIComponent(target);
//   }

//   if (params) {
//     params += "&ca=1";
//   }

//   return params;
// }

// export function buildImpressionRequestParams(name, piece, target) {
//   var params =
//     "c_n=" +
//     encodeURIComponent(name) +
//     "&c_p=" +
//     encodeURIComponent(piece);

//   if (target) {
//     params += "&c_t=" + encodeURIComponent(target);
//   }

//   if (params) {
//     params += "&ca=1";
//   }

//   return params;
// }

// export function buildContentBlock(node) {
//   if (!node) {
//     return;
//   }

//   const name = h.trim(findContentName(node));
//   const piece = h.trim(findContentPiece(node));
//   const target = h.trim(findContentTarget(node));

//   return {
//     name: name || "Unknown",
//     piece: piece || "Unknown",
//     target: target || "",
//   };
// }

// export function collectContent(contentNodes) {
//   if (!contentNodes || !contentNodes.length) {
//     return [];
//   }

//   const contents = [];

//   for (const contentNode of contentNodes) {
//     const contentBlock = buildContentBlock(contentNode);
//     if (contentBlock) {
//       contents.push(contentBlock);
//     }
//   }

//   return contents;
// }

// export function toAbsoluteUrl(url) {
//   if ((!url || String(url) !== url) && url !== "") {
//     // we only handle strings
//     return url;
//   }

//   if ("" === url) {
//     return window.location.href;
//   }

//   // Eg //example.com/test.jpg
//   if (url.search(/^\/\//) !== -1) {
//     return window.location.protocol + url;
//   }

//   // Eg http://example.com/test.jpg
//   if (url.search(/:\/\//) !== -1) {
//     return url;
//   }

//   // Eg #test.jpg
//   if (0 === url.indexOf("#")) {
//     return window.location.origin + window.location.pathname + url;
//   }

//   // Eg ?x=5
//   if (0 === url.indexOf("?")) {
//     return window.location.origin + window.location.pathname + url;
//   }

//   // Eg mailto:x@y.z tel:012345, ... market:... sms:..., javascript:... ecmascript: ... and many more
//   if (0 === url.search("^[a-zA-Z]{2,11}:")) {
//     return url;
//   }

//   // Eg /test.jpg
//   if (url.search(/^\//) !== -1) {
//     return window.location.origin + url;
//   }

//   // Eg test.jpg
//   var regexMatchDir = "(.*/)";
//   var base =
//     window.location.origin +
//     window.location.pathname.match(new RegExp(regexMatchDir))[0];
//   return base + url;
// }

// export function isUrlToCurrentDomain(url) {
//   var absoluteUrl = toAbsoluteUrl(url);

//   if (!absoluteUrl) {
//     return false;
//   }

//   var origin = window.location.origin;
//   if (origin === absoluteUrl) {
//     return true;
//   }

//   if (0 === String(absoluteUrl).indexOf(origin)) {
//     if (":" === String(absoluteUrl).substr(origin.length, 1)) {
//       return false; // url has port whereas origin has not => different URL
//     }

//     return true;
//   }

//   return false;
// }

// export function setHrefAttribute(node, url) {
//   if (!node || !url) {
//     return;
//   }

//   query.setAnyAttribute(node, "href", url);
// }

// /**
//  * @param {Node} targetNode
//  *
//  * @returns {boolean}
//  */
// export function shouldIgnoreInteraction(targetNode) {
//   if (
//     query.hasNodeAttribute(targetNode, CONTENT_IGNOREINTERACTION_ATTR)
//   ) {
//     return true;
//   }
//   if (
//     query.hasNodeCssClass(targetNode, CONTENT_IGNOREINTERACTION_CLASS)
//   ) {
//     return true;
//   }
//   if (
//     query.hasNodeCssClass(
//       targetNode,
//       LEGACY_CONTENT_IGNOREINTERACTION_CLASS,
//     )
//   ) {
//     return true;
//   }
//   return false;
// }
