## Setup

Start by running `./bin/setup` in your current shell.

### Environment Variables

The setup script will create a gitignored `.env` file in EAVE_HOME, with a list of environment variables that the apps use. Before running an app, you should fill these out. Some environment variables have defaults and can be left undefined (see the corresponding config.* file for more info).

The format of the `.env` file isn't formally specified anywhere, but it should be parseable by [python-dotenv](https://github.com/theskumar/python-dotenv#file-format).

## IDE

For the fastest setup, built-in configuration, debug scripts, and more, it is recommended to use VSCode for development in this repository.

To get started, open EAVE_HOME (this directory) in VSCode.

## Running apps

This VSCode workspace defines launch configurations for each app, which you can use from the "Run and Debug" pane in VSCode.

### Running the proxy

This repository comes with mitmproxy, configured as a pseudo-reverse proxy that listens on localhost:8080 and routes traffic based on the hostname and path, similar to our production load balancer. To run the proxy:

```bash
$EAVE_HOME/bin/http-proxy
```

Now, start whichever services you need, and access them using the respective domain (with TLD `localhost` and port `8080`). For example:

- `http://api.eave.localhost:8080` -> Core API
- `http://www.eave.localhost:8080` -> Website
- `http://apps.eave.localhost:8080/slack` -> Slack app
- `http://apps.eave.localhost:8080/github` -> GitHub app

This proxy serves three primary functions:

1. All local services can be accessed through the same port (8080), eliminating the need to remember which service is mapped to which port.
1. HTTPS URLs are supported by mitmproxy.
1. mitmproxy provides capabilities for viewing, modifying, and replaying the request/response cycle, to help debug HTTP requests.

Note: Although the proxy is running and forwarding requests, you still need to run the apps (through the VSCode Launch configurations, for example) to be able to access them through the proxy.

#### SSL

You can access your local apps over HTTPS, although it is not necessary in most cases. Testing OAuth is one example of when HTTPS may be necessary. HTTPS requests are supported out of the box, so you can visit `https://api.eave.localhost:8080` (for example) and the request will be processed. However, you are likely to receive a TLS warning or error from whichever application you're using (eg curl or Google Chrome), because the certificate used is self-signed and not trusted by any application by default.

This repository provides a self-signed certificate, which mitmproxy is configured to use for HTTPS requests. Additionally, this repository provides a script to install (trust) the certificate on your system, which is technically optional, but recommended. If you do not install and trust the certificate, the proxy can still serve HTTPS requests, but you'll have to always bypass the certificate security warnings (eg via `curl --insecure` or Chrome's "Proceed to ..." button).

To install and trust the self-signed certificate on your system, run the provided script at `${EAVE_HOME}/develop/certs/bin/install-certs` (*Note: This is so far only tested on Ubuntu. Please fix any issues you encounter.*). If necessary, you can update your `.env` file to change the base URLs to "https://..." (eg `EAVE_PUBLIC_WWW_BASE=https://www.eave.localhost`).

Alternatively, if you can't or don't want to use the provided self-signed certificate, you can install mitmproxy's self-signed certificate instead. See the [mitmproxy documentation](https://docs.mitmproxy.org/stable/concepts-certificates/) for details. (*Note: The `bin/proxy` script is configured to use the Eave self-signed certificate; changes to that script may be necessary to support mitmproxy's certificate)*

You should now be able to connect to your local services normally over HTTPS (without any connection warnings/errors).

A few things to be aware of:

1. The `install-certs` script adds the self-signed certificate to as many certificate stores on your system as possible, with the goal being that any application you're using will accept the certificate. If you find an application that doesn't accept the certificate, please update the script to add support for it.
1. The script adds an environment variable `REQUESTS_CA_BUNDLE` to your environment, which is used by Python when making HTTPS requests.
1. The certificate trust is tested with the following applications, currently on Ubuntu only: Google Chrome, curl, Python