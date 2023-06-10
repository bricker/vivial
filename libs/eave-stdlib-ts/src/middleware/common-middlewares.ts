import { Express, NextFunction, Request, RequestHandler, Response } from 'express';
import helmet from 'helmet';
import { requestIntegrity } from './request-integrity.js';
import { requestLoggingMiddleware } from './logging.js';

const atlassianHeaderMiddleware = (_req: Request, res: Response, next: NextFunction) => {
  res.setHeader('Surrogate-Control', 'no-store');
  res.setHeader(
    'Cache-Control',
    'no-store, no-cache, must-revalidate, proxy-revalidate',
  );
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');

  next();
};

// Atlassian security policy requirements
// http://go.atlassian.com/security-requirements-for-cloud-apps
// HSTS must be enabled with a minimum age of at least one year

export const securityMiddlewares: RequestHandler[] = [
  helmet.hsts({
    maxAge: 31536000,
    includeSubDomains: false,
  }),

  helmet.referrerPolicy({
    policy: ['origin'],
  }),

  helmet.xPoweredBy(),

  atlassianHeaderMiddleware,
];

export const genericMiddlewares: RequestHandler[] = [
  requestIntegrity,
  requestLoggingMiddleware,
]
