import { avaConfig } from '@bricker/tooling-configs';

export default ({ projectDir }) => {
  const config = {
    // Add your config overrides here
    ...avaConfig({ projectDir }),
  };

  return config;
};
