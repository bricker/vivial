import { CloudTasksClient, protos } from "@google-cloud/tasks";
import { Request } from "express";
import assert from "node:assert";
import { constants as httpConstants } from "node:http2";
import { ClientApiEndpointConfiguration } from "./api-util.js";
import { sharedConfig } from "./config.js";
import { EaveApp } from "./eave-origins.js";
import {
  EAVE_ACCOUNT_ID_HEADER,
  EAVE_ORIGIN_HEADER,
  EAVE_REQUEST_ID_HEADER,
  EAVE_SIGNATURE_HEADER,
  EAVE_SIG_TS_HEADER,
  EAVE_TEAM_ID_HEADER,
  GCP_CLOUD_TRACE_CONTEXT,
  GCP_GAE_REQUEST_LOG_ID,
  MIME_TYPE_JSON,
} from "./headers.js";
import { LogContext, eaveLogger } from "./logging.js";
import { CtxArg, makeRequest } from "./requests.js";
import Signing, { buildMessageToSign, makeSigTs } from "./signing.js";
import { ExpressRoutingMethod } from "./types.js";

// document me

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

/**
 * This function creates a task from a request. It first wraps the context with the request, then checks if a uniqueTaskId is provided.
 * If not, it tries to extract it from the request headers. It then constructs a payload from the request body and headers.
 * It removes the user agent from the headers as it's not relevant for the task processor.
 * Finally, it calls the createTask function with the constructed parameters.
 *
 * @param {Object} args - The arguments for the function.
 * @param {string} args.queueName - The name of the queue where the task will be created.
 * @param {string} args.targetPath - The target path for the task.
 * @param {string} args.origin - The origin of the task.
 * @param {string} args.audience - The audience for the task.
 * @param {string} [args.uniqueTaskId] - The unique ID for the task. If not provided, it will be extracted from the request headers.
 * @param {string} args.taskNamePrefix - The prefix for the task name.
 * @param {Object} args.req - The request object from which the task is created.
 * @param {Object} args.ctx - The context for the task.
 *
 * @returns {Promise<void>} A promise that resolves when the task is created.
 *
 * @throws {Error} If the uniqueTaskId cannot be extracted from the request headers.
 */
export async function createTaskFromRequest({
  queueName,
  targetPath,
  origin,
  audience,
  uniqueTaskId,
  taskNamePrefix,
  req,
  ctx,
}: CreateTaskFromRequestArgs): Promise<void> {
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

/**
 * Asynchronously creates a task in Google Cloud Tasks.
 *
 * @param {CreateTaskArgs} args - The arguments to create a task.
 * @param {string} args.queueName - The name of the queue where the task will be created.
 * @param {string} args.targetPath - The relative URI path that the request will be sent to.
 * @param {Buffer|string|Object} args.payload - The payload that will be sent in the HTTP request body.
 * @param {Object} [args.headers={}] - Additional HTTP headers to send with the request.
 * @param {string} args.origin - The origin of the request.
 * @param {string} args.audience - The audience of the request.
 * @param {string} [args.uniqueTaskId] - A unique identifier for the task. If not provided, Cloud Tasks will automatically generate one.
 * @param {string} [args.taskNamePrefix] - A prefix for the task name. This will be prepended to the uniqueTaskId.
 * @param {Object} args.ctx - The context of the request.
 *
 * @returns {Promise<void>} A promise that resolves when the task is successfully created.
 *
 * @throws {AssertionError} If the task's appEngineHttpRequest is not defined.
 *
 * @example
 * createTask({
 *   queueName: 'my-queue',
 *   targetPath: '/my-path',
 *   payload: { foo: 'bar' },
 *   headers: { 'Content-Type': 'application/json' },
 *   origin: 'my-origin',
 *   audience: 'my-audience',
 *   uniqueTaskId: 'my-unique-task-id',
 *   taskNamePrefix: 'my-task-name-prefix',
 *   ctx: { eave_request_id: 'my-request-id', eave_team_id: 'my-team-id', eave_account_id: 'my-account-id' },
 * });
 */
export async function createTask({
  queueName,
  targetPath,
  payload,
  headers,
  origin,
  audience,
  uniqueTaskId,
  taskNamePrefix,
  ctx,
}: CreateTaskArgs): Promise<void> {
  ctx = LogContext.wrap(ctx);

  if (!headers) {
    headers = {};
  }

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

  headers[httpConstants.HTTP2_HEADER_CONTENT_TYPE] = MIME_TYPE_JSON;
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
  const parent = client.queuePath(
    sharedConfig.googleCloudProject,
    sharedConfig.appLocation,
    queueName,
  );

  const task: protos.google.cloud.tasks.v2.ITask = {
    appEngineHttpRequest: {
      headers,
      httpMethod: "POST",
      relativeUri: targetPath,
      body: Buffer.from(body).toString("base64"),
    },
  };

  assert(task.appEngineHttpRequest);

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

  eaveLogger.debug(`Creating task on queue ${queueName}`, ctx, {
    // fields are snake cased for consistency with Python
    task: {
      name: task.name,
      body: task.appEngineHttpRequest.body?.toString(),
      headers: task.appEngineHttpRequest.headers,
    },
    queue_name: parent,
  });

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
