import AddOnFactory from 'atlassian-connect-express';

class EaveApiAdapter /* implements StoreAdapter */ {
  async get(key: string, clientKey: string): Promise<any> {

  }

  async set(key: string, value: any, clientKey: string): Promise<any> {
  }

  async del(key: string, clientKey: string): Promise<void> {
  }

  async getAllClientInfos(): Promise<AddOnFactory.ClientInfo[]> {
    return [];
  }

  isMemoryStore() {
    return false;
  }
}

module.exports = EaveApiAdapter;
