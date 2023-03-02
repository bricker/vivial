# Eave GitHub App

A node server with an express frontend for accepting and routing requests for GitHub events.

## Development

This application is written in TypeScript. To setup and start the application for development:

1. `npm install`
1. `npm run setup`
1. Add a GitHub Personal Access Token to `secrets.json`
1. `npm run watch-dev`

Notes:

- The local server is run through `ts-node`, which compiles the TypeScript files at boot time.
- The `watch-dev` script runs the `ts-node` server through `nodemon`, a tool that watches for file changes and reloads the server.
- The information in `secrets.json` is only needed for local development. In production, the secrets are pulled from [Google Secret Manager](https://console.cloud.google.com/security/secret-manager).

## Deployment

This application is deployed to [Google AppEngine](https://console.cloud.google.com/appengine). Deployment is done through the `gcloud` CLI. See the [gcloud CLI documentation](https://cloud.google.com/sdk/gcloud) for setup instructions.

To do a basic, standard deployment, an npm script is provided:

```
npm run deploy
```

For detailed deployment instructions, refer to documentation for the `gcloud app` CLI tool (`gcloud app --help`).

## Runtime

This service is run on the `node16` runtime in Google AppEngine. More information can be found in the [Google AppEngine documentation](https://cloud.google.com/appengine/docs/standard/nodejs/runtime).

## Tests

### Linting

- The TypeScript compiler is configured to be strict, failing on violations.
- Additional linting is done by `eslint`. To lint the codebase, run: `npm run lint`.
