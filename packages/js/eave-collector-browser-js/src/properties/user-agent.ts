import { UserAgentProperties } from "../types";

export async function getUserAgentProperties(): Promise<UserAgentProperties> {
  const userAgentProperties: UserAgentProperties = {
    ua_string: navigator.userAgent, // always available
  };

  // @ts-ignore: navigator.userAgentData does not have wide support.
  // It's not available in ES2015 (our target), but in case it _is_ available we should use it.
  // Additionally, it is only available in secure contexts (https) in any browser.
  const userAgentData = navigator.userAgentData;
  if (!userAgentData) {
    return userAgentProperties;
  }

  // Initialize with low-entropy values that are always available (when userAgentData is supported)
  // Because userAgentData isn't available in our ES target, it is type `any` here.
  // See here for the documentation on these fields:
  // https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData
  userAgentProperties.brands = userAgentData.brands;
  userAgentProperties.platform = userAgentData.platform;
  userAgentProperties.mobile = userAgentData.mobile;

  // Attempt to get high-entropy values.
  // Currently this method simply returns the requested values through a Promise.
  // In later versions it might require a user permission.
  // https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/getHighEntropyValues
  const highEntropyValues = await userAgentData.getHighEntropyValues([
    "formFactor",
    "fullVersionList",
    "model",
    "platformVersion",
  ]);

  userAgentProperties.form_factor = highEntropyValues.formFactor;
  userAgentProperties.full_version_list = highEntropyValues.fullVersionList;
  userAgentProperties.model = highEntropyValues.model;
  userAgentProperties.platform_version = highEntropyValues.platformVersion;

  return userAgentProperties;
}
