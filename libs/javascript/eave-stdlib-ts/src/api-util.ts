import { Status } from './core-api/operations';
import { sharedConfig } from './config';

export function statusPayload(): Status.ResponseBody {
  return {
    "service": sharedConfig.appService,
    "version": sharedConfig.appVersion,
    "status": "OK",
  }
}

export interface ResponseInterface {
  json(payload: any): ResponseInterface;
  status(code: number): ResponseInterface;
  end(): ResponseInterface;
}

export interface RouterInterface {
  get(path: string, ...handlers: ((_: any, res: ResponseInterface) => any)[]): any;
}

export function addStandardEndpoints(app: RouterInterface, pathPrefix: string = '') {
  app.get(`${pathPrefix}/status`, (_: unknown, res: ResponseInterface) => {
    const payload = statusPayload();
    res.json(payload).status(200).end();
  });
}
