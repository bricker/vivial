// @ts-check
import * as h from "./helpers.mjs";

export default {
  /**
   * @param {NodeListOf<Element> | HTMLCollectionOf<Element>} foundNodes
   * @returns {Element[]}
   */
  htmlCollectionToArray: function (foundNodes) {
    const nodes = [];

    if (!foundNodes || !foundNodes.length) {
      return nodes;
    }

    let index;
    for (index = 0; index < foundNodes.length; index++) {
      nodes.push(foundNodes[index]);
    }

    return nodes;
  },

  /**
   * @param {string} selector
   * @returns {Element[]}
   */
  find: function (selector) {
    // we use querySelectorAll only on document, not on nodes because of its unexpected behavior. See for
    // instance http://stackoverflow.com/questions/11503534/jquery-vs-document-queryselectorall and
    // http://jsfiddle.net/QdMc5/ and http://ejohn.org/blog/thoughts-on-queryselectorall
    if (!document.querySelectorAll || !selector) {
      return []; // we do not support all browsers
    }

    const foundNodes = document.querySelectorAll(selector);
    return this.htmlCollectionToArray(foundNodes);
  },

  /**
   * @param {string[]} selectors
   * @returns {Element[]}
   */
  findMultiple: function (selectors) {
    if (!selectors || !selectors.length) {
      return [];
    }

    let index, foundNodes;
    let nodes = [];
    for (index = 0; index < selectors.length; index++) {
      foundNodes = this.find(selectors[index]);
      nodes = nodes.concat(foundNodes);
    }

    nodes = this.makeNodesUnique(nodes);

    return nodes;
  },

  /**
   * @param {Element} node
   * @param {string} tagName
   * @returns {Element[]}
   */
  findNodesByTagName: function (node, tagName) {
    if (!node || !tagName || !node.getElementsByTagName) {
      return [];
    }

    const foundNodes = node.getElementsByTagName(tagName);
    return this.htmlCollectionToArray(foundNodes);
  },

  /**
   * @param {Element[]} nodes
   * @returns {Element[]}
   */
  makeNodesUnique: function (nodes) {
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
  },

  /**
   * @param {Node} node
   * @param {string} attributeName
   *
   * @returns {string | null}
   */
  getAttributeValueFromNode: function (node, attributeName) {
    if (!this.hasNodeAttribute(node, attributeName)) {
      return null;
    }

    if (node && node.getAttribute) {
      return node.getAttribute(attributeName);
    }

    if (!node || !node.attributes) {
      return null;
    }

    const typeOfAttr = typeof node.attributes[attributeName];
    if ("undefined" === typeOfAttr) {
      return null;
    }

    if (node.attributes[attributeName].value) {
      return node.attributes[attributeName].value; // nodeValue is deprecated ie Chrome
    }

    if (node.attributes[attributeName].nodeValue) {
      return node.attributes[attributeName].nodeValue;
    }

    let index;
    const attrs = node.attributes;

    if (!attrs) {
      return null;
    }

    for (index = 0; index < attrs.length; index++) {
      if (attrs[index].nodeName === attributeName) {
        return attrs[index].nodeValue;
      }
    }

    return null;
  },

  /**
   * @param {Node} node
   * @param {string} attributeName
   *
   * @returns {boolean}
   */
  hasNodeAttributeWithValue: function (node, attributeName) {
    const value = this.getAttributeValueFromNode(node, attributeName);
    return !!value;
  },

  /**
   * @param {Node} node
   * @param {string} attributeName
   *
   * @returns {boolean}
   */
  hasNodeAttribute: function (node, attributeName) {
    const element = h.castNodeToElement(node);
    if (!element) {
      return false;
    }
    return element.hasAttribute(attributeName);
  },

  /**
   * @param {Node} node
   * @param {string} klassName
   *
   * @returns {boolean}
   */
  hasNodeCssClass: function (node, klassName) {
    const element = h.castNodeToElement(node);
    if (!element) {
      return false;
    }

    const classes = typeof element.className === "string" ? element.className.split(" ") : [];
    return h.indexOfArray(classes, klassName) !== -1;
  },

  /**
   * @param {Node} nodeToSearch
   * @param {string} attributeName
   * @param {Node[]} [nodes]
   *
   * @returns {Node[]}
   */
  findNodesHavingAttribute: function (nodeToSearch, attributeName, nodes) {
    if (!nodes) {
      nodes = [];
    }

    if (!attributeName) {
      return nodes;
    }

    for (const child of nodeToSearch.childNodes) {
      if (this.hasNodeAttribute(child, attributeName)) {
        nodes.push(child);
      }

      nodes = this.findNodesHavingAttribute(child, attributeName, nodes);
    }

    return nodes;
  },

  /**
   * @param {Node} node
   * @param {string} attributeName
   *
   * @returns {Node | null}
   */
  findFirstNodeHavingAttribute: function (node, attributeName) {
    if (!node || !attributeName) {
      return null;
    }

    if (this.hasNodeAttribute(node, attributeName)) {
      return node;
    }

    const nodes = this.findNodesHavingAttribute(node, attributeName);

    if (nodes.length > 0) {
      return nodes[0];
    }

    return null;
  },

  /**
   * @param {Node} node
   * @param {string} attributeName
   *
   * @returns {Node | null}
   */
  findFirstNodeHavingAttributeWithValue: function (node, attributeName) {
    if (!node || !attributeName) {
      return null;
    }

    if (this.hasNodeAttributeWithValue(node, attributeName)) {
      return node;
    }

    const nodes = this.findNodesHavingAttribute(node, attributeName);

    if (nodes.length === 0) {
      return null;
    }

    for (const node of nodes) {
      if (this.getAttributeValueFromNode(node, attributeName)) {
        return node;
      }
    }
  },

  /**
   * @param {Node} nodeToSearch
   * @param {string} className
   * @param {Element[]} [nodes]
   *
   * @returns {Element[]}
   */
  findNodesHavingCssClass: function (nodeToSearch, className, nodes) {
    if (!nodes) {
      nodes = [];
    }

    if (!nodeToSearch || !className) {
      return nodes;
    }

    if (nodeToSearch.nodeType === Node.ELEMENT_NODE) {
      const element = h.castNodeToElement(nodeToSearch);
      const foundNodes = element.getElementsByClassName(className);
      return this.htmlCollectionToArray(foundNodes);
    }

    for (const child of nodeToSearch.childNodes) {
      if (this.hasNodeCssClass(child, className)) {
        nodes.push(child);
      }

      nodes = this.findNodesHavingCssClass(child, className, nodes);
    }

    return nodes;
  },

  /**
   * @param {Element} node
   * @param {string} className
   * @returns {Element | undefined}
   */
  findFirstNodeHavingClass: function (node, className) {
    if (!node || !className) {
      return;
    }

    if (this.hasNodeCssClass(node, className)) {
      return node;
    }

    const nodes = this.findNodesHavingCssClass(node, className);

    if (nodes && nodes.length) {
      return nodes[0];
    }
  },

  /**
   * @param {Element} node
   * @returns {boolean}
   */
  isLinkElement: function (node) {
    if (!node) {
      return false;
    }

    const elementName = String(node.nodeName).toLowerCase();
    const linkElementNames = ["a", "area"];
    const pos = h.indexOfArray(linkElementNames, elementName);

    return pos !== -1;
  },

  /**
   * @param {Element} node
   * @param {string} attrName
   * @param {string} attrValue
   */
  setAnyAttribute: function (node, attrName, attrValue) {
    if (!node || !attrName) {
      return;
    }

    if (node.setAttribute) {
      node.setAttribute(attrName, attrValue);
    } else {
      node[attrName] = attrValue;
    }
  },
};
