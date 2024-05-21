// @ts-check

import "./main.mjs";
import { castNodeToElement, castNodeToHtmlElement } from "./helpers.mjs";

/**
 * Author: Jason Farrell
 * Author URI: http://useallfive.com/
 *
 * Description: Checks if a DOM element is truly visible.
 * Package URL: https://github.com/UseAllFive/true-visibility
 * License: MIT (https://github.com/UseAllFive/true-visibility/blob/master/LICENSE.txt)
 */

/**
 * @param {Node} node
 *
 * @returns {boolean}
 */
export function isVisible(node) {
  if (!node) {
    return false;
  }

  /**
   * Cross browser method to get style properties
   * @param {HTMLElement} el
   * @param {string} property
   *
   * @returns {string | undefined}
   */
  function _getStyle(el, property) {
    return document.defaultView?.getComputedStyle(
      el,
      null,
    )[property];
  }

  /**
   * @param {HTMLElement} element
   *
   * @returns {boolean}
   */
  function _elementInDocument(element) {
    let _element = element.parentNode;

    while (_element) {
      if (_element === document) {
        return true;
      }
      _element = _element.parentNode;
    }
    return false;
  }

  /**
   * Checks if a DOM element is visible. Takes into
   * consideration its parents and overflow.
   *
   * @param {Node} _node      the DOM element to check if is visible
   *
   * These params are optional that are sent in recursively,
   * you typically won't use these:
   *
   * @param {number} [t]       Top corner position number
   * @param {number} [r]       Right corner position number
   * @param {number} [b]       Bottom corner position number
   * @param {number} [l]       Left corner position number
   * @param {number} [w]       Element width number
   * @param {number} [h]       Element height number
   *
   * @returns {boolean}
   */
  function _isVisible(_node, t, r, b, l, w, h) {
    const element = castNodeToHtmlElement(_node);
    if (!element) {
      return false;
    }

    const p = element.parentNode;
    const VISIBLE_PADDING = 1; // has to be visible at least one px of the element

    if (!_elementInDocument(element)) {
      return false;
    }

    //-- Return true for document node
    if (9 === p?.nodeType) {
      return true;
    }

    //-- Return false if our element is invisible
    if (
      "0" === _getStyle(element, "opacity") ||
      "none" === _getStyle(element, "display") ||
      "hidden" === _getStyle(element, "visibility")
    ) {
      return false;
    }

    if (
      t === undefined||
      r === undefined ||
      b === undefined ||
      l === undefined ||
      w === undefined ||
      h === undefined
    ) {
      t = element.offsetTop;
      l = element.offsetLeft;
      b = t + element.offsetHeight;
      r = l + element.offsetWidth;
      w = element.offsetWidth;
      h = element.offsetHeight;
    }

    if (
      node === element &&
      (0 === h || 0 === w) &&
      "hidden" === _getStyle(element, "overflow")
    ) {
      return false;
    }

    //-- If we have a parent, let's continue:
    if (p) {
      const parent = castNodeToHtmlElement(p);
      if (!parent) {
        return false;
      }
      //-- Check if the parent can hide its children.
      if (
        "hidden" === _getStyle(parent, "overflow") ||
        "scroll" === _getStyle(parent, "overflow")
      ) {
        //-- Only check if the offset is different for the parent
        if (
          //-- If the target element is to the right of the parent elm
          l + VISIBLE_PADDING > parent.offsetWidth + parent.scrollLeft ||
          //-- If the target element is to the left of the parent elm
          l + w - VISIBLE_PADDING < parent.scrollLeft ||
          //-- If the target element is under the parent elm
          t + VISIBLE_PADDING > parent.offsetHeight + parent.scrollTop ||
          //-- If the target element is above the parent elm
          t + h - VISIBLE_PADDING < parent.scrollTop
        ) {
          //-- Our target element is out of bounds:
          return false;
        }
      }
      //-- Add the offset parent's left/top coords to our element's offset:
      if (element.offsetParent === p) {
        l += parent.offsetLeft;
        t += parent.offsetTop;
      }
      //-- Let's recursively check upwards:
      return _isVisible(parent, t, r, b, l, w, h);
    }
    return true;
  }

  return _isVisible(node);
}
