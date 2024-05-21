/**
 * Track form submission events
 *
 * @noreturn
 */
this.enableFormTracking = function () {
  if (formTrackingEnabled) {
    return;
  }
  formTrackingEnabled = true;

  if (!formTrackerInstalled) {
    formTrackerInstalled = true;
    h.trackCallbackOnReady(function () {
      document.body.addEventListener(
        "submit",
        function (event) {
          if (!event.target) {
            return;
          }
          const target = event.target;
          if (target.nodeName === "FORM") {
            const formAction =
              target.getAttribute("action") ||
              window.location.href;

            logEvent(
              // TODO: details
              "form",
              "submit",
              "form submitted",
              formAction,
              {
                // custom data
                event: "FormSubmit",
                formElement: target.outerHtml,
                formElementId: target.getAttribute("id"),
                formElementName: target.getAttribute("name"),
                formElementClasses: target.className.split(" "),
                formElementAction: formAction,
              },
              undefined, // callback
            );
          }
        },
        true,
      );
    });
  }
};