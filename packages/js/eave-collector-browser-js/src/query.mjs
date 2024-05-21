// @ts-check
import * as h from "./helpers.mjs";

/**
 * @param {string} selector
 *
 * @returns {Element[]}
 */
export function findElement(selector) {
  // we use querySelectorAll only on document, not on nodes because of its unexpected behavior. See for
  // instance http://stackoverflow.com/questions/11503534/jquery-vs-document-queryselectorall and
  // http://jsfiddle.net/QdMc5/ and http://ejohn.org/blog/thoughts-on-queryselectorall
  if (!document.querySelectorAll || !selector) {
    return []; // we do not support all browsers
  }

  const foundNodes = document.querySelectorAll(selector);
  return Array.from(foundNodes);
}

/**
 * @param {string[]} selectors
 *
 * @returns {Element[]}
 */
export function findMultiple(selectors) {
  if (selectors.length === 0) {
    return [];
  }

  const nodes = [];
  for (const selector of selectors) {
    const foundNodes = findElement(selector);
    nodes.push(...foundNodes);
  }

  makeNodesUnique(nodes);

  return nodes;
}

/**
 * @param {Element} node
 * @param {string} tagName
 *
 * @returns {Element[]}
 */
export function findNodesByTagName(node, tagName) {
  if (!node || !tagName || !node.getElementsByTagName) {
    return [];
  }

  const foundNodes = node.getElementsByTagName(tagName);
  return Array.from(foundNodes);
}

/**
 * @param {Node[]} nodes
 *
 * @returns {Node[]}
 */
export function makeNodesUnique(nodes) {
  const copy = [...nodes];
  nodes.sort(function (n1, n2) {
    if (n1 === n2) {
      return 0;
    }

    const index1 = h.indexOfArray(copy, n1);
    const index2 = h.indexOfArray(copy, n2);

    if (index1 === index2) {
      return 0;
    }

    return index1 > index2 ? -1 : 1;
  });

  if (nodes.length <= 1) {
    return nodes;
  }

  let index = 0;
  let numDuplicates = 0;
  const duplicates = [];
  let node;

  node = nodes[index++];

  while (node) {
    if (node === nodes[index]) {
      numDuplicates = duplicates.push(index);
    }

    node = nodes[index++] || null;
  }

  while (numDuplicates--) {
    nodes.splice(duplicates[numDuplicates], 1);
  }

  return nodes;
}

/**
 * @param {Node} node
 * @param {string} attributeName
 *
 * @returns {string | null}
 */
export function getAttributeValueFromNode(node, attributeName) {
  if (!hasNodeAttribute(node, attributeName)) {
    return null;
  }

  const element = h.castNodeToElement(node);
  if (!element) {
    return null;
  }

  return element.getAttribute(attributeName);
}

/**
 * @param {Node} node
 * @param {string} attributeName
 *
 * @returns {boolean}
 */
export function hasNodeAttributeWithValue(node, attributeName) {
  const value = getAttributeValueFromNode(node, attributeName);
  return !!value;
}

/**
 * @param {Node} node
 * @param {string} attributeName
 *
 * @returns {boolean}
 */
export function hasNodeAttribute(node, attributeName) {
  const element = h.castNodeToElement(node);
  if (!element) {
    return false;
  }
  return element.hasAttribute(attributeName);
}

/**
 * @param {Node} node
 * @param {string} klassName
 *
 * @returns {boolean}
 */
export function hasNodeCssClass(node, klassName) {
  const element = h.castNodeToElement(node);
  if (!element) {
    return false;
  }

  const classes = typeof element.className === "string" ? element.className.split(" ") : [];
  return h.indexOfArray(classes, klassName) !== -1;
}

/**
 * @param {Node} nodeToSearch
 * @param {string} attributeName
 * @param {Node[]} [nodes]
 *
 * @returns {Node[]}
 */
export function findNodesHavingAttribute(nodeToSearch, attributeName, nodes) {
  if (!nodes) {
    nodes = [];
  }

  if (!attributeName) {
    return nodes;
  }

  for (const child of nodeToSearch.childNodes) {
    if (hasNodeAttribute(child, attributeName)) {
      nodes.push(child);
    }

    nodes = findNodesHavingAttribute(child, attributeName, nodes);
  }

  return nodes;
}

/**
 * @param {Node} node
 * @param {string} attributeName
 *
 * @returns {Node | null}
 */
export function findFirstNodeHavingAttribute(node, attributeName) {
  if (!node || !attributeName) {
    return null;
  }

  if (hasNodeAttribute(node, attributeName)) {
    return node;
  }

  const nodes = findNodesHavingAttribute(node, attributeName);

  if (nodes.length > 0) {
    return nodes[0];
  }

  return null;
}

/**
 * @param {Node} node
 * @param {string} attributeName
 *
 * @returns {Node | null}
 */
export function findFirstNodeHavingAttributeWithValue(node, attributeName) {
  if (!node || !attributeName) {
    return null;
  }

  if (hasNodeAttributeWithValue(node, attributeName)) {
    return node;
  }

  const nodes = findNodesHavingAttribute(node, attributeName);

  if (nodes.length === 0) {
    return null;
  }

  for (const node of nodes) {
    if (getAttributeValueFromNode(node, attributeName)) {
      return node;
    }
  }

  return null;
}

/**
 * @param {Node} nodeToSearch
 * @param {string} className
 * @param {Node[]} [nodes]
 *
 * @returns {Node[]}
 */
export function findNodesHavingCssClass(nodeToSearch, className, nodes) {
  if (!nodes) {
    nodes = [];
  }

  if (!nodeToSearch || !className) {
    return nodes;
  }

  const element = h.castNodeToElement(nodeToSearch);
  if (element) {
    const foundNodes = element.getElementsByClassName(className);
    return Array.from(foundNodes);
  }

  for (const child of nodeToSearch.childNodes) {
    if (hasNodeCssClass(child, className)) {
      nodes.push(child);
    }

    nodes = findNodesHavingCssClass(child, className, nodes);
  }

  return nodes;
}

/**
 * @param {Node} node
 * @param {string} className
 *
 * @returns {Node | null}
 */
export function findFirstNodeHavingClass(node, className) {
  if (!node || !className) {
    return null;
  }

  if (hasNodeCssClass(node, className)) {
    return node;
  }

  const nodes = findNodesHavingCssClass(node, className);

  if (nodes && nodes.length) {
    return nodes[0];
  }

  return null;
}

/**
 * @param {Node} node
 *
 * @returns {boolean}
 */
export function isLinkElement(node) {
  if (!node) {
    return false;
  }

  const elementName = String(node.nodeName).toLowerCase();
  const linkElementNames = ["a", "area"];
  const pos = h.indexOfArray(linkElementNames, elementName);

  return pos !== -1;
}

/**
 * @param {Node} node
 * @param {string} attrName
 * @param {string} attrValue
 *
 * @noreturn
 */
export function setAnyAttribute(node, attrName, attrValue) {
  if (!node || !attrName) {
    return;
  }

  const element = h.castNodeToElement(node);
  if (element) {
    element.setAttribute(attrName, attrValue);
  }
}
