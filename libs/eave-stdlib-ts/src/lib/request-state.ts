import { Request } from "express";


const SCOPE_KEY = 'eave_state';

export type EaveRequestState = {
  eave_account_id?: string;
  eave_team_id?: string;
  eave_origin?: string;
  request_id?: string;
  request_method?: string;
  request_scheme?: string;
  request_path?: string;
  request_headers?: { [key: string]: string };
}

export function getEaveState(req: Request): EaveRequestState {
  normalizeScope(req);
  return <EaveRequestState>(<any>req)['extensions'][SCOPE_KEY];
}

export function setEaveScope(req: Request, eaveState: EaveRequestState): void {
  normalizeScope(req);
  (<any>req)['extensions'][SCOPE_KEY] = eaveState;
}

/**
 * Update the provided request with the scope extensions.
 * 
 * @param req request to add/edit extensions scope to
 */
function normalizeScope(req: Request): void {
  if ((<any>req)['extensions'] === undefined) {
    (<any>req)['extensions'] = { [SCOPE_KEY]: {} };
  }
}