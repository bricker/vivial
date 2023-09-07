import { v4 as uuidv4 } from 'uuid';

export class TestUtil {
  testData: { [key: string]: any } = {};

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

export interface TestContextBase {
  u: TestUtil;
}
