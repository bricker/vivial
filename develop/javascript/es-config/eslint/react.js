const config = {
  extends: [
    'plugin:react/recommended',
  ],
  plugins: [
    'react',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'react/jsx-filename-extension': 'off',
    'react/prop-types': 'off',
    'react/prefer-stateless-function': 'off',
    'react/jsx-one-expression-per-line': 'off',
  },
};

module.exports = config;
