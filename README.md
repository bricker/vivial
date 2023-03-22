## Setup

Start by running `./bin/setup` in your current shell.

### Environment Variables

The setup script will create a gitignored `.env` file in each of the app roots, with a list of environment variables that the app uses. Before running an app, you should fill these out. Some environment variables have defaults and can be left undefined (see the corresponding config.* file for more info).

The format of the `.env` file isn't formally specified anywhere, but it should be parseable by [python-dotenv](https://github.com/theskumar/python-dotenv#file-format).

## IDE

For the fastest setup, built-in configuration, debug scripts, and more, it is recommended to use VSCode for development in this repository.

To get started, open `.vscode/eave.code-workspace` in VSCode.

## Running apps

Each app has a VSCode launch configuration, which you can use from the "Run and Debug" pane in VSCode.

### Running the proxy

This repository comes with a reverse proxy that listens on *.eave.run:8080 and routes traffic similarly to our production load balancer. To run the proxy:

```bash
$EAVE_HOME/bin/proxy
```

Now, you can develop using more meaningful URLs, that more closely match production, and are all accessible on the same port, eg:

- `http://api.eave.run:8080/status`
- `http://apps.eave.run:8080/slack/status`
- `http://www.eave.run:8080`

Note: Although the proxy is running and forwarding requests, you still need to run the apps (through the VSCode Launch configurations, for example) to be able to access them through the proxy.

Note: The proxy serves traffic over unencrypted HTTP connections.
