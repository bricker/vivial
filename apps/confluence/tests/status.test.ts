import { v4 as uuidv4 } from 'uuid';
import anyTest, { TestFn } from 'ava';
import request from 'supertest';
import { app } from '../src/app.js';

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
  u: TestUtil;
}

const test = anyTest as TestFn<TestContext>;

test.beforeEach((t) => {
  t.context = {
    u: new TestUtil(),
  };
});

test.afterEach((t) => {
});

test('status', async (t) => {
  const response = await request(app).get('/confluence/status');
  t.assert(response.status === 200);
  t.assert(response.body['status'] === 'OK');
});
