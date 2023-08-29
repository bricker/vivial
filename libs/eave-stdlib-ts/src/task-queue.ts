import { constants as httpConstants } from 'node:http2';
import { Request } from 'express';
import { CloudTasksClient, protos } from '@google-cloud/tasks';
import { EaveOrigin } from './eave-origins.js';
import { CtxArg } from './requests.js';
import headersImport from './headers.js';
import eaveLogger, { LogContext } from './logging.js';
import Signing, { buildMessageToSign } from './signing.js';
import { sharedConfig } from './config.js';

type CreateTaskSharedArgs = CtxArg & {
  queueName: string,
  targetPath: string,
  origin: EaveOrigin,
  uniqueTaskId?: string,
  taskNamePrefix?: string,
}

type CreateTaskArgs = CreateTaskSharedArgs & {
  payload: Buffer | object | string,
  headers?: {[key:string]: string},
}

type CreateTaskFromRequestArgs = CreateTaskSharedArgs & {
  req: Request,
}

export async function createTaskFromRequest({
  queueName,
  targetPath,
  origin,
  uniqueTaskId,
  taskNamePrefix,
  req,
  ctx,
}: CreateTaskFromRequestArgs): Promise<void> {
  ctx = LogContext.wrap(ctx, req);

  if (!uniqueTaskId) {
    const traceId = req.header(headersImport.GCP_CLOUD_TRACE_CONTEXT);
    const logId = req.header(headersImport.GCP_GAE_REQUEST_LOG_ID);

    if (traceId) {
      uniqueTaskId = traceId.split('/')[0];
    } else if (logId) {
      uniqueTaskId = logId;
    }
  }

  const payload = req.body;
  const headers: {[key:string]: string} = {};
  // FIXME: Is there a cleaner way to do this? req.headers is a NodeJS.Dict typescript object.
  for (const key in req.headers) { // eslint-disable-line no-restricted-syntax
    if (Object.hasOwn(req.headers, key)) {
      // express joins array values into string values for headers
      const value = req.header(key)!;
      headers[key] = value;
    }
  }

  // The "user agent" is the GitHub webhook deliverer, but when passing off to the task processor, that's not true.
  // GCP Task Queue merges the user agents.
  delete headers[httpConstants.HTTP2_HEADER_USER_AGENT];

  await createTask({
    queueName,
    targetPath,
    origin,
    uniqueTaskId,
    taskNamePrefix,
    payload,
    headers,
    ctx,
  });
}

export async function createTask({
  queueName,
  targetPath,
  payload,
  headers,
  origin,
  uniqueTaskId,
  taskNamePrefix,
  ctx,
}: CreateTaskArgs): Promise<protos.google.cloud.tasks.v2.ITask> {
  ctx = LogContext.wrap(ctx);

  if (!headers) {
    headers = {};
  }

  headers[httpConstants.HTTP2_HEADER_CONTENT_TYPE] = headersImport.MIME_TYPE_JSON;

  let body: string;
  if (payload instanceof Buffer) {
    body = payload.toString();
  } else if (typeof payload === 'string') {
    body = payload;
  } else {
    body = JSON.stringify(payload);
  }

  const signatureMessage = buildMessageToSign({
    method: httpConstants.HTTP2_METHOD_POST,
    url: targetPath,
    requestId: ctx.eave_request_id,
    origin,
    payload: body,
    teamId: ctx.eave_team_id,
    accountId: ctx.eave_account_id,
    ctx,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(signatureMessage);

  headers[headersImport.EAVE_SIGNATURE_HEADER] = signature;
  headers[headersImport.EAVE_REQUEST_ID_HEADER] = ctx.eave_request_id;
  headers[headersImport.EAVE_ORIGIN_HEADER] = origin;

  if (ctx.eave_account_id) {
    headers[headersImport.EAVE_ACCOUNT_ID_HEADER] = ctx.eave_account_id;
  }

  if (ctx.eave_team_id) {
    headers[headersImport.EAVE_TEAM_ID_HEADER] = ctx.eave_team_id;
  }

  const client = new CloudTasksClient();
  const parent = client.queuePath(
    sharedConfig.googleCloudProject,
    sharedConfig.appLocation,
    queueName,
  );

  const task: protos.google.cloud.tasks.v2.ITask = {
    appEngineHttpRequest: {
      headers,
      httpMethod: 'POST',
      relativeUri: targetPath,
      body,
    },
  };

  if (uniqueTaskId) {
    if (taskNamePrefix) {
      uniqueTaskId = `${taskNamePrefix}${uniqueTaskId}`;
    }

    // If this isn't given, Cloud Tasks creates a unique task name automatically.
    task.name = client.taskPath(
      sharedConfig.googleCloudProject,
      sharedConfig.appLocation,
      queueName,
      uniqueTaskId,
    );
  }

  eaveLogger.debug(
    `Creating task on queue ${queueName}`,
    ctx,
    {
      // fields are snake cased for consistency with Python
      task_name: task.name,
      queue_name: parent,
    },
  );

  // if (sharedConfig.isDevelopment) {
  //   // FIXME: This is a hack
  //   await fetch(`http://localhost:${process.env['PORT']}/${targetPath}`, {
  //     method: httpConstants.HTTP2_METHOD_POST,
  //     body,
  //     headers,
  //   });
  // }

  const [responseTask] = await client.createTask({ parent, task });
  return responseTask;
}
