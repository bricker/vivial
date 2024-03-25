## Setup

Start by running `./bin/setup` in your current shell.

### Environment Variables

The setup script will create a gitignored `.env` file in EAVE_HOME, with a list of environment variables that the apps use. Before running an app, you should fill these out. Some environment variables have defaults and can be left undefined (see the corresponding config.* file for more info).

The format of the `.env` file isn't formally specified anywhere, but it should be parseable by [python-dotenv](https://github.com/theskumar/python-dotenv#file-format).

## IDE

For the fastest setup, built-in configuration, debug scripts, and more, it is recommended to use VSCode for development in this repository.

To get started, open EAVE_HOME (this directory) in VSCode.

## Running apps

This VSCode workspace defines launch configurations for most apps, which you can use from the "Run and Debug" pane in VSCode. Alternatively, most apps have a `bin/start-dev` script if you prefer to start the server from the terminal, but VSCode debug features may not be available.

### Running the HTTP proxy

This repository comes with mitmproxy, configured as a pseudo-reverse proxy that listens on localhost:8080 and routes traffic based on the hostname and path, similar to our production load balancer. To run the proxy:

```bash
$EAVE_HOME/bin/http-proxy
```

Now, start whichever services you need, and access them using the respective domain under `*.eave.run:8080`. For example:

- `http://api.eave.run:8080` -> Core API
- `http://www.eave.run:8080` -> Website
- `http://apps.eave.run:8080/github` -> GitHub app
- `http://metabase.eave.run:8080` -> Metabase

This proxy serves three primary functions:

1. All local services can be accessed through the same port (8080), eliminating the need to remember which service is mapped to which port.
1. HTTPS URLs are supported by mitmproxy.
1. mitmproxy provides capabilities for viewing, modifying, and replaying the request/response cycle, to help debug HTTP requests.

Note: Although the proxy is running and forwarding requests, you still need to run the apps (through the VSCode Launch configurations, for example) to be able to access them through the proxy.

#### DNS

The `eave.run` domain is a real, publicly registered domain, owned by Eave. However, its only DNS record is a CNAME mapping `*.eave.run` to `localhost`. You can therefore use `eave.run` the same way you'd use `localhost` for local development.
A real TLD is necessary for Google OAuth to work in development, because Google doesn't allow `localhost` as an authorized domain.
There are a few advantages to using a real domain instead of `/etc/hosts`:

1. Works out of the box.
1. Arbitrary, dynamic, wildcard subdomains are supported. `/etc/hosts` does not support wildcards, so each subdomain must be explicitly mapped.
1. Honored by all applications. Applications sometimes don't read `/etc/hosts` (eg `host` and `dig`).

##### If it's not working

- Check that you're using a _subdomain_ (eg `www.eave.run:8080`). The apex domain (`eave.run`) doesn't have a DNS record.
- Check that you're specifying a port. Our default configuration uses `8080`.
- **Occasionally this DNS setup won't work**, especially on public wifi networks. The easiest workaround is to just manually update `/etc/hosts` to map each `eave.run` subdomain to `127.0.0.1`. Example:

```
# /etc/hosts

127.0.0.1   www.eave.run
127.0.0.1   api.eave.run
127.0.0.1   apps.eave.run
127.0.0.1   metabase.eave.run
```

Alternatively, you can just use `*eave.localhost`, eg `http://www.eave.localhost:8080`. For this to work, you'll need to update your `.env` file to use `localhost` for `EAVE_WWW_BASE_PUBLIC`, etc. Note that Google Oauth won't work if you do this.

Finally, if all else fails, you can access the services directly using the service's port, eg `localhost:5100` for the core API. This bypasses the DNS and HTTP proxy completely. You'll need to update your `.env` configuration to support this, and Google OAuth won't work with this setup.

#### SSL

You can access your local apps over HTTPS, although it is not necessary in most cases. Testing OAuth is one example of when HTTPS may be necessary. HTTPS requests are supported out of the box, so you can visit `https://api.eave.run:8080` (for example) and the request will be processed. However, you are likely to receive a TLS warning or error from whichever application you're using (eg curl or Google Chrome), because the certificate used is self-signed and not trusted by any application by default.

This repository provides a self-signed certificate, which mitmproxy is configured to use for HTTPS requests. Additionally, this repository provides a script to install (trust) the certificate on your system, which is technically optional, but recommended. If you do not install and trust the certificate, the proxy can still serve HTTPS requests, but you'll have to always bypass the certificate security warnings (eg via `curl --insecure` or Chrome's "Proceed to ..." button).

To install and trust the self-signed certificate on your system, run the provided script at `${EAVE_HOME}/develop/certs/bin/install-certs` (*Note: This is so far only tested on Ubuntu. Please fix any issues you encounter.*). If necessary, you can update your `.env` file to change the base URLs to "https://..." (eg `EAVE_WWW_BASE_PUBLIC=https://www.eave.run`).

Alternatively, if you can't or don't want to use the provided self-signed certificate, you can install mitmproxy's self-signed certificate instead. See the [mitmproxy documentation](https://docs.mitmproxy.org/stable/concepts-certificates/) for details. (*Note: The `bin/proxy` script is configured to use the Eave self-signed certificate; changes to that script may be necessary to support mitmproxy's certificate)*

You should now be able to connect to your local services normally over HTTPS (without any connection warnings/errors).

A few things to be aware of:

1. The `install-certs` script adds the self-signed certificate to as many certificate stores on your system as possible, with the goal being that any application you're using will accept the certificate. If you find an application that doesn't accept the certificate, please update the script to add support for it.
1. The script adds an environment variable `REQUESTS_CA_BUNDLE` to your environment, which is used by Python when making HTTPS requests.
1. The certificate trust is tested with the following applications, currently on Ubuntu only: Google Chrome, curl, Python