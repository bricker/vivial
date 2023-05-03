/* eslint-disable */

export interface EaveSystemAction {
  action_name: string;
  description: string;
  opaque_params: { [key: string]: string };
  event_ts: number;
  event_source: string;
}

export interface EaveSystemAction_OpaqueParamsEntry {
  key: string;
  value: string;
}
