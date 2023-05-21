import { Response } from 'express';

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

export function getEaveState(res: Response): EaveRequestState {
  normalizeScope(res);
  return <EaveRequestState>res.locals[SCOPE_KEY];
}

export function setEaveState(res: Response, eaveState: EaveRequestState): void {
  normalizeScope(res);
  res.locals[SCOPE_KEY] = eaveState;
}

/**
 * Update the provided response.locals with the scope.
 *
 * @param res response to add/edit scope to
 */
function normalizeScope(res: Response): void {
  if (res.locals[SCOPE_KEY] === undefined) {
    res.locals[SCOPE_KEY] = {};
  }
}
