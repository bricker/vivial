  // /**
  //  * Enable tracking of uncaught JavaScript errors
  //  *
  //  * If enabled, uncaught JavaScript Errors will be tracked as an event by defining a
  //  * window.onerror handler. If a window.onerror handler is already defined we will make
  //  * sure to call this previously registered error handler after tracking the error.
  //  *
  //  * By default we return false in the window.onerror handler to make sure the error still
  //  * appears in the browser's console etc. Note: Some older browsers might behave differently
  //  * so it could happen that an actual JavaScript error will be suppressed.
  //  * If a window.onerror handler was registered we will return the result of this handler.
  //  *
  //  * Make sure not to overwrite the window.onerror handler after enabling the JS error
  //  * tracking as the error tracking won't work otherwise. To capture all JS errors we
  //  * recommend to include the eave JavaScript tracker in the HTML as early as possible.
  //  * If possible directly in <head></head> before loading any other JavaScript.
  //  *
  //  * @noreturn
  //  */
  // this.enableJSErrorTracking = function () {
  //   if (enableJSErrorTracking) {
  //     return;
  //   }

  //   enableJSErrorTracking = true;
  //   const onError = window.onerror;

  //   window.onerror = function (
  //     message,
  //     url,
  //     linenumber,
  //     column,
  //     error,
  //   ) {
  //     trackCallback(function () {
  //       const category = "JavaScript Errors";

  //       let action = url + ":" + linenumber;
  //       if (column) {
  //         action += ":" + column;
  //       }

  //       if (
  //         h.indexOfArray(javaScriptErrors, category + action + message) === -1
  //       ) {
  //         javaScriptErrors.push(category + action + message);

  //         let msg;
  //         if (typeof message === "string") {
  //           msg = message;
  //         } else {
  //           msg = message.type; // ?
  //         }

  //         logEvent(category, action, msg);

  //       }
  //     });

  //     if (onError) {
  //       return onError(message, url, linenumber, column, error);
  //     }

  //     return false;
  //   };
  // };
