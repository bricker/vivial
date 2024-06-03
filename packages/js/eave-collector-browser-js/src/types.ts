export type StringMap<T extends string | string[]> = { [key: string]: T };
export type NullableStringMap<T extends string | string[]> = { [key: string]: T | null };

export type JSONScalar = string | number | boolean | null | undefined;
export type JSONObject = {
  [key: string]: JSONScalar | JSONScalar[] | JSONObject | JSONObject[];
};
export type JSONValue = JSONScalar | JSONScalar[] | JSONObject | JSONObject[];

export type KeyValueArray = {
  key: string;
  value: string | null;
}[];

// These are just for clarity, because Javascript represents UTS in millis,
// but the server needs them in seconds resolution.
export type EpochTimeStampMillis = number;
export type EpochTimeStampSeconds = number;

export type EaveConfiguration = {
  EAVE_CLIENT_ID?: string;
};

export type EaveInterface = {
  enableAll: () => void;
  disableAll: () => void;
  enableCookies: () => void;
  disableCookies: () => void;
  enableTracking: () => void;
  disableTracking: () => void;
};

export type GlobalEaveState = {
  pageViewId: string;
};

export type GlobalEaveWindow = Window & EaveConfiguration & { eave: EaveInterface };

export type DeviceBrandProperties = {
  brand: string;
  version: string;
}

export type DeviceProperties = {
  user_agent: string;
  brands?: DeviceBrandProperties[];
  platform?: string;
  mobile?: boolean;
  form_factor?: string;
  model?: string;
  platform_version?: string;
  screen_width: number;
  screen_height: number;
  screen_avail_width: number;
  screen_avail_height: number;
};

export type PageProperties = {
  current_url: string;
  current_title: string;
  pageview_id: string;
  current_query_params: KeyValueArray;
};

export type SessionProperties = {
  id: string | null;
  start_timestamp: EpochTimeStampSeconds | null;
  duration_ms: DOMHighResTimeStamp | null;
};

export type UserProperties = {
  id: string | null;
  visitor_id: string | null;
};

export type DiscoveryProperties = {
  // custom properties
  timestamp: EpochTimeStampSeconds | null;
  browser_referrer: string | null;

  // Known params
  gclid?: string;
  fbclid?: string;
  msclkid?: string;
  campaign?: string;
  source?: string;
  medium?: string;
  term?: string;
  content?: string;

  // catch-all for additional UTM params
  extra_utm_params: KeyValueArray | null;
};

export type TargetProperties = {
  type: string | null;
  id: string | null;
  text: string | null;
  attributes: KeyValueArray | null;
};

export type BrowserEventPayload = {
  action: string;
  timestamp: EpochTimeStampSeconds;
  target: TargetProperties | null;
  device: DeviceProperties;
  page: PageProperties;
  session: SessionProperties | null;
  user: UserProperties;
  discovery: DiscoveryProperties | null;
  extra?: KeyValueArray;
};
