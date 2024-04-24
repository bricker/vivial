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

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
