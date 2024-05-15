// @ts-check
import "./globals.mjs";

/**
 * Author: Jason Farrell
 * Author URI: http://useallfive.com/
 *
 * Description: Checks if a DOM element is truly visible.
 * Package URL: https://github.com/UseAllFive/true-visibility
 * License: MIT (https://github.com/UseAllFive/true-visibility/blob/master/LICENSE.txt)
 */

/**
 * @param {HTMLElement} node
 * @returns {boolean}
 */
export function isVisible(node) {
  if (!node) {
    return false;
  }

  /**
   * Cross browser method to get style properties
   * @param {Element} el
   * @param {string} property
   * @returns {string | undefined}
   */
  function _getStyle(el, property) {
    return document.defaultView?.getComputedStyle(
      el,
      null,
    )[property];
  }

  /**
   * @param {Element} element
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
   * @param {HTMLElement} el      the DOM element to check if is visible
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
  function _isVisible(el, t, r, b, l, w, h) {

    /** @type {HTMLElement | null} */
    // @ts-ignore
    const p = el.parentNode;
    const VISIBLE_PADDING = 1; // has to be visible at least one px of the element

    if (!_elementInDocument(el)) {
      return false;
    }

    //-- Return true for document node
    if (9 === p?.nodeType) {
      return true;
    }

    //-- Return false if our element is invisible
    if (
      "0" === _getStyle(el, "opacity") ||
      "none" === _getStyle(el, "display") ||
      "hidden" === _getStyle(el, "visibility")
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
      t = el.offsetTop;
      l = el.offsetLeft;
      b = t + el.offsetHeight;
      r = l + el.offsetWidth;
      w = el.offsetWidth;
      h = el.offsetHeight;
    }

    if (
      node === el &&
      (0 === h || 0 === w) &&
      "hidden" === _getStyle(el, "overflow")
    ) {
      return false;
    }

    //-- If we have a parent, let's continue:
    if (p) {
      //-- Check if the parent can hide its children.
      if (
        "hidden" === _getStyle(p, "overflow") ||
        "scroll" === _getStyle(p, "overflow")
      ) {
        //-- Only check if the offset is different for the parent
        if (
          //-- If the target element is to the right of the parent elm
          l + VISIBLE_PADDING > p.offsetWidth + p.scrollLeft ||
          //-- If the target element is to the left of the parent elm
          l + w - VISIBLE_PADDING < p.scrollLeft ||
          //-- If the target element is under the parent elm
          t + VISIBLE_PADDING > p.offsetHeight + p.scrollTop ||
          //-- If the target element is above the parent elm
          t + h - VISIBLE_PADDING < p.scrollTop
        ) {
          //-- Our target element is out of bounds:
          return false;
        }
      }
      //-- Add the offset parent's left/top coords to our element's offset:
      if (el.offsetParent === p) {
        l += p.offsetLeft;
        t += p.offsetTop;
      }
      //-- Let's recursively check upwards:
      return _isVisible(p, t, r, b, l, w, h);
    }
    return true;
  }

  return _isVisible(node);
}
