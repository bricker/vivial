/* eslint-disable */

export interface EaveUserAction {
  action_name: string;
  description: string;
  opaque_params: { [key: string]: string };
  eave_account_id: string;
  event_ts: number;
  event_source: string;
  visitor_id: string;
}

export interface EaveUserAction_OpaqueParamsEntry {
  key: string;
  value: string;
}
