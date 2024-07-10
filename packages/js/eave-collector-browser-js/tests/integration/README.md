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

Any flags passed will be passed on to the `cy:test` command. e.g. to run a specific test: `npm test -- --spec cypress/e2e/clickSpec.cy.js`

If running locally, recommended to run `npm run cy:open` to run tests in GUI. Seeing things occasionally helps.
Cypress tests require the React app server to be actively running to run tests against. You can do this with `npm start`.

### `cy:test`

Runs cypress tests via `cypress run` CLI. Expects the react app under test to be running separately on localhost
before this command is run.

### `cy:open`

Opens the cypress test GUI. In order to run any of the tests in the GUI, you will need to separately run
the react app.

This command can be helpful in visually debugging test failures.

## Debugging

This can be challenging in cypress specs, since they eat `console.log`s. You're best off using
the `debugger` key word. More info in the [cypress docs](https://docs.cypress.io/guides/guides/debugging).

This only works when using `cy:open` to run the tests in a GUI and while the browser inspector is open
on the GUI while the test is running.
