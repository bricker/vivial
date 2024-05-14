# Eave Client JS e2e test app

A simple React app with the sole purpose of testing/validating the eave-client analytics atom collection JS script.
Running `npm run e2e-test` in the root NPM project will run the tests in this project against the dummy React app.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3300](http://localhost:3300) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Runs the cypress e2e tests located in the `cypress/e2e/` directory. Runs tests in headless mode.

If running locally, recommended to run `npm run cy:open` to run tests in GUI. Seeing things occasionally helps.
Cypress tests require the React app server to be actively running to run tests against. You can do this with `npm start`.

### `EAVE_CLIENT_ID` environment variable

The `EAVE_CLIENT_ID` environment variable _must_ be set when running the integration tests. This is the client ID used when sending atoms to the core API.

To get the client ID, run the setup-db script in core API, and then copy the ID from one the `client_credentials` records created by the script.

See https://docs.cypress.io/guides/guides/environment-variables for how to set the environment variable. The easiest way is to create a `cypress.env.json` file in this directory that looks something like this:

```json
{
  "EAVE_CLIENT_ID": "259ed872-2619-4322-bf52-0f6cbace3bcc"
}
```

Note that the `cypress.env.json` file is gitignored because the client ID is different across developer machines; however, the `EAVE_CLIENT_ID` value is not sensitive.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
