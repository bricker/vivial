const config = {
  extends: ["plugin:react/recommended"],
  plugins: ["react"],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    "react/jsx-filename-extension": "off",
    "react/prop-types": "off",
    "react/prefer-stateless-function": "off",
    "react/jsx-one-expression-per-line": "off",
    "react/no-unescaped-entities": "off",
    "react/jsx-max-props-per-line": ["error", { maximum: 1, when: "multiline" }],
  },
};

module.exports = config;
