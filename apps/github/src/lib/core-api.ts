import crypto from 'crypto';
import fetch, { RequestInit } from 'node-fetch';
import appConfig from '../config.js';
import { JsonValue } from '../types.js';

enum DocumentPlatform {
  eave = 'eave',
  confluence = 'confluence',
}

type DocumentReference = {
  id: string;
  document_id: string;
  document_url: string;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent?: EaveDocument;
}

export enum SubscriptionSourcePlatform {
  slack = 'slack',
  github = 'github',
  jira = 'jira',
}

export enum SubscriptionSourceEvent {
  jira_issue_comment = 'jira_issue_comment',
  github_file_change = 'github_file_change',
}

export type SubscriptionSource = {
  platform: string;
  event: SubscriptionSourceEvent;
  id: string;
}

type Subscription = {
  id: string;
  document_reference_id?: string;
  source: SubscriptionSource;
}

type Team = {
  id: string;
  name: string;
  document_platform: DocumentPlatform;
}

type UpsertDocumentResponse = {
  team: Team;
  subscription: Subscription;
  document_reference: DocumentReference;
}

type SubscriptionResponse = {
  team: Team;
  subscription: Subscription;
  document_reference?: DocumentReference;
}

type SubscriptionResponseWithMetadata = SubscriptionResponse & {
  status: number;
  created: boolean;
}

type StatusResponse = {
  service: string;
  version: string;
  status: string;
}

export async function status(): Promise<StatusResponse> {
  const resp = await fetch(`${appConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <StatusResponse>(await resp.json());
  return responseData;
}
export async function upsertDocument(document: EaveDocument, source: SubscriptionSource, teamId: string): Promise<UpsertDocumentResponse> {
  const inputData = {
    document,
    subscription: { source },
  };

  const request = await initRequest(inputData, teamId);
  const resp = await fetch(`${appConfig.eaveApiBase}/documents/upsert`, request);

  const responseData = <UpsertDocumentResponse>(await resp.json());
  return responseData;
}

export async function createSubscription(source: SubscriptionSource, teamId: string): Promise<SubscriptionResponseWithMetadata> {
  const inputData = {
    subscription: { source },
  };

  const request = await initRequest(inputData, teamId);
  const resp = await fetch(`${appConfig.eaveApiBase}/subscriptions/create`, request);

  const responseData = <SubscriptionResponse>(await resp.json());
  return {
    ...responseData,
    status: resp.status,
    created: resp.status === 201,
  };
}

export async function getSubscription(source: SubscriptionSource, teamId: string): Promise<SubscriptionResponse | null> {
  const inputData = {
    subscription: { source },
  };

  const request = await initRequest(inputData, teamId);
  const resp = await fetch(`${appConfig.eaveApiBase}/subscriptions/query`, request);

  if (resp.status > 299) {
    return null;
  }

  const responseData = <SubscriptionResponse>(await resp.json());
  return responseData;
}

async function initRequest(data: JsonValue, teamId: string | undefined = undefined): Promise<RequestInit> {
  const payload = JSON.stringify(data);
  const signature = await computeSignature(payload, teamId);

  return {
    method: 'post',
    body: payload,
    headers: {
      'content-type': 'application/json',
      'eave-team-id': appConfig.eaveTeamId,
      'eave-signature': signature,
    },
  };
}

async function computeSignature(payload: string, teamId: string | undefined = undefined): Promise<string> {
  const key = await appConfig.eaveSigningSecret;
  const hmac = crypto.createHmac('sha256', key);

  if (teamId !== undefined) {
    hmac.update(teamId);
  }

  hmac.update(payload);
  return hmac.digest('hex');
}
