export type StringMap<T extends string | string[]> = { [key: string]: T };

export type JSONScalar = string | number | boolean | null | undefined;
export type JSONObject = {
  [key: string]: JSONScalar | JSONScalar[] | JSONObject | JSONObject[];
};
export type JSONValue = JSONScalar | JSONScalar[] | JSONObject | JSONObject[];

export type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR" | "SILENT";

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
  setLogLevel: (level: LogLevel) => void;
};

export type GlobalEaveState = {
  pageViewId: string;
};

export type GlobalEaveWindow = Window &
  EaveConfiguration & { eave: EaveInterface };

export type UserAgentProperties = {
  ua_string: string;
  brands?: {
    brand: string;
    version: string;
  }[];
  platform?: string;
  mobile?: boolean;
  form_factor?: string;
  full_version_list?: {
    brand: string;
    version: string;
  }[];
  model?: string;
  platform_version?: string;
};

export type ScreenProperties = {
  width: number;
  height: number;
  avail_width: number;
  avail_height: number;
};

export type PerformanceProperties = {
  network_latency_ms: DOMHighResTimeStamp;
  dom_load_latency_ms: DOMHighResTimeStamp;
};

export type PageProperties = {
  current_url: string;
  current_title: string;
  pageview_id: string;
  current_query_params: StringMap<string[]>;
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
  campaign?: string;
  gclid?: string;
  fbclid?: string;

  // catch-all for additional UTM params
  utm_params: StringMap<string>;
};

export type TargetProperties = {
  type: string | null;
  id: string | null;
  text: string | null;
  attributes: StringMap<string> | null;
};

export type EventProperties = {
  action: string;
  timestamp: EpochTimeStampSeconds;
  origin_elapsed_ms?: DOMHighResTimeStamp;
  target: TargetProperties | null;
};

export type BrowserEventPayload = {
  user_agent: UserAgentProperties;
  screen: ScreenProperties;
  performance: PerformanceProperties | null;
  page: PageProperties;
  session: SessionProperties | null;
  user: UserProperties;
  discovery: DiscoveryProperties | null;
  event: EventProperties;
  cookies: StringMap<string> | null;
  extra?: JSONObject;
};
