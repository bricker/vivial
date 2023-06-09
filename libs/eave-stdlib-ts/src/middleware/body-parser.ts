import { Request, Response, NextFunction } from 'express';
import eaveLogger from '../logging.js';

/*
Simple JSON body parser. Similar to body-parser's json parser, but different in two ways:
1. Does no sort of validation. Assumes that the body is JSON-serialized.
2. Always replaces the existing `req.body` attribute with the parsed JSON.
body-parser's json parser won't parse the body if the body was already read.
For our services, we use the "raw" parser, which marks the body as having been read,
and downstream parsers won't do any further processing.
See here: https://github.com/expressjs/body-parser/blob/ee91374eae1555af679550b1d2fb5697d9924109/lib/types/raw.js#L56
and here: https://github.com/expressjs/body-parser/blob/ee91374eae1555af679550b1d2fb5697d9924109/lib/read.js#L46
*/
export function bodyParser(req: Request, res: Response, next: NextFunction) {
  try {
    const rawBody = <Buffer>req.body;
    const parsedBody = JSON.parse(rawBody.toString());
    req.body = parsedBody;
    next();
  } catch (e: unknown) {
    eaveLogger.error({ message: 'Error during JSON parsing', exc: e });
    res.status(500).end();
  }
}
