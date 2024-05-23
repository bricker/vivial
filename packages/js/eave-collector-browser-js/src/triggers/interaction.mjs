
// /**
//  * @param {Node} node
//  * @param {string} contentInteraction
//  * @returns {string | undefined}
//  */
// function buildContentInteractionRequestNode(node, contentInteraction) {
//   if (!node) {
//     return;
//   }

//   const contentNode = content.findParentContentNode(node);
//   const contentBlock = content.buildContentBlock(contentNode);

//   if (!contentBlock) {
//     return;
//   }

//   if (!contentInteraction) {
//     contentInteraction = "Unknown";
//   }

//   return buildContentInteractionRequest(
//     contentInteraction,
//     contentBlock.name,
//     contentBlock.piece,
//     contentBlock.target,
//   );
// }

// /**
//  * @param {Element[]} contentNodes
//  */
// function setupInteractionsTracking(contentNodes) {
//   if (!contentNodes || !contentNodes.length) {
//     return;
//   }

//   var index, targetNode;
//   for (index = 0; index < contentNodes.length; index++) {
//     targetNode = content.findTargetNode(contentNodes[index]);

//     if (targetNode && !targetNode.contentInteractionTrackingSetupDone) {
//       targetNode.contentInteractionTrackingSetupDone = true;

//       targetNode.addEventListener(
//         "click",
//         trackContentImpressionClickInteraction(targetNode),
//       );
//     }
//   }
// }

// /**
//  * @param {Node} targetNode
//  * @returns {(event: Event) => string | number | false | null | undefined}
//  */
// function trackContentImpressionClickInteraction(targetNode) {
//   return function (event) {
//     if (!targetNode) {
//       return;
//     }

//     const contentBlock = content.findParentContentNode(targetNode);

//     if (!contentBlock) {
//       return false;
//     }

//     let interactedElement;
//     if (event) {
//       interactedElement = event.target;
//     }
//     if (!interactedElement) {
//       interactedElement = targetNode;
//     }

//     if (
//       !isNodeAuthorizedToTriggerInteraction(contentBlock, interactedElement)
//     ) {
//       return;
//     }

//     const theTargetNode = content.findTargetNode(contentBlock);

//     if (!theTargetNode || content.shouldIgnoreInteraction(theTargetNode)) {
//       return false;
//     }

//     const link = getLinkIfShouldBeProcessed(theTargetNode);

//     if (linkTrackingEnabled && link && link.type) {
//       return link.type; // will be handled via outlink or download.
//     }

//     return trackerInstance.trackContentInteractionNode(
//       interactedElement,
//       "click",
//     );
//   };
// }

// /**
//  * @param {any} interaction
//  * @param {string} name
//  * @param {any} piece
//  * @param {any} target
//  *
//  * @returns {string | undefined}
//  */
// function buildContentInteractionRequest(interaction, name, piece, target) {
//   const params = content.buildInteractionRequestParams(
//     interaction,
//     name,
//     piece,
//     target,
//   );

//   if (!params) {
//     return;
//   }

//   return getRequest(params, null, "contentInteraction");
// }

// /**
//  * @param {Node} contentNode
//  * @param {Node} interactedNode
//  *
//  * @returns {boolean}
//  */
// function isNodeAuthorizedToTriggerInteraction(contentNode, interactedNode) {
//   if (!contentNode || !interactedNode) {
//     return false;
//   }

//   let targetNode = content.findTargetNode(contentNode);

//   if (content.shouldIgnoreInteraction(targetNode)) {
//     // interaction should be ignored
//     return false;
//   }

//   targetNode = content.findTargetNodeNoDefault(contentNode);
//   if (targetNode && !h.containsNodeElement(targetNode, interactedNode)) {
//     /**
//      * There is a target node defined but the clicked element is not within the target node. example:
//      * <div data-track-content><a href="Y" data-content-target>Y</a><img src=""/><a href="Z">Z</a></div>
//      *
//      * The user clicked in this case on link Z and not on target Y
//      */
//     return false;
//   }

//   return true;
// }

// /**
//  * @param {string} interaction
//  * @param {string} fallbackTarget
//  * @param {Node} [anyNode]
//  *
//  * @returns {string | undefined}
//  */
// function getContentInteractionToRequestIfPossible(
//   interaction,
//   fallbackTarget,
//   anyNode,
// ) {
//   if (!anyNode) {
//     return;
//   }

//   const contentNode = content.findParentContentNode(anyNode);

//   if (!contentNode) {
//     // we are not within a content block
//     return;
//   }

//   if (!isNodeAuthorizedToTriggerInteraction(contentNode, anyNode)) {
//     return;
//   }

//   const contentBlock = content.buildContentBlock(contentNode);

//   if (!contentBlock) {
//     return;
//   }

//   if (!contentBlock.target && fallbackTarget) {
//     contentBlock.target = fallbackTarget;
//   }

//   return content.buildInteractionRequestParams(
//     interaction,
//     contentBlock.name,
//     contentBlock.piece,
//     contentBlock.target,
//   );
// }


// /**
//  * Tracks a content interaction using the specified values. You should use this method only in conjunction
//  * with `trackContentImpression()`. The specified `contentName` and `contentPiece` has to be exactly the
//  * same as the ones that were used in `trackContentImpression()`. Otherwise the interaction will not count.
//  *
//  * @param {string} contentInteraction The type of interaction that happened. For instance 'click' or 'submit'.
//  * @param {string} contentName  The name of the content. For instance "Ad Sale".
//  * @param {string} [contentPiece='Unknown'] The actual content. For instance a path to an image or the text of a text ad.
//  * @param {string} [contentTarget] For instance the URL of a landing page.
//  * @noreturn
//  */
// this.trackContentInteraction = function (
//   contentInteraction,
//   contentName,
//   contentPiece,
//   contentTarget,
// ) {
//   contentInteraction = h.trim(contentInteraction);
//   contentName = h.trim(contentName);
//   contentPiece = h.trim(contentPiece);
//   contentTarget = h.trim(contentTarget);

//   if (!contentInteraction || !contentName) {
//     return;
//   }

//   contentPiece = contentPiece || "Unknown";

//   trackCallback(function () {
//     const request = buildContentInteractionRequest(
//       contentInteraction,
//       contentName,
//       contentPiece,
//       contentTarget,
//     );
//     if (request) {
//       requestQueue.push(request);
//     }
//   });
// };

// /**
//  * Tracks an interaction with the given DOM node / content block.
//  *
//  * By default we track interactions on click but sometimes you might want to track interactions yourself.
//  * For instance you might want to track an interaction manually on a double click or a form submit.
//  * Make sure to disable the automatic interaction tracking in this case by specifying either the CSS
//  * class `eaveContentIgnoreInteraction` or the attribute `data-content-ignoreinteraction`.
//  *
//  * @param {EventTarget} domNode  This element itself or any of its parent elements has to be a content block
//  *                         element. Meaning one of those has to have a `eaveTrackContent` CSS class or
//  *                         a `data-track-content` attribute.
//  * @param {string} [contentInteraction='Unknown] The name of the interaction that happened. For instance
//  *                                             'click', 'formSubmit', 'DblClick', ...
//  * @returns {string | null}
//  */
// this.trackContentInteractionNode = function (domNode, contentInteraction) {
//   let theRequest = null;

//   trackCallback(function () {
//     theRequest = buildContentInteractionRequestNode(
//       domNode,
//       contentInteraction,
//     );
//     if (theRequest) {
//       requestQueue.push(theRequest);
//     }
//   });
//   //note: return value is only for tests... will only work if dom is already ready...
//   return theRequest;
// };