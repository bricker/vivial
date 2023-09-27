import { CloudTasksClient, protos } from "@google-cloud/tasks";
import { Request } from "express";
import assert from "node:assert";
import { constants as httpConstants } from "node:http2";
import { ClientApiEndpointConfiguration } from "./api-util.js";
import { sharedConfig } from "./config.js";
import { EaveApp } from "./eave-origins.js";
import { EAVE_ACCOUNT_ID_HEADER, EAVE_ORIGIN_HEADER, EAVE_REQUEST_ID_HEADER, EAVE_SIGNATURE_HEADER, EAVE_SIG_TS_HEADER, EAVE_TEAM_ID_HEADER, GCP_CLOUD_TRACE_CONTEXT, GCP_GAE_REQUEST_LOG_ID, MIME_TYPE_JSON } from "./headers.js";
import { LogContext, eaveLogger } from "./logging.js";
import { CtxArg, makeRequest } from "./requests.js";
import Signing, { buildMessageToSign, makeSigTs } from "./signing.js";
import { ExpressRoutingMethod } from "./types.js";

type CreateTaskSharedArgs = CtxArg & {
  queueName: string;
  targetPath: string;
  origin: EaveApp;
  audience: EaveApp;
  uniqueTaskId?: string;
  taskNamePrefix?: string;
};

type CreateTaskArgs = CreateTaskSharedArgs & {
  payload: Buffer | object | string;
  headers?: { [key: string]: string };
};

type CreateTaskFromRequestArgs = CreateTaskSharedArgs & {
  req: Request;
};

export async function createTaskFromRequest({ queueName, targetPath, origin, audience, uniqueTaskId, taskNamePrefix, req, ctx }: CreateTaskFromRequestArgs): Promise<void> {
  ctx = LogContext.wrap(ctx, req);

  if (!uniqueTaskId) {
    const traceId = req.header(GCP_CLOUD_TRACE_CONTEXT);
    const logId = req.header(GCP_GAE_REQUEST_LOG_ID);

    if (traceId) {
      uniqueTaskId = traceId.split("/")[0];
    } else if (logId) {
      uniqueTaskId = logId;
    }
  }

  const payload = req.body;
  const headers: { [key: string]: string } = {};
  // FIXME: Is there a cleaner way to do this? req.headers is a NodeJS.Dict typescript object.
  // eslint-disable-next-line no-restricted-syntax
  for (const key in req.headers) {
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
    audience,
    uniqueTaskId,
    taskNamePrefix,
    payload,
    headers,
    ctx,
  });
}

export async function createTask({ queueName, targetPath, payload, headers, origin, audience, uniqueTaskId, taskNamePrefix, ctx }: CreateTaskArgs): Promise<void> {
  ctx = LogContext.wrap(ctx);

  if (!headers) {
    headers = {};
  }

  headers[httpConstants.HTTP2_HEADER_CONTENT_TYPE] = MIME_TYPE_JSON;

  let body: string;
  if (payload instanceof Buffer) {
    body = payload.toString();
  } else if (typeof payload === "string") {
    body = payload;
  } else {
    body = JSON.stringify(payload);
  }

  const eaveSigTs = makeSigTs();

  const signatureMessage = buildMessageToSign({
    method: httpConstants.HTTP2_METHOD_POST,
    path: targetPath,
    ts: eaveSigTs,
    requestId: ctx.eave_request_id,
    origin,
    audience,
    payload: body,
    teamId: ctx.eave_team_id,
    accountId: ctx.eave_account_id,
    ctx,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(signatureMessage);

  headers[EAVE_SIGNATURE_HEADER] = signature;
  headers[EAVE_REQUEST_ID_HEADER] = ctx.eave_request_id;
  headers[EAVE_ORIGIN_HEADER] = origin;
  headers[EAVE_SIG_TS_HEADER] = eaveSigTs.toString();

  if (!headers[EAVE_ACCOUNT_ID_HEADER] && ctx.eave_account_id) {
    headers[EAVE_ACCOUNT_ID_HEADER] = ctx.eave_account_id;
  }

  if (!headers[EAVE_TEAM_ID_HEADER] && ctx.eave_team_id) {
    headers[EAVE_TEAM_ID_HEADER] = ctx.eave_team_id;
  }

  const client = new CloudTasksClient();
  const parent = client.queuePath(sharedConfig.googleCloudProject, sharedConfig.appLocation, queueName);

  const task: protos.google.cloud.tasks.v2.ITask = {
    appEngineHttpRequest: {
      headers,
      httpMethod: "POST",
      relativeUri: targetPath,
      body,
    },
  };

  if (uniqueTaskId) {
    if (taskNamePrefix) {
      uniqueTaskId = `${taskNamePrefix}${uniqueTaskId}`;
    }

    // If this isn't given, Cloud Tasks creates a unique task name automatically.
    task.name = client.taskPath(sharedConfig.googleCloudProject, sharedConfig.appLocation, queueName, uniqueTaskId);
  }

  eaveLogger.debug(`Creating task on queue ${queueName}`, ctx, {
    // fields are snake cased for consistency with Python
    task_name: task.name,
    queue_name: parent,
  });

  assert(task.appEngineHttpRequest);

  if (sharedConfig.isDevelopment) {
    const host = sharedConfig.eavePublicServiceBase(origin);

    const endpointConfig: ClientApiEndpointConfiguration = {
      path: task.appEngineHttpRequest.relativeUri!,
      url: `${host}${task.appEngineHttpRequest.relativeUri}`,
      audience,
      method: ExpressRoutingMethod.post,
    };

    /*
    In development only, signature is done twice: once in this function, and again in `makeRequest`. Not ideal but not worth refactoring this function to prevent it.

    The purpose of having this development block at the bottom of the function is to run as much code as possible in development. Cloud Tasks doesn't have an official local emulator as of this writing, so placing a job on the queue isn't useful during development.

    So in development, we bypass the queue and make the request directly to the target app. It's not a great solution! [This](https://github.com/aertje/cloud-tasks-emulator) exists, but it's a) third-party, and b) requires either `go` or `docker`, which currently would complicate development/onboarding too much to be worth it.
    */
    await makeRequest({
      config: endpointConfig,
      origin,
      ctx,
      input: task.appEngineHttpRequest.body,
      addlHeaders: task.appEngineHttpRequest.headers || undefined,
    });
  }

  await client.createTask({ parent, task });
}
