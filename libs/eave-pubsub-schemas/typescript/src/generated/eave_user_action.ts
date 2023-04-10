/* eslint-disable */

export interface EaveUserAction {
  action: EaveUserAction_Action | undefined;
  message_source: string;
}

export interface EaveUserAction_Action {
  platform: string;
  name: string;
  description: string;
  opaque_params: string;
  eave_user_id: string;
  user_ts: number;
}
