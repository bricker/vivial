import { v4 as uuidv4 } from 'uuid';
import anyTest, { TestFn } from 'ava';
import sinon from 'sinon';
import request from 'supertest';
import ConfluenceClient from '../src/confluence-client.js';
import { app } from '../src/app.js';
import { HostClient } from 'atlassian-connect-express';
import * as signing from '@eave-fyi/eave-stdlib-ts/src/signing.js';
import { createHash } from 'crypto';

class TestUtil {
  testData: {[key:string]: any} = {};

  anystr(name: string): string {
    if (this.testData[name] === undefined) {
      this.testData[name] = uuidv4();
    }

    return this.testData[name];
  }

  getstr(name: string): string {
    return this.testData[name];
  }
}

interface TestContext {
  sandbox: sinon.SinonSandbox;
  confluenceClient: sinon.SinonStubbedInstance<ConfluenceClient>;
  signing: sinon.SinonStubbedInstance<Signing>;
  u: TestUtil;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const mockConfluenceClient = new ConfluenceClient(<any>null); // client doesn't matter
  const confluenceClient = sandbox.stub(mockConfluenceClient);
  sandbox.stub(ConfluenceClient, 'getAuthedConnectClient').returns(Promise.resolve(confluenceClient));

  const mockSigning = new signing.default('eave_www');
  const s = sandbox.stub(signing, 'default').returns(mockSigning);
  s.signBase64.callsFake(async (data: string | Buffer): Promise<string> => {
    return createHash('sha256')
      .update(data)
      .digest().toString();
  });
  signing.verifySignatureOrException.callsFake(async (message: string | Buffer, signature: string | Buffer): Promise<boolean> => {
    return true;
    // return signature === createHash('sha256')
    //   .update(message)
    //   .digest().toString();
  });

  t.context = {
    sandbox,
    confluenceClient,
    signing,
    u: new TestUtil(),
  };
});

test.afterEach((t) => {
  t.context.sandbox.restore();
});

test('createContent', async (t) => {
  const response = await request(app)
    .post('/confluence/api/content/create')
    .set({
      'eave-team-id': t.context.u.anystr('team id'),
      'eave-origin': 'eave_www',
      'eave-signature': 'xxx',
    })
    .send({
      confluence_destination: {
        space_key: t.context.u.anystr('space_key'),
      },
      document: {
        title: t.context.u.anystr('doc title'),
        content: t.context.u.anystr('doc content'),
      },
    });

  t.assert(t.context.confluenceClient.getSpaceByKey.called);
  t.assert(response !== null);
});
