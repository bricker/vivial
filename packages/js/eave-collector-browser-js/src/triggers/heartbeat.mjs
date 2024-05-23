
// /**
//  * Set heartbeat (in seconds)
//  *
//  * @param {number} heartBeatDelayInSeconds Defaults to 15s. Cannot be lower than 5.
//  * @noreturn
//  */
// this.enableHeartBeatTimer = function (heartBeatDelayInSeconds) {
//   heartBeatDelayInSeconds = Math.max(heartBeatDelayInSeconds || 15, 5);
//   configHeartBeatDelay = heartBeatDelayInSeconds * 1000;

//   // if a tracking request has already been sent, start the heart beat timeout
//   if (lastTrackerRequestTime !== null) {
//     setUpHeartBeat();
//   }
// };

// /**
//  * Disable heartbeat if it was previously activated.
//  *
//  * @noreturn
//  */
// this.disableHeartBeatTimer = function () {
//   if (configHeartBeatDelay || heartBeatSetUp) {
//     window.removeEventListener(
//       "focus",
//       heartBeatOnFocus,
//     );
//     window.removeEventListener(
//       "blur",
//       heartBeatOnBlur,
//     );
//     window.removeEventListener(
//       "visibilitychange",
//       heartBeatOnVisible,
//     );
//   }

//   configHeartBeatDelay = null;
//   heartBeatSetUp = false;
// };



// function heartBeatOnFocus() {
//   hadWindowFocusAtLeastOnce = true;
//   timeWindowLastFocused = new Date().getTime();
// }

// /**
//  * @returns {boolean}
//  */
// function hadWindowMinimalFocusToConsiderViewed() {
//   // we ping on blur or unload only if user was active for more than configHeartBeatDelay seconds on
//   // the page otherwise we can assume user was not really on the page and for example only switching
//   // through tabs
//   const now = new Date().getTime();
//   return (
//     !timeWindowLastFocused ||
//     now - timeWindowLastFocused > configHeartBeatDelay
//   );
// }

// /**
//  * @noreturn
//  */
// function heartBeatOnBlur() {
//   if (hadWindowMinimalFocusToConsiderViewed()) {
//     heartBeatPingIfActivityAlias();
//   }
// }

// /**
//  * @noreturn
//  */
// function heartBeatOnVisible() {
//   if (
//     document.visibilityState === "hidden" &&
//     hadWindowMinimalFocusToConsiderViewed()
//   ) {
//     heartBeatPingIfActivityAlias();
//   } else if (document.visibilityState === "visible") {
//     timeWindowLastFocused = new Date().getTime();
//   }
// }

// /**
//  * Setup event handlers and timeout for initial heart beat.
//  *
//  * @noreturn
//  */
// function setUpHeartBeat() {
//   if (heartBeatSetUp || !configHeartBeatDelay) {
//     return;
//   }

//   heartBeatSetUp = true;

//   window.addEventListener("focus", heartBeatOnFocus);
//   window.addEventListener("blur", heartBeatOnBlur);
//   window.addEventListener("visibilitychange", heartBeatOnVisible);

//   // when using multiple trackers then we need to add this event for each tracker
//   eaveWindow.eave.coreHeartBeatCounter++;
//   eaveWindow.eave.eave?.addPlugin(
//     "HeartBeat" + eaveWindow.eave.coreHeartBeatCounter,
//     {
//       unload: function () {
//         // we can't remove the unload plugin event when disabling heart beat timer but we at least
//         // check if it is still enabled... note: when enabling heart beat, then disabling, then
//         // enabling then this could trigger two requests under circumstances maybe. it's edge case though

//         // we only send the heartbeat if onunload the user spent at least 15seconds since last focus
//         // or the configured heatbeat timer
//         if (heartBeatSetUp && hadWindowMinimalFocusToConsiderViewed()) {
//           heartBeatPingIfActivityAlias();
//         }
//       },
//     },
//   );
// }


// /**
//  * If there was user activity since the last check, and it's been configHeartBeatDelay seconds
//  * since the last tracker, send a ping request (the heartbeat timeout will be reset by sendRequest).
//  *
//  * @returns {boolean} whether the heartbeat was sent
//  */
// heartBeatPingIfActivityAlias = function heartBeatPingIfActivity() {
//   const now = new Date().getTime();

//   if (!lastTrackerRequestTime) {
//     return false; // no tracking request was ever sent so lets not send heartbeat now
//   }

//   if (lastTrackerRequestTime + configHeartBeatDelay <= now) {
//     trackerInstance.ping();

//     return true;
//   }

//   return false;
// };
