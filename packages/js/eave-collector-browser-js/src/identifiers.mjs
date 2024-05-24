

// /**
//  * @returns {string} the browser ID
//  */
// function generateBrowserSpecificId() {
//   const browserFeatures = detectBrowserFeatures();

//   return h
//     .sha1(
//       (navigator.userAgent || "") +
//         (navigator.platform || "") +
//         JSON.stringify(browserFeatures),
//     )
//     .slice(0, 6);
// }

// /**
//  * @returns {string} the device ID
//  */
// function makeCrossDomainDeviceId() {
//   const timestamp = h.getCurrentTimestampInSeconds();
//   const browserId = generateBrowserSpecificId();
//   const deviceId = String(timestamp) + browserId;

//   return deviceId;
// }

// /**
//  * @returns {string}
//  */
// function getCrossDomainVisitorId() {
//   const visitorId = trackerInstance.getVisitorId();
//   const deviceId = makeCrossDomainDeviceId();
//   return visitorId + deviceId;
// }