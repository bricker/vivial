import fetch from 'node-fetch';
import appSettings from '../settings.js';

enum DocumentPlatform {
  eave = 'eave',
  confluence = 'confluence',
}

type DocumentReference = {
  id: string;
  documentId: string;
  documentUrl: string;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent?: EaveDocument;
}

export enum SubscriptionSourceEvent {
  github_file_change = 'github.file_change',
}

export type SubscriptionSource = {
  platform: string;
  event: SubscriptionSourceEvent;
  id: string;
}

type Subscription = {
  id: string;
  documentReferenceId?: string;
  source: SubscriptionSource;
}

type Team = {
  id: string;
  name: string;
  documentPlatform: DocumentPlatform;
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
  async upsertDocument(document: EaveDocument, source: SubscriptionSource, addlHeaders: object | undefined = undefined): Promise<UpsertDocumentResponse> {
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/documents/upsert`, {
      method: 'post',
      body: JSON.stringify({
        document,
        subscription: { source },
      }),
      headers: {
        'content-type': 'application/json',
        'eave-team-id': appSettings.eaveTeamId,
        ...addlHeaders,
      },
    });

    const data = <UpsertDocumentResponse>(await resp.json());
    return data;
  }

  async getOrCreateSubscription(source: SubscriptionSource): Promise<SubscriptionResponseWithMetadata> {
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/subscriptions/create`, {
      method: 'post',
      body: JSON.stringify({
        subscription: { source },
      }),
      headers: {
        'content-type': 'application/json',
        'eave-team-id': appSettings.eaveTeamId,
      },
    });

    const data = <SubscriptionResponse>(await resp.json());
    return {
      ...data,
      status: resp.status,
      created: resp.status === 201,
    };
  }

  async getSubscription(source: SubscriptionSource): Promise<SubscriptionResponse | null> {
    const resp = await fetch(`${appSettings.eaveCoreApiUrl}/subscriptions/query`, {
      method: 'post',
      body: JSON.stringify({
        subscription: { source },
      }),
      headers: {
        'content-type': 'application/json',
        'eave-team-id': appSettings.eaveTeamId,
      },
    });

    if (resp.status > 299) {
      return null;
    }

    const data = <SubscriptionResponse>(await resp.json());
    return data;
  }
}

const defaultClient = new EaveCoreClient();
export default defaultClient;
