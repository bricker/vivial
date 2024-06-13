export type JsonScalar = string | number | boolean | null | undefined;
export type JsonObject = {
  [key: string]: JsonScalar | JsonScalar[] | JsonObject | JsonObject[];
};
export type JsonValue = JsonScalar | JsonScalar[] | JsonObject | JsonObject[];

export type ScalarMap<T extends JsonScalar> = { [key: string]: T };

// export type KeyValueDict = {
//   key: string;
//   value: JsonScalar;
// };

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
};

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

export type CurrentPageProperties = {
  url: string;
  title: string;
  pageview_id: string;
};

export type SessionProperties = {
  id: string | null;
  start_timestamp: EpochTimeStampSeconds | null;
};

// export type UserProperties = {
//   account_id: string | null;
//   visitor_id: string | null;
// };

export type TrafficSourceProperties = {
  timestamp: EpochTimeStampSeconds | null;
  browser_referrer: string | null;
  tracking_params: ScalarMap<string> | null;
  // gclid: string | null;
  // fbclid: string | null;
  // msclkid: string | null;
  // dclid: string | null;
  // ko_click_id: string | null;
  // rtd_cid: string | null;
  // li_fat_id: string | null;
  // ttclid: string | null;
  // twclid: string | null;
  // wbraid: string | null;
  // gbraid: string | null;
  // keyword: string | null;
  // matchtype: string | null;
  // campaign: string | null;
  // campaign_id: string | null;
  // pid: string | null;
  // cid: string | null;
  // utm_campaign: string | null;
  // utm_source: string | null;
  // utm_medium: string | null;
  // utm_term: string | null;
  // utm_content: string | null;
  // other_utm_params: ScalarMap<string> | null;
};

export type TargetProperties = {
  type: string | null;
  id: string | null;
  content: string | null;
  attributes: ScalarMap<string> | null;
};

export type BrowserEventPayload = {
  action: string;
  timestamp: EpochTimeStampSeconds;
  target: TargetProperties | null;
  device: DeviceProperties | null;
  current_page: CurrentPageProperties | null;
  extra?: ScalarMap<JsonScalar> | null;
  corr_ctx: ScalarMap<string>;
  // session: SessionProperties | null;
  // user: UserProperties | null;
  // traffic_source: TrafficSourceProperties | null;
};
