import fetch, { RequestInit } from 'node-fetch';
import jws from 'jws';
import appSettings from '../config.js';
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

class EaveCoreClient {
  async upsertDocument(document: EaveDocument, source: SubscriptionSource): Promise<UpsertDocumentResponse> {
    const inputData = {
      document,
      subscription: { source },
    };

    const request = await this.initRequest(inputData);
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/documents/upsert`, request);

    const responseData = <UpsertDocumentResponse>(await resp.json());
    return responseData;
  }

  async getOrCreateSubscription(source: SubscriptionSource): Promise<SubscriptionResponseWithMetadata> {
    const inputData = {
      subscription: { source },
    };

    const request = await this.initRequest(inputData);
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/subscriptions/create`, request);

    const responseData = <SubscriptionResponse>(await resp.json());
    return {
      ...responseData,
      status: resp.status,
      created: resp.status === 201,
    };
  }

  async getSubscription(source: SubscriptionSource): Promise<SubscriptionResponse | null> {
    const inputData = {
      subscription: { source },
    };

    const request = await this.initRequest(inputData);
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/subscriptions/query`, request);

    if (resp.status > 299) {
      return null;
    }

    const responseData = <SubscriptionResponse>(await resp.json());
    return responseData;
  }

  private async initRequest(data: JsonValue): Promise<RequestInit> {
    const payload = JSON.stringify(data);
    const signature = await this.signPayload(payload);

    return {
      method: 'post',
      body: payload,
      headers: {
        'content-type': 'application/json',
        'eave-team-id': appSettings.eaveTeamId,
        'eave-signature': signature,
      },
    };
  }

  private async signPayload(payload: JsonValue): Promise<string> {
    const secret = await appSettings.eaveSigningSecret;
    const signature = jws.sign({
      header: { alg: 'HS256' },
      payload,
      secret,
    });
    return signature;
  }
}

const defaultClient = new EaveCoreClient();
export default defaultClient;
