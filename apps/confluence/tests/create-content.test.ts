import anyTest, { TestFn } from 'ava';
import sinon from 'sinon';
import request from 'supertest';
import Signing, * as signing from '@eave-fyi/eave-stdlib-ts/src/signing.js';
import { TestContextBase, TestUtil } from '@eave-fyi/eave-stdlib-ts/src/test-util.js';
import { createHash } from 'crypto';
import { app } from '../src/app.js';
import ConfluenceClient from '../src/confluence-client.js';

interface TestContext extends TestContextBase {
  sandbox: sinon.SinonSandbox;
  confluenceClient: sinon.SinonStubbedInstance<ConfluenceClient>;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const mockConfluenceClient = new ConfluenceClient(<any>null); // client doesn't matter
  const confluenceClient = sandbox.stub(mockConfluenceClient);
  sandbox.stub(ConfluenceClient, 'getAuthedConfluenceClient').returns(Promise.resolve(confluenceClient));

  const mockSigning = new Signing('eave_www');
  sandbox.stub(Signing, 'new').returns(mockSigning);
  sandbox.stub(signing.default.prototype, 'signBase64').callsFake(async (data: string | Buffer): Promise<string> => {
    return createHash('sha256')
      .update(data)
      .digest().toString();
  });
  sandbox.stub(signing.default.prototype, 'verifySignatureOrException').callsFake(async (message: string | Buffer, signature: string | Buffer): Promise<boolean> => {
    return signature === createHash('sha256')
      .update(message)
      .digest().toString();
  });

  t.context = {
    sandbox,
    confluenceClient,
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
