import { avaConfig } from './index.js';

export default ({ projectDir }) => {
  return {
    // Add your config overrides here
    ...avaConfig({ projectDir }),
  };
};
