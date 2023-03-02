function buildConfig() {
  const config = {
    extends: [
      './node_modules/@bricker/tooling-configs/configs/eslintrc.cjs',
    ],
    ignorePatterns: [
      '*.graphql',
    ],
    // Add your config overrides here
    overrides: [
      {
        files: ['*.ts'],
        extends: ['plugin:@typescript-eslint/recommended'],
        plugins: ['@typescript-eslint'],
        parser: '@typescript-eslint/parser',
        rules: {
          '@typescript-eslint/no-non-null-assertion': 'off',
          'import/prefer-default-export': 'off',
          'dot-notation': 'off',
          'no-use-before-define': ['error', {
            functions: false,
            classes: false,
            variables: true,
          }],
        },
      },
    ],
  };

  return config;
}

module.exports = buildConfig();
