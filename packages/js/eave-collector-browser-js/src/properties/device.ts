import { DeviceProperties } from "../types";

export async function getUserAgentProperties(): Promise<DeviceProperties> {
  const deviceProperties: DeviceProperties = {
    // always available:
    user_agent: navigator.userAgent,
    screen_width: screen.width,
    screen_height: screen.height,
    screen_avail_width: screen.availWidth,
    screen_avail_height: screen.availHeight,
  };

  // @ts-ignore: navigator.userAgentData does not have wide support.
  // It's not available in ES2015 (our target), but in case it _is_ available we should use it.
  // Additionally, it is only available in secure contexts (https) in any browser.
  const userAgentData = navigator.userAgentData;
  if (!userAgentData) {
    return deviceProperties;
  }

  // Initialize with low-entropy values that are always available (when userAgentData is supported)
  // Because userAgentData isn't available in our ES target, it is type `any` here.
  // See here for the documentation on these fields:
  // https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData
  deviceProperties.brands = userAgentData.brands;
  deviceProperties.platform = userAgentData.platform;
  deviceProperties.mobile = userAgentData.mobile;

  // Attempt to get high-entropy values.
  // Currently this method simply returns the requested values through a Promise.
  // In later versions it might require a user permission.
  // https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/getHighEntropyValues
  try {
    const { formFactor, fullVersionList, model, platformVersion } = await userAgentData.getHighEntropyValues([
      "formFactor",
      "fullVersionList",
      "model",
      "platformVersion",
    ]);

    if (fullVersionList) {
      // Overwrite the `brands` attributes with `fullVersionList`.
      // `fullVersionList` is the same info as `brands`, but with more specific version info.
      deviceProperties.brands = fullVersionList;
    }

    if (formFactor) {
      deviceProperties.form_factor = formFactor;
    }

    if (model) {
      deviceProperties.model = model;
    }

    if (platformVersion) {
      deviceProperties.platform_version = platformVersion;
    }
  } catch (e) {
    // Probably `NotAllowedError`, indicating the user denied some permissions.
    // That's okay, we'll just return the basic data we already have.
    console.warn(e);
  }

  return deviceProperties;
}
