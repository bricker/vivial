## apps/core/eave/core/__init__.py

```
The code is part of a Python module that imports two modules from the 'eave.stdlib' package: 'eave_origins' and 'eave_signing'. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The code then defines two constants: 'EAVE_API_SIGNING_KEY' and 'EAVE_API_JWT_ISSUER'. The 'EAVE_API_SIGNING_KEY' is obtained by calling the 'get_key' function from the 'eave_signing' module with the value of 'eave_api' from the 'EaveOrigin' enumeration in the 'eave_origins' module. The 'EAVE_API_JWT_ISSUER' is set to the value of 'eave_api' from the same enumeration. 

This suggests that all authentication tokens coming into the core API should be both signed and issued by the API itself.
```

```json
[]
```

## apps/core/eave/core/app.py

```
This Python script is part of a web application server built using the Starlette framework, which is an asynchronous web framework for Python. The script defines the routes and middleware for the application, and sets up the Starlette application instance.

The script starts by importing various modules and functions, including middleware for authentication, team lookup, and signature verification, as well as operations for handling accounts, documents, integrations with Atlassian, Github, and Slack, subscriptions, and teams. It also imports modules for handling requests and exceptions.

The `make_route` function is defined to set up a route with specific middleware based on the configuration provided. The function checks if team ID, authentication, signature, and origin are required for the route, and adds the corresponding middleware accordingly.

A list of routes is then defined for various endpoints of the application. Each route is created using the `make_route` function with a specific configuration and endpoint. The routes include endpoints for handling status, documents, subscriptions, integrations, teams, authenticated accounts, and OAuth authorization and callbacks for Google, Slack, Atlassian, and Github.

The `graceful_shutdown` function is defined to close the database engine and cache client when the application is shutting down.

Finally, the Starlette application instance is created with the defined middleware, routes, exception handlers, and shutdown function. This instance is stored in the `app` variable.
```

```json
[
  "atlassian",
  "github",
  "slack",
  "google"
]
```

## apps/core/eave/core/public/http_endpoint.py

```
This Python code defines an HTTP endpoint class with improved typing, based on the Starlette framework. The class, `HTTPEndpoint`, is initialized with a scope, receive, and send parameters. It supports HTTP methods like GET, HEAD, POST, PUT, PATCH, DELETE, and OPTIONS. 

The `dispatch` method is used to handle incoming requests. It creates a request object and determines the appropriate handler based on the request method. If the handler is asynchronous, it awaits the handler's response; otherwise, it runs the handler in a separate thread pool. 

If a method is not allowed, the `method_not_allowed` function is called. This function either raises an HTTPException (if running inside a Starlette application) or returns a plain text response indicating that the method is not allowed.

This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It is a part of the application's core functionality and is likely imported and used by the main application file.
```

```json
[]
```

## apps/core/eave/core/public/exception_handlers.py

```
The code in the file `exception_handlers.py` does not start an application server. Instead, it defines a set of exception handlers for different types of HTTP errors that can occur in a web application. These handlers are designed to be used with the Starlette ASGI framework, which is a lightweight and high-performance framework for building asynchronous web applications in Python.

Each handler function takes a Starlette `Request` object and an `Exception` object as input, and returns a Starlette `Response` object. The response is a JSON object that includes the HTTP status code, a descriptive error message, and some context information about the request.

The `exception_handlers` dictionary at the end of the file maps each type of exception to its corresponding handler function. This dictionary can be used by the Starlette framework to automatically dispatch exceptions to the appropriate handler.

The specific types of HTTP errors handled by this code include:

- Internal Server Error (500)
- Not Found (404)
- Bad Request (400)
- Unauthorized (401)
- Validation Error (422)

For each type of error, the corresponding handler function logs the error, creates an `ErrorResponse` model with the appropriate status code and message, and returns a JSON response with this information. In the case of the Unauthorized error, the handler also deletes any authentication cookies from the response. For the Validation Error, if the exception is a `pydantic.ValidationError`, the handler adds the validation errors to the context information in the response.
```

```json
[]
```

## apps/core/eave/core/public/__init__.py

```
The code in this file is importing modules named 'exception_handlers' and 'http_endpoint' from the current directory. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's just a part of the application that handles exceptions and HTTP endpoints.
```

```json
[]
```

## apps/core/eave/core/public/requests/atlassian_integration.py

```
The code in the file `atlassian_integration.py` does not start an application server. Instead, it defines a class `AtlassianIntegration` that inherits from `HTTPEndpoint`. This class has a single asynchronous method `post` which handles POST requests.

The `post` method first extracts the JSON body from the incoming request and parses it into an instance of `GetAtlassianInstallation.RequestBody`. It then starts a database session and attempts to retrieve an Atlassian installation record and a team record from the database using the ORM (Object-Relational Mapping) classes `AtlassianInstallationOrm` and `TeamOrm`.

If the Atlassian installation record is not found, it raises a `NotFoundError`. If both records are found, it returns a JSON response containing the API models of both records. The response is created using the `GetAtlassianInstallation.ResponseBody` class and the `eave_api_util.json_response` function.
```

```json
[]
```

## apps/core/eave/core/public/requests/team.py

```
The provided Python code does not start an application server. It is a part of a larger application, possibly a web application, and defines two HTTP endpoints for handling specific types of requests related to team management in a system. The code uses the Starlette framework for handling HTTP requests and responses.

The first class, `GetTeamEndpoint`, defines a POST endpoint that retrieves information about a team and its integrations from the database. It uses the `TeamOrm` class to interact with the database and retrieve the required data. The response is then formatted as JSON using the `json_response` function.

The second class, `UpsertConfluenceDestinationAuthedEndpoint`, also defines a POST endpoint. This endpoint is used to either insert (if it doesn't exist) or update (if it does exist) a Confluence destination for a team. It uses the `TeamOrm`, `ConnectInstallationOrm`, and `ConfluenceDestinationOrm` classes to interact with the database. The response, which includes information about the team and the Confluence destination, is also formatted as JSON.

Both endpoints use asynchronous functions, indicating that they are designed to handle multiple requests concurrently without blocking.
```

```json
[
  "confluence"
]
```

## apps/core/eave/core/public/requests/authed_account.py

```
The code in this file does not start an application server. Instead, it defines two classes `GetAuthedAccount` and `GetAuthedAccountTeamIntegrations` that handle HTTP POST requests in an asynchronous manner. Both classes are subclasses of `HTTPEndpoint` from the `eave.core.public.http_endpoint` module.

The `GetAuthedAccount` class has a `post` method that loads the request state, retrieves the team and account information from the database, and returns a JSON response with the authenticated account and team details.

The `GetAuthedAccountTeamIntegrations` class also has a `post` method that loads the request state, retrieves the team and account information from the database, as well as the team's integrations and destination. It then returns a JSON response with the authenticated account, team details, integrations, and destination.

The code uses the Starlette library for handling requests and responses, and interacts with a database using an asynchronous session from `eave.core.internal.database.async_session`.
```

```json
[]
```

## apps/core/eave/core/public/requests/github_integration.py

```
The code in the file `github_integration.py` does not start an application server. Instead, it defines a class `GithubIntegration` that extends `HTTPEndpoint`. This class has a single asynchronous method `post` which takes a request as an argument and returns a response. 

The `post` method first extracts the JSON body from the request and parses it into a `GetGithubInstallation.RequestBody` object. It then starts a database session and attempts to retrieve a `GithubInstallationOrm` object based on the `github_install_id` from the parsed body. If no such installation is found, it raises a `NotFoundError`. 

If an installation is found, it retrieves the associated team by its `team_id`. Finally, it returns a JSON response containing the installation and team information. 

The code uses several modules from the `eave` package, including database and ORM (Object-Relational Mapping) modules for interacting with the database, an HTTP endpoint module for defining the endpoint, and an API utility module for creating the JSON response. It also uses the `starlette.requests` and `starlette.responses` modules for handling HTTP requests and responses.
```

```json
[]
```

## apps/core/eave/core/public/requests/subscriptions.py

```
The code in the file `subscriptions.py` does not start an application server. Instead, it defines three classes: `GetSubscription`, `CreateSubscription`, and `DeleteSubscription`. Each of these classes is a subclass of `HTTPEndpoint`, which suggests that they are used to handle HTTP requests in a web application.

The `GetSubscription` class defines a method for handling POST requests. This method retrieves a subscription from a database, and returns it in the response. If the subscription does not exist, it returns a response with no subscription.

The `CreateSubscription` class also defines a method for handling POST requests. This method creates a new subscription in the database, or updates an existing one. The response includes the subscription and its status code.

The `DeleteSubscription` class defines a method for handling POST requests as well. This method deletes a subscription from the database, and returns a response with a status code of OK.

Each of these classes uses the `EaveRequestState` to load the current state of the request, and uses the `eave.core.internal.database.async_session` to interact with the database. The classes also use various other modules and classes from the `eave` package, as well as the `Request` and `Response` classes from the `starlette.requests` and `starlette.responses` packages, respectively.
```

```json
[]
```

## apps/core/eave/core/public/requests/status.py

```
The code defines several HTTP endpoints for a web application using the Starlette framework for Python. It does not start an application server itself, but it is likely part of a larger application that does.

The `StatusRequest` class defines an endpoint that responds to several HTTP methods (POST, DELETE, HEAD, OPTIONS, GET) by executing a SQL query "SELECT 1" and returning a JSON response with a status code and message. If the SQL query returns no rows, the status code is set to "SERVICE UNAVAILABLE" and the status message is set to "UNHEALTHY".

The `WarmupRequest` class defines an endpoint that responds to GET requests by preloading some configuration data and returning a response with status code "OK".

The `StartRequest` and `StopRequest` classes each define an endpoint that responds to GET requests by simply returning a response with status code "OK". These could potentially be used to start or stop some process in the application, but the current implementation does not do anything beyond returning a response.
```

```json
[]
```

## apps/core/eave/core/public/requests/slack_integration.py

```
The code is from a Python file that defines a class `SlackIntegration` which extends the `HTTPEndpoint` class. This class has a single asynchronous method `post` which handles POST requests. 

The `post` method first parses the request body into a `GetSlackInstallation.RequestBody` object. Then it starts a database session and tries to find a `SlackInstallationOrm` object with the given `slack_team_id`. If it can't find such an object, it raises a `NotFoundError`. 

If it does find a `SlackInstallationOrm`, it ensures that the access tokens are up to date by calling the `refresh_token_or_exception` method. It then retrieves the associated `TeamOrm` object.

Finally, it creates a `GetSlackInstallation.ResponseBody` object with the `SlackInstallationOrm` and `TeamOrm` objects, and returns this as a JSON response.

This file does not start an application server. It is likely part of a larger application that uses the Starlette ASGI framework.
```

```json
[]
```

## apps/core/eave/core/public/requests/documents.py

```
This Python code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it defines three classes: `UpsertDocument`, `SearchDocuments`, and `DeleteDocument`. These classes are likely part of a larger application, possibly a web server or API, that handles HTTP requests related to documents.

1. `UpsertDocument`: This class handles HTTP POST requests to upsert (update or insert) a document. It first checks if the document already exists. If it does, it updates the document; otherwise, it creates a new document. It also logs the event of creating or updating a document.

2. `SearchDocuments`: This class handles HTTP POST requests to search for documents. It uses the provided query to search for documents and logs the event of searching for documents.

3. `DeleteDocument`: This class handles HTTP POST requests to delete a document. It deletes the specified document and all its associated subscriptions, then logs the event of deleting a document.

All three classes inherit from `eave.core.public.http_endpoint.HTTPEndpoint`, which suggests that they are part of an HTTP API. They all use Starlette's `Request` and `Response` classes to handle HTTP requests and responses, and they interact with a database using an asynchronous session from `eave.core.internal.database.async_session`.
```

```json
[]
```

## apps/core/eave/core/public/requests/connect_integration.py

```
The code in this file does not start an application server. Instead, it defines two classes, `QueryConnectIntegrationEndpoint` and `RegisterConnectIntegrationEndpoint`, which are used to handle HTTP requests related to querying and registering Connect integrations respectively.

The `QueryConnectIntegrationEndpoint` class has a `post` method that handles POST requests. It retrieves the request body, parses it into a `QueryConnectIntegrationRequest.RequestBody` object, and then queries the database for a Connect installation that matches the provided product, client key, and team ID. If no such installation is found, it logs a warning and returns a 404 response. If an installation is found, it retrieves the associated team (if any) and returns a JSON response containing the team and installation data.

The `RegisterConnectIntegrationEndpoint` class also has a `post` method that handles POST requests. It retrieves the request body, parses it into a `RegisterConnectIntegrationRequest.RequestBody` object, and then queries the database for a Connect installation that matches the provided product and client key. If no such installation is found, it creates a new one with the provided data. If an installation is found, it updates it with the provided data. In both cases, it logs an analytics event and returns a JSON response containing the team (if any) and installation data.
```

```json
[]
```

## apps/core/eave/core/public/requests/noop.py

```
This Python code defines a class called `NoopRequest` that inherits from `HTTPEndpoint`. This class has a single asynchronous method `get` which takes a `Request` object as an argument and returns a `Response` object. The `get` method does not perform any operations on the request and simply returns an empty response. 

The code does not start an application server. It uses Starlette, which is a lightweight ASGI framework/toolkit, ideal for building high performance asyncio services. However, this specific file only defines a class and does not run a server.
```

```json
[]
```

## apps/core/eave/core/public/requests/oauth/base.py

```
The code is written in Python and it does not start an application server. It is a part of a larger application, likely a web application given the use of Request and Response objects from the Starlette library, which is an asynchronous web framework for Python.

The code defines a class `BaseOAuthCallback` that inherits from `HTTPEndpoint`. This class seems to be a base class for handling OAuth callbacks. It has several attributes including `request`, `response`, `state`, `code`, `error`, `error_description`, `auth_provider`, and `eave_state`.

The class has two methods: `get` and `_check_valid_callback`. 

The `get` method is an asynchronous method that takes a request as an argument and returns a response. It extracts various parameters from the request, verifies the OAuth state using a shared function, loads the request state, and assigns various attributes to the instance of the class before returning the response.

The `_check_valid_callback` method checks if the callback is valid. If there's an error or if the code is missing, it logs a warning message, cancels the flow using a shared function, and returns False. If there's no error and the code is present, it returns True. 

The code also imports several modules and classes from different packages, including typing for type annotations, starlette for handling requests and responses, eave.stdlib for logging and request state handling, and a local http_endpoint module.
```

```json
[]
```

## apps/core/eave/core/public/requests/oauth/slack_oauth.py

```
The code in the file slack_oauth.py is part of an application that uses the Starlette framework for Python. It does not start an application server itself.

The file contains code for handling OAuth authorization and callbacks with Slack. It defines two classes: SlackOAuthAuthorize and SlackOAuthCallback. 

SlackOAuthAuthorize generates a state token for CSRF protection, creates an authorization URL, sets tracking cookies, and saves the state cookie. 

SlackOAuthCallback handles the callback from Slack after the user has authorized the application. It checks if the callback is valid, retrieves access tokens and user information from Slack, creates or updates a user account in the application's database, and redirects the user to a specific location in Slack. 

The file also contains code for updating or creating a Slack installation in the application's database, logging events, and sending a welcome message to the user in Slack after installation.
```

```json
[
  "slack"
]
```

## apps/core/eave/core/public/requests/oauth/github_oauth.py

```
The code in the file `github_oauth.py` does not start an application server. It is a part of a larger application, likely a web application, and is responsible for handling OAuth authentication with GitHub.

The file contains two classes: `GithubOAuthAuthorize` and `GithubOAuthCallback`, both of which inherit from `HTTPEndpoint`. These classes are likely used as endpoints in a web application to handle the OAuth flow with GitHub.

The `GithubOAuthAuthorize` class has a `get` method that generates an authorization URL for GitHub OAuth, sets tracking cookies, and saves the state cookie. It then returns a redirect response to the authorization URL.

The `GithubOAuthCallback` class also has a `get` method that handles the callback from GitHub after the user has authorized the application. It verifies the state, checks if the user is already logged in, and either updates or creates a new GitHub installation associated with the user's account. It also logs various events for analytics purposes.

The code uses various libraries and modules such as `json`, `urllib.parse`, `oauthlib.common`, `starlette.requests`, `starlette.responses`, and several modules from the `eave` package.
```

```json
[
  "github"
]
```

## apps/core/eave/core/public/requests/oauth/shared.py

```
The provided Python code does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

This code is part of a larger application, specifically a module for handling OAuth related operations. OAuth is an open standard for access delegation, commonly used as a way for Internet users to grant websites or applications access to their information on other websites but without giving them the passwords.

The code includes several functions that handle various aspects of the OAuth process:

- `verify_oauth_state_or_exception`: This function verifies the state of the OAuth request and raises an exception if the state is invalid.
- `set_redirect`: This function sets the location header of the response and changes the status code to indicate a temporary redirect.
- `set_error_code`: This function updates the query parameters of the location header to include an error code.
- `cancel_flow`: This function redirects the response to a base URL.
- `check_beta_whitelisted`: This function checks if an email is whitelisted for beta testing.
- `get_logged_in_eave_account`: This function checks if a user is logged in and retrieves their account information if they are.
- `get_existing_eave_account`: This function checks for an existing account with a given provider and ID, and updates access and refresh tokens in the database.
- `create_new_account_and_team`: This function creates a new account and team in the database, logs an event for account creation, and sends a notification to a Slack channel.
- `get_or_create_eave_account`: This function retrieves an existing account or creates a new one if none exists. It also sets authentication cookies in the response headers and redirects the response to a default location.

The code uses several libraries and modules including http, re (regular expressions), typing, urllib.parse, and several modules from the eave and starlette packages.
```

```json
[]
```

## apps/core/eave/core/public/requests/oauth/__init__.py

```
The code is written in Python and it does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The code is importing the `enum` module, which allows for the creation of enumerations, which are basically a way to organize various types of data in Python. 

It then defines a constant string `EAVE_ERROR_CODE_QP` with the value "ev_error_code".

Afterwards, it defines an enumeration class `EaveOnboardingErrorCode` that inherits from `enum.StrEnum`. This enumeration has one member: `already_linked` with a string value of "already_linked". This could be used to represent specific error codes in a more readable and organized manner in the application.
```

```json
[]
```

## apps/core/eave/core/public/requests/oauth/atlassian_oauth.py

```
The code in the file `atlassian_oauth.py` is part of a larger application, and does not start an application server itself. It is responsible for handling OAuth authorization and callbacks with Atlassian services such as Jira and Confluence.

The code imports necessary modules and defines constants. It then defines two classes: `AtlassianOAuthAuthorize` and `AtlassianOAuthCallback`. 

`AtlassianOAuthAuthorize` has a `get` method that initiates the OAuth flow by creating an OAuth session, getting the authorization URL, setting tracking cookies, saving the state cookie, and returning a redirect response to the authorization URL.

`AtlassianOAuthCallback` extends from a base OAuth callback class and also has a `get` method. This method handles the callback from Atlassian after the user has authorized the application. It checks the validity of the callback, fetches the OAuth token, gets user information, links the Connect installation, and updates or creates an Atlassian installation record in the database.

The code also includes several helper methods to handle specific tasks such as linking the Connect installation, getting matching Connect installations, updating the Eave team document platform, setting the default Confluence space if applicable, and updating or creating an Atlassian installation.

The code uses SQLAlchemy for database operations and Starlette for handling HTTP requests and responses. It also uses logging and analytics functions for tracking events and errors.
```

```json
[
  "atlassian",
  "jira",
  "confluence"
]
```

## apps/core/eave/core/public/requests/oauth/google_oauth.py

```
The code in the file `google_oauth.py` is not starting an application server. Instead, it is defining two classes, `GoogleOAuthAuthorize` and `GoogleOAuthCallback`, which are used to handle Google OAuth authorization and callback respectively.

The `GoogleOAuthAuthorize` class has a `get` method which initiates the OAuth flow by redirecting the user to Google's authorization URL. It also sets tracking cookies and saves the state cookie.

The `GoogleOAuthCallback` class also has a `get` method which handles the callback from Google after user authorization. It checks the validity of the callback, fetches the OAuth token, decodes the ID token, and then either gets an existing Eave account or creates a new one based on the information obtained from Google.

The code uses several libraries including `starlette` for handling HTTP requests and responses, `google.oauth2` for handling Google OAuth2 credentials, and `eave.stdlib` and `eave.core.internal.oauth` for handling various aspects of the Eave application's functionality.
```

```json
[
  "google_oauth"
]
```

## apps/core/eave/core/public/requests/oauth

```
sentinel
```

## apps/core/eave/core/public/requests

```
sentinel
```

## apps/core/eave/core/public/middlewares/authentication.py

```
The code is a Python script that defines an ASGI (Asynchronous Server Gateway Interface) middleware for authentication in an application. The middleware, `AuthASGIMiddleware`, is a subclass of `EaveASGIMiddleware`. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The middleware intercepts HTTP requests and performs authentication checks. If the development bypass is allowed, it performs a development bypass authentication. Otherwise, it verifies the authentication by checking for the presence of an account ID header and a bearer token in the request. 

If these checks pass, it retrieves the account associated with the account ID and access token from the database. It then verifies the OAuth token associated with the account. If the token has expired, it refreshes the token and verifies it again. 

Finally, it stores the account ID and team ID in the request context for further processing. If any of these checks fail, it raises an exception and aborts the request.
```

```json
[]
```

## apps/core/eave/core/public/middlewares/team_lookup.py

```
The code is a Python script that defines a middleware for an ASGI (Asynchronous Server Gateway Interface) application. The middleware is named `TeamLookupASGIMiddleware` and it's part of the Eave framework. It does not start an application server.

The middleware's main function is to look up a team ID from the HTTP request headers and validate it. If the team ID is already set in the request context (possibly by another middleware), it checks if the team ID in the context matches the one in the headers. If they don't match, it raises a `BadRequestError`.

If the team ID is not set in the context, it checks if it's present in the headers. If it's not present, it raises a `MissingRequiredHeaderError`. If it is present, it validates that the team ID is a valid UUID and then queries the database to fetch the team with that ID. If the team exists, it sets the team ID in the request context.

The middleware uses the Eave framework's standard library for handling exceptions, API utilities, and HTTP headers. It also uses the ASGI typing module for type hinting.
```

```json
[]
```

## apps/core/eave/core/public/middlewares/development_bypass.py

```
The code is a middleware for a Python application that bypasses authentication in a development environment. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The middleware function `development_bypass_auth` accepts an HTTP scope object and does not return any value. It loads the current request state and logs a warning message indicating that authentication verification is being bypassed. 

It then retrieves the account ID from the authorization header of the HTTP request. If no account ID is found, it raises an exception.

If an account ID is found, it starts a database session and attempts to retrieve an account with the given ID from the database. If the account is found, its ID is stored in the context of the current request state. The database session is managed asynchronously, meaning that other tasks can run while waiting for the database operations to complete. 

The code uses several modules from the `eave` package, including modules for internal core functions, standard library functions, API utilities, and logging. It also uses the `uuid` module from Python's standard library to handle UUIDs (Universally Unique Identifiers), and the `asgiref.typing` module for type annotations.
```

```json
[]
```

## apps/core/eave/core/public/middlewares

```
sentinel
```

## apps/core/eave/core/public

```
sentinel
```

## apps/core/eave/core/internal/document_client.py

```
The code defines a Python module for interacting with documents in a system. It does not start an application server.

The module contains a data class `DocumentMetadata` and an abstract base class `DocumentClient`. 

`DocumentMetadata` is a lightweight version of `DocumentReferenceOrm` without the ORM (Object-Relational Mapping) related attributes. It has two attributes: `id` and `url`.

`DocumentClient` is an abstract base class that defines the protocol for document operations. It declares four methods: `create_document`, `update_document`, `search_documents`, and `delete_document`. These methods are asynchronous, meaning they are designed to handle IO-bound operations efficiently.

The methods in `DocumentClient` use the `DocumentInput` and `DocumentSearchResult` data classes from the `eave.stdlib.core_api.models.documents` module, and optionally a `LogContext` for logging purposes. The methods return either a `DocumentMetadata` instance, a list of `DocumentSearchResult` instances, or nothing (`None`).
```

```json
[]
```

## apps/core/eave/core/internal/__init__.py

```
The code is importing modules from a Python package. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. The modules being imported are 'database', 'app_config' from 'config', 'orm', and 'oauth'. These could be used for database operations, application configuration, object-relational mapping, and OAuth authentication respectively.
```

```json
[]
```

## apps/core/eave/core/internal/database.py

```
The code in this file is not starting an application server. Instead, it is setting up a connection to a PostgreSQL database using SQLAlchemy, an SQL toolkit and Object-Relational Mapping (ORM) system for Python. 

The database connection details such as the host, username, password, and database name are fetched from the application configuration. The database driver used is "postgresql+asyncpg", which indicates that it uses the asyncpg library for asynchronous IO with PostgreSQL.

An asynchronous engine is created with the database URI, and an asynchronous sessionmaker is also created with the engine. This sessionmaker can be used to create sessions that automatically commit and close when used in a context manager. 

The code also includes an example of how to use the async session to add an object to the database.
```

```json
[]
```

## apps/core/eave/core/internal/config.py

```
The code in the file `apps/core/eave/core/internal/config.py` does not start an application server. Instead, it defines a configuration class `AppConfig` for an application, which is a subclass of `EaveConfig` from the `eave.stdlib.config` module.

The `AppConfig` class has several properties and cached properties that fetch configuration values from environment variables or secrets, depending on whether the application is running in development mode or not. These properties include database host, user, password, and name, Google OAuth client credentials and client ID, and a list of pre-whitelisted emails for beta testing.

The database password and the list of pre-whitelisted emails have error handling to log exceptions and return default values if fetching their values fails.

At the end of the file, an instance of `AppConfig` is created and assigned to `app_config`. This instance can be imported by other modules to access the application's configuration.
```

```json
[]
```

## apps/core/eave/core/internal/oauth/slack.py

```
The code in the file `slack.py` is used for handling OAuth authentication with Slack. It does not start an application server.

The file imports necessary modules and sets up an `AuthorizeUrlGenerator` with the required scopes for accessing various Slack features. It also sets up a redirect URI for OAuth callbacks.

The file defines several classes:

- `SlackIdentity`: This class represents a Slack user's identity. It includes various properties like user ID, team ID, email, name, picture, locale, and more. The class's constructor takes a dictionary and assigns its values to the class's properties.

- `SlackTeam`, `SlackAuthorizedUser`, and `SlackOAuthResponse`: These are TypedDict classes that define the structure of a Slack team, an authorized user, and an OAuth response respectively.

The file also defines several functions:

- `get_authenticated_client`: This function takes an access token and returns an authenticated Slack client.

- `get_userinfo_or_exception`: This asynchronous function takes a Slack client and returns a `SlackIdentity` object. If the response from the Slack API is not a dictionary, it raises a TypeError.

- `get_access_token_or_exception` and `refresh_access_token_or_exception`: These asynchronous functions are used to get and refresh an access token respectively. They make a request to the Slack API and return a `SlackOAuthResponse` object.
```

```json
[
  "slack"
]
```

## apps/core/eave/core/internal/oauth/google.py

```
The code in the file `google.py` is not starting an application server. Instead, it is a module that provides functionality related to Google's OAuth2 authentication. 

The module imports several libraries related to Google's OAuth2 and API client, as well as some internal libraries from the `eave` application. It defines several classes and functions that are used to interact with Google's OAuth2 service.

The classes defined in the module include `GoogleIdToken`, `GoogleOAuthClientConfig`, and `GoogleOAuthV2GetResponse`. These classes are used to represent data returned from Google's OAuth2 service.

The functions defined in the module include `get_userinfo`, `get_oauth_credentials`, `build_flow`, `get_oauth_flow_info`, and `decode_id_token`. These functions are used to interact with Google's OAuth2 service, including getting user information, building an OAuth2 flow, getting OAuth2 flow information, and decoding an ID token.

The module also defines some constants related to Google's OAuth2 service, such as the OAuth scopes and the redirect URI.
```

```json
[
  "google_oauth2"
]
```

## apps/core/eave/core/internal/oauth/__init__.py

```
The code in this file is importing different modules from the same directory. These modules are slack, atlassian, google, models, and state_cookies. This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's just importing modules for use in other parts of the application.
```

```json
[]
```

## apps/core/eave/core/internal/oauth/state_cookies.py

```
The code in the file `state_cookies.py` is a part of an application that uses Starlette, a lightweight ASGI framework/toolkit, which is ideal for building high performance asyncio services. However, this file does not start an application server.

The code defines functions for handling OAuth state cookies. These cookies are used in the OAuth authentication process to maintain the state between the client and the server. The functions allow for the creation, retrieval, and deletion of these cookies.

The `_build_cookie_name` function constructs a cookie name based on the authentication provider. The `_build_cookie_params` function builds a dictionary of parameters for the cookie, including domain, path, security settings, and more.

The `save_state_cookie` function sets a cookie on the response with a specific name and value, and additional parameters. The `get_state_cookie` function retrieves a cookie from the request. If the cookie does not exist, it raises an `UnexpectedMissingValue` exception. The `delete_state_cookie` function deletes a specific cookie from the response.

There is a note in the code indicating that the `save_state_cookie` function assumes that the value of the provider matches the path for `/oauth/{provider}/callback`, which may not always be true.
```

```json
[]
```

## apps/core/eave/core/internal/oauth/atlassian.py

```
The code in the file `atlassian.py` is part of a Python application that interacts with the Atlassian API using OAuth2 for authentication. It does not start an application server like Express, Flask, Django, Gin, or Rack.

The code defines several classes and functions to handle OAuth2 sessions with Atlassian. The `AtlassianOAuthSession` class extends the `OAuth2Session` class from the `requests_oauthlib` library and is used to manage OAuth2 sessions with Atlassian. It includes methods for getting the authorization URL, fetching tokens, making requests, getting user information, and getting available resources.

The `AtlassianOAuthTokenResponse` data class is used to store the response from Atlassian when requesting an OAuth token.

The `ATLASSIAN_OAUTH_SCOPES` list defines the scopes for which the application requests access when authenticating with Atlassian.

The `get_available_resources` method uses caching to avoid unnecessary API calls. The `get_userinfo` method retrieves information about the current user. The `atlassian_cloud_id` and `api_base_url` properties are used to construct URLs for API requests. The `get_token` method is used mainly for testing purposes.
```

```json
[
  "atlassian"
]
```

## apps/core/eave/core/internal/oauth/models.py

```
The code does not start an application server. It is a Python script that defines two data models related to OAuth (Open Authorization) flow. 

1. `OAuthFlowInfo`: This is a data class that holds two string variables - `authorization_url` and `state`. 

2. `OAuthCallbackRequestBody`: This is a Pydantic model that has three optional string variables - `state`, `code`, and `error`. Pydantic models are mainly used for data validation and settings management using Python type annotations.

Both of these models are likely used for handling OAuth authentication flow in the application.
```

```json
[]
```

## apps/core/eave/core/internal/oauth

```
sentinel
```

## apps/core/eave/core/internal/orm/slack_installation.py

```
This Python code defines a class `SlackInstallationOrm` that represents a table in a database using SQLAlchemy, an SQL toolkit and Object-Relational Mapping (ORM) system for Python. The table is named "slack_sources" and contains various fields related to Slack installations, such as team ID, bot token, bot refresh token, and timestamps for creation and updates.

The class provides methods for creating a new row in the table (`create`), refreshing the bot token (`refresh_token_or_exception`), and querying the table (`_build_select`, `one_or_none`, `one_or_exception`). It also provides properties to return the data as API models (`api_model`, `api_model_peek`).

The `refresh_token_or_exception` method is notable because it checks if the bot token is still valid, and if not, it attempts to refresh the token. If there's no refresh token or if the refresh request fails, it raises a `MissingOAuthCredentialsError`.

This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's a module that defines a database model and related operations.
```

```json
[]
```

## apps/core/eave/core/internal/orm/connect_installation.py

```
The provided Python code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it defines a SQLAlchemy ORM (Object-Relational Mapping) class `ConnectInstallationOrm` for interacting with a database table named `connect_installations`. 

The `ConnectInstallationOrm` class has various attributes that map to the columns of the `connect_installations` table. These include `team_id`, `id`, `product`, `client_key`, `shared_secret`, `base_url`, `org_url`, `atlassian_actor_account_id`, `display_url`, `description`, `created`, and `updated`.

The class also includes several methods for querying the database. These methods include `_build_query` for constructing a SQL SELECT statement, `one_or_exception` for fetching a single record or raising an exception if no record is found, `one_or_none` for fetching a single record or returning None if no record is found, and `query` for executing the constructed query and returning the results.

In addition, the class includes methods for creating and updating records in the database. The `create` method inserts a new record into the database, while the `update` method modifies an existing record.

Finally, the class includes two property methods, `api_model` and `api_model_peek`, which convert an instance of the ORM class to instances of the `ConnectInstallation` and `ConnectInstallationPeek` classes respectively.
```

```json
[]
```

## apps/core/eave/core/internal/orm/base.py

```
The code is part of an internal ORM (Object-Relational Mapping) system for a Python application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The code imports necessary modules and defines a class `Base` that extends `DeclarativeBase` from SQLAlchemy, a Python SQL toolkit and ORM. The class `Base` is currently empty, but there are commented-out methods that suggest it might be used for querying the database.

The function `_load_all()` is defined to import all Python modules in the same directory as this file. This function is used to fully populate `Base.metadata` for scripts such as Alembic or tests.

The function `get_base_metadata()` is defined to return the metadata of the `Base` class. If the metadata is not loaded yet, it calls `_load_all()` to load all modules and sets `_base_metadata` to `Base.metadata`.

The `_base_metadata` variable is defined as a global variable and is initially set to `None`. It's used to store the metadata of the `Base` class after it's loaded.
```

```json
[]
```

## apps/core/eave/core/internal/orm/github_installation.py

```
The provided Python code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it defines a SQLAlchemy ORM (Object-Relational Mapping) model for a GitHub installation.

The `GithubInstallationOrm` class extends from a `Base` class and represents a table named "github_installations" in a database. This table has fields such as `team_id`, `id`, `github_install_id`, `created`, and `updated`.

The class also includes methods for creating a new GitHub installation (`create`), building a select query (`_build_select`), fetching a single installation or returning None if not found (`one_or_none`), and fetching a single installation or raising an exception if not found (`one_or_exception`). 

Additionally, it provides properties to get the API model representation of the GitHub installation (`api_model` and `api_model_peek`). These properties use the `from_orm` method from the `GithubInstallation` and `GithubInstallationPeek` classes to convert the ORM object into an API model object.
```

```json
[
  "github"
]
```

## apps/core/eave/core/internal/orm/team.py

```
The code in the file `team.py` is a part of an application's ORM (Object-Relational Mapping) layer. It does not start an application server. 

The file defines a class `TeamOrm` that represents the `teams` table in a database. The class includes fields such as `id`, `name`, `document_platform`, `created`, `updated`, and `beta_whitelisted`. It also includes methods for creating a new team, querying for a team by id, and getting a team's integrations and document client.

The `TeamOrm` class uses SQLAlchemy, an SQL toolkit and ORM for Python, to interact with the database. It also uses Python's typing module to provide type hints for better code readability and error checking.

The `get_document_client` method returns a document client based on the team's document platform. Currently, it only supports the Confluence platform and raises a `NotImplementedError` for other platforms.

The `get_integrations` method returns all the integrations associated with the team, including Slack, Github, Atlassian, Confluence, and Jira.

The `get_destination` method returns the destination of the team's documents based on the document platform. Currently, it only supports the Confluence platform and raises a `NotImplementedError` for other platforms.
```

```json
[
  "confluence",
  "slack",
  "github",
  "atlassian",
  "jira"
]
```

## apps/core/eave/core/internal/orm/account.py

```
The code in the file `account.py` does not start an application server. It is a part of an Object-Relational Mapping (ORM) system, specifically for the `Account` model. 

The `AccountOrm` class represents the `accounts` table in a database. It has fields like `team_id`, `id`, `visitor_id`, `opaque_utm_params`, `auth_provider`, `auth_id`, `access_token`, `refresh_token`, `email`, `created`, and `updated`. 

The class also includes methods for creating new account records (`create`), selecting account records based on certain parameters (`_build_select`, `one_or_exception`, `one_or_none`), verifying OAuth tokens (`verify_oauth_or_exception`), refreshing OAuth tokens (`refresh_oauth_token`), and getting the team associated with an account (`get_team`). 

The class also provides properties to get the API model (`api_model`) and analytics model (`analytics_model`) of an account. 

The code uses SQLAlchemy for database interactions and slack_sdk for Slack API interactions. It also uses the eave library for various functionalities like logging, exceptions, and OAuth.
```

```json
[
  "slack",
  "sqlalchemy"
]
```

## apps/core/eave/core/internal/orm/subscription.py

```
The code in the file `subscription.py` does not start an application server. Instead, it defines a SQLAlchemy ORM class `SubscriptionOrm` for interacting with a database table named "subscriptions". 

The `SubscriptionOrm` class includes several fields such as `team_id`, `id`, `source_platform`, `source_event`, `source_id`, `document_reference_id`, `created`, and `updated`. It also includes a unique index on the combination of `source_key`, `team_id`, `source_platform`, `source_event`, and `source_id`.

The class has several methods for interacting with the database. These include:

- `get_document_reference`: This method retrieves a document reference associated with a subscription.
- `create`: This method creates a new subscription.
- `_build_query`: This method builds a query based on provided parameters.
- `query`: This method executes a query and returns all matching subscriptions.
- `one_or_none`: This method executes a query and returns one matching subscription or None if no subscriptions match.
- `one_or_exception`: This method executes a query and returns one matching subscription or raises an exception if no subscriptions match.

The class also includes a nested class `QueryParams` which is a TypedDict used for type checking the parameters passed to the query methods.
```

```json
[]
```

## apps/core/eave/core/internal/orm/__init__.py

```
The code in this file is importing various classes from different modules within the same directory. These classes are likely related to Object-Relational Mapping (ORM), which is a technique that lets you interact with your database, like you would with SQL. In other words, it's converting data between incompatible type systems in databases and object-oriented programming languages. 

The classes being imported include AccountOrm, AtlassianInstallationOrm, DocumentReferenceOrm, GithubInstallationOrm, SlackInstallationOrm, ConnectInstallationOrm, SubscriptionOrm, TeamOrm, and ResourceMutexOrm. Each of these classes likely corresponds to a different table in the database.

This file does not start an application server. It is simply importing classes for use elsewhere in the application.
```

```json
[]
```

## apps/core/eave/core/internal/orm/util.py

```
The code in this file does not start an application server. Instead, it defines utility functions for creating foreign key and primary key constraints in a database using SQLAlchemy, a SQL toolkit and Object-Relational Mapping (ORM) system for Python. 

The `make_team_fk` function creates a foreign key constraint on the `team_id` column, referencing the `id` column in the `teams` table. The `ondelete="CASCADE"` argument means that when a referenced row in the `teams` table is deleted, all rows in the referencing table with a matching `team_id` will also be deleted.

The `make_team_composite_fk` function creates a composite foreign key constraint on the `team_id` and another column specified by the `fk_column` parameter. This constraint references the `team_id` and `id` columns in another table specified by the `foreign_table` parameter. The `ondelete="CASCADE"` argument has the same effect as in the previous function.

The `UUID_DEFAULT_EXPR` is a SQL expression that generates a random UUID.

The `make_team_composite_pk` function creates a composite primary key constraint on the `team_id` and `id` columns.
```

```json
[]
```

## apps/core/eave/core/internal/orm/atlassian_installation.py

```
The code in the file `atlassian_installation.py` defines an ORM (Object-Relational Mapping) class `AtlassianInstallationOrm` for interacting with the `atlassian_installations` table in a database. This class is built on top of the `Base` class, which is likely a base ORM class from SQLAlchemy.

The `AtlassianInstallationOrm` class has several fields that map to columns in the `atlassian_installations` table, such as `team_id`, `id`, `atlassian_site_name`, `atlassian_cloud_id`, `confluence_space_key`, `oauth_token_encoded`, `created`, and `updated`.

The class also defines several methods for querying and manipulating data in the `atlassian_installations` table. These methods include `_build_select`, `one_or_exception`, `one_or_none`, and `create`. The `_build_select` method builds a select query based on provided parameters. The `one_or_exception` and `one_or_none` methods execute a select query and return either one result or raise an exception, or return one result or None, respectively. The `create` method creates a new record in the table.

The class also includes methods for handling OAuth tokens, such as `oauth_token_decoded`, `build_oauth_session`, and `update_token`. These methods decode the OAuth token, build an OAuth session, and update the OAuth token, respectively.

Finally, the class has two properties, `api_model` and `api_model_peek`, which return instances of the `AtlassianInstallation` and `AtlassianInstallationPeek` classes, respectively, created from the current ORM instance.

The file does not start an application server.
```

```json
[]
```

## apps/core/eave/core/internal/orm/document_reference.py

```
This Python code defines a SQLAlchemy ORM (Object-Relational Mapping) model for a table named "document_references". The model is defined in the class `DocumentReferenceOrm` which inherits from a `Base` class. 

The table has the following columns: `team_id`, `id`, `document_id`, `document_url`, `created`, and `updated`. The `team_id` and `id` are of type UUID, `document_id` and `document_url` are strings, and `created` and `updated` are datetime fields. The `id` and `created` fields have default values, and the `updated` field is updated with the current timestamp whenever the row is updated.

The class also includes methods to create a new row in the table (`create`), fetch a single row based on `team_id` and `id` or raise an exception if not found (`one_or_exception`), and fetch a single row based on `team_id` and `id` or return None if not found (`one_or_none`). 

The file does not start an application server. It is a module that defines a database model and related operations.
```

```json
[]
```

## apps/core/eave/core/internal/orm/resource_mutex.py

```
The code defines a Python class `ResourceMutexOrm` that represents a table `resource_mutexes` in a database. This class is used to manage locks on resources, identified by a unique UUID, in a concurrent environment. The class uses SQLAlchemy, an SQL toolkit and Object-Relational Mapping (ORM) system for Python, to interact with the database.

The class has four columns: `id`, `resource_id`, `created`, and `updated`. The `id` and `resource_id` are unique UUIDs, while `created` and `updated` are timestamps.

The class provides two class methods: `acquire` and `release`. The `acquire` method attempts to acquire a lock on a resource. If the resource is already locked and the lock is older than 60 seconds, it forcefully releases the lock and acquires a new one. If the lock is valid (i.e., less than 60 seconds old), it denies access. The `release` method releases the lock on a resource.

The code does not start an application server like Express, Flask, Django, Gin, Rack, etc.
```

```json
[]
```

## apps/core/eave/core/internal/orm/confluence_destination.py

```
The provided Python code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it defines two classes: `ConfluenceDestinationOrm` and `ConfluenceClient`.

`ConfluenceDestinationOrm` is a SQLAlchemy ORM class that represents a table named "confluence_destinations" in a database. It includes methods for creating, updating, and querying entries in this table. The table's columns include `team_id`, `id`, `connect_installation_id`, `space_key`, `created`, and `updated`.

`ConfluenceClient` is a class that interacts with the Confluence API. It includes methods for getting available spaces, searching documents, deleting a document, creating a document, and updating a document. The class uses the team_id and space_key from the `ConfluenceDestinationOrm` instance it is initialized with to make these API requests.

The code also imports several modules and classes from different packages such as datetime, typing, uuid, sqlalchemy, eave.core.internal.document_client, eave.stdlib.confluence_api.operations, eave.stdlib.confluence_api.models, eave.stdlib.core_api.models.connect, eave.stdlib.core_api.models.documents, eave.stdlib.core_api.models.team, eave.core.internal.config, eave.stdlib.logging, and the local database module.
```

```json
[
  "confluence"
]
```

## apps/core/eave/core/internal/orm

```
sentinel
```

## apps/core/eave/core/internal

```
sentinel
```

## apps/core/eave/core

```
starlette_server
```

## apps/slack/socketmode.py

```
This Python script is used to handle Slack's Socket Mode with the Slack Bolt library. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The script imports necessary modules and sets the time to UTC. It then defines a class `AsyncSocketModeWithImmediateAckHandler` which inherits from `AsyncSocketModeHandler`. This class overrides the `handle` method to immediately acknowledge the message from Slack, allowing the app to process the message at its own pace.

The `start_socket_mode` function is defined to start the Socket Mode handler with the Slack app and app token retrieved from the app configuration.

Finally, if this script is run as the main program, it starts the Socket Mode handler asynchronously.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/slack_app.py

```
The code is part of a Python application that interacts with the Slack API using the slack_sdk and slack_bolt libraries. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The code defines an asynchronous function `authorize` that handles the authorization process for Slack. It checks if a team_id and client are provided, retrieves cached data if available, validates the cached token, and falls back to API requests if necessary. If the data is not cached or the cache is inaccessible, it makes an API request to get the installation data and performs an auth test. If the auth test is successful, it caches the new data.

The code also defines an instance of `AsyncApp` from the slack_bolt library. This instance is configured to process events before sending a response, ignore self events, and disable SSL check, request verification, and URL verification. The `authorize` function is passed as an argument to handle authorization.

The `eave.slack.event_handlers.register_event_handlers` function is called to register event handlers with the `AsyncApp` instance. 

Two custom exceptions `MissingSlackTeamIdError` and `MissingSlackClientError` are defined to handle cases where these required parameters are not provided.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/event_handlers.py

```
The code in this file does not start an application server. Instead, it defines a set of event handlers for a Slack application using the Slack Bolt framework. 

The `register_event_handlers` function registers handlers for various Slack events such as a shortcut called "eave_watch_request", a "message" event, and a "member_joined_channel" event. It also registers an error handler.

The `error_handler` function logs any exceptions that occur when running the event handler.

The `shortcut_eave_watch_request_handler` function handles the "eave_watch_request" shortcut event. Currently, it only logs the event and checks for the presence of certain data, but does not perform any other actions.

The `event_message_handler` function handles the "message" event. It processes the message unless it's from a bot, and handles any exceptions that occur during processing.

The `event_member_joined_channel_handler` function handles the "member_joined_channel" event. If the user who joined the channel is the bot itself, it sends a welcome message to the channel and logs an analytics event.

The `noop_handler` function is a no-operation handler that simply acknowledges receipt of an event. It's currently commented out in the `register_event_handlers` function, so it's not being used.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/slack_models.py

```
The code in the file `slack_models.py` is a part of a larger application, possibly a Slack bot or a similar service that interacts with Slack. It does not start an application server. 

The file contains several classes that model different entities in the Slack API, such as:

- `SlackAddReactionError`: An exception class for handling errors when adding reactions in Slack.
- `_SlackContext`: A class for encapsulating the context of a Slack operation, including the client used for making API calls.
- `SlackProfile`: A class representing a user's profile in Slack, with fields for various profile attributes.
- `SlackConversationTopic`: A class representing the topic of a conversation in Slack.
- `SlackConversation`: A class representing a conversation in Slack, with fields for various conversation attributes and methods for fetching conversation data from the Slack API.
- `SlackMessageLinkType`: An enumeration of different types of links that can be included in a Slack message.
- `SlackReaction`: A class representing a reaction in Slack.
- `SlackPermalink`: A class representing a permalink to a message in Slack.
- `SlackMessage`: A class representing a message in Slack, with fields for various message attributes and methods for fetching and formatting message data from the Slack API.
- `SlackShortcut`: An empty class, possibly intended to represent a shortcut in Slack.

The file uses the `slack_sdk` library to interact with the Slack API and the `pydantic` library for data validation and serialization. It also uses the `asyncio` library for asynchronous I/O operations, suggesting that the application is designed to handle multiple operations concurrently.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/app.py

```
This Python script is part of a Slack application. It uses the Starlette framework, which is a lightweight ASGI framework/toolkit, perfect for building high performance asyncio services. 

The script starts by importing necessary modules and functions. It then sets the time to UTC. 

Next, it defines several routes for the application, including routes for warming up, starting, stopping, and processing Slack events. It also mounts a route for Slack events with a status route and an event callback handler.

The script also defines a function for gracefully shutting down the application. If the cache is initialized, it closes the cache client.

Finally, it creates an instance of the Starlette application with the defined middleware, routes, and shutdown function. This instance could be used to start an application server.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/config.py

```
This Python code is not starting an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it is a configuration file for a Slack application within a larger project. 

The file imports necessary modules and sets some constants. It then defines a class `AppConfig` that inherits from `EaveConfig` in the `eave.stdlib.config` module. This class has several properties that fetch secrets from the environment, specifically the `eave_slack_app_signing_secret` and `eave_slack_app_socketmode_token`. These secrets are likely used for authenticating the Slack application. 

The `is_socketmode` property checks if the application is running in socket mode by checking if the "SLACK_SOCKETMODE" environment variable is set. 

Finally, an instance of `AppConfig` is created and assigned to the variable `app_config`.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/requests/warmup.py

```
This Python script is part of a larger application, possibly a web application, but it does not start an application server itself. It uses the Starlette library, which is a lightweight ASGI framework/toolkit, ideal for building high performance asyncio services.

The script defines three classes: WarmupRequest, StartRequest, and StopRequest. Each of these classes inherits from the HTTPEndpoint class provided by Starlette, and each defines an asynchronous get method, which is a handler for HTTP GET requests.

- The WarmupRequest class handles warmup requests. When it receives a GET request, it logs the event, preloads some configurations and public keys, attempts to establish a Redis connection (used for caching), logs an error if the Redis connection fails, and finally responds with an HTTP OK status and the content "OK".
- The StartRequest class handles start requests. When it receives a GET request, it logs the event and responds with an HTTP OK status and the content "OK".
- The StopRequest class handles stop requests. When it receives a GET request, it logs the event and responds with an HTTP OK status and the content "OK".

The script does not define what should happen when a start or stop request is received beyond logging the event and sending a response. This would likely be defined elsewhere in the application.
```

```json
[]
```

## apps/slack/eave/slack/requests/event_processor.py

```
The code is a part of a larger application, possibly a microservice, that processes Slack events. It does not start an application server itself. 

The file defines a class `SlackEventProcessorTask` which inherits from `HTTPEndpoint`, a class from the Starlette framework for building asynchronous web applications. This suggests that the code is part of an asynchronous web application.

The `post` method of the `SlackEventProcessorTask` class handles POST requests. It logs the request, checks if the request has a valid signature, and if it does, it processes the request using an instance of `AsyncSlackRequestHandler` from the Slack Bolt framework. The handler is passed the Slack app instance and additional context properties. If the request does not have a valid signature, it returns a success response to prevent Cloud Tasks from retrying.

The `_is_valid_signature` method checks if the request has all required headers and if the signature of the request is valid. If any of these checks fail, it logs a warning and returns False. If all checks pass, it returns True.

The code uses several modules from the Eave standard library (`eave.stdlib`) for logging, handling requests, managing exceptions, and working with headers and time. It also uses modules from the Slack Bolt framework and the Starlette framework.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/requests/event_callback.py

```
This Python file is part of a larger application, likely a web server, but it does not start the server itself. It defines a class `SlackEventCallbackHandler` which extends `HTTPEndpoint` from the Starlette framework, a lightweight ASGI framework/toolkit. 

The `SlackEventCallbackHandler` class is designed to handle POST requests to the `/slack/events` endpoint. It validates incoming requests, checks if they match certain conditions (SSL check, URL verification, signature validation, and event type), and creates a task for valid requests. 

The class uses several libraries and modules including `http`, `slack_bolt`, `slack_sdk`, `starlette`, and internal modules (`eave.stdlib` and `..config`). It also uses the Slack Bolt framework for building Slack apps in Python, and the Starlette library for building ASGI services.

The class has several private methods to handle different checks:
- `_is_ssl_check`: Checks if the request is an SSL check.
- `_is_url_verification`: Checks if the request is a URL verification.
- `_is_signature_valid`: Verifies the Slack signature to avoid creating tasks for invalid requests.
- `_is_watched_event`: Checks if the event type in the request is one that the application cares about.
- `_create_task`: Creates a task from the request and adds it to a queue.

The file does not start an application server like Express, Flask, Django, Gin, Rack, etc.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/requests

```
sentinel
```

## apps/slack/eave/slack/brain/base.py

```
The code is written in Python and it does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The code defines a class called `Base` which seems to be a base class for a Slack application. The class has several attributes related to a Slack message, user profile, team, subscriptions, and context. It also has an attribute for logging context from the eave library.

The `Base` class has an `__init__` method to initialize these attributes and a `log_event` method to log events with certain parameters. The `log_event` method uses the `analytics.log_event` function from the eave library.

There is also a property method `execution_count` which retrieves the execution count from the slack context. If the execution count is not found, it defaults to 0. 

The code also imports several modules and classes from different libraries such as typing, slack_bolt, eave, and others.
```

```json
[]
```

## apps/slack/eave/slack/brain/intent_processing.py

```
The code is part of a Python module named `intent_processing.py` in a Slack application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The module defines a class `IntentProcessingMixin` that inherits from `DocumentManagementMixin` and `SubscriptionManagementMixin`. This class is responsible for handling different types of actions related to document and subscription management in the Slack application.

The `handle_action` method of this class uses Python's structural pattern matching to handle different types of message actions such as creating documentation, watching or unwatching a conversation, searching, updating, refining, deleting documentation, and handling unknown requests.

The `handle_unknown_request` method handles requests that are not recognized by the system. It logs a warning message and sends a response to the user indicating that the system does not know how to handle the request. It also checks if there is an active subscription or document reference and includes this information in the response.

The `unwatch_conversation` method stops watching a conversation by deleting the subscription for the conversation. It also logs an event indicating that the system has stopped watching the conversation.
```

```json
[]
```

## apps/slack/eave/slack/brain/communication.py

```
The code in the file `communication.py` is part of a larger application, likely a chatbot, that communicates with the Slack API. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file defines a class `CommunicationMixin` that inherits from a `Base` class. This class has several asynchronous methods for sending responses and handling errors. 

The `send_response` method sends a message to the Slack channel and logs the event. If there are any additional parameters, they are included in the log.

The `notify_failure` method sends a failure message to the user and logs the event. If the error is an instance of `HTTPException`, it includes the request ID in the parameters.

The `acknowledge_receipt` method attempts to add a reaction to the message to acknowledge receipt. If it encounters an error, it tries a different reaction. If it fails again, it logs a warning and gives up. If it succeeds, it logs the event.

The `_add_reaction` method attempts to add a reaction to both the message and its parent. If it encounters an error, it logs a warning or an exception and raises the error.

The file uses several libraries including `slack_sdk` for interacting with the Slack API, `eave.stdlib` for handling exceptions, logging, and typing, and Python's built-in `typing` library for type hinting.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/brain/message_prompts.py

```
The code in this file does not start an application server. It is a Python script that uses the OpenAI API to generate responses based on input messages. 

The script imports necessary modules and defines an enumeration class `MessageAction` with possible actions that can be taken based on a message. 

There is a commented-out enumeration class `MessageType` and a commented-out function `message_type`, which seem to be intended for categorizing the purpose of a message.

The function `message_action` takes a context string and an optional logging context as input. It uses the OpenAI API to generate a response based on a prompt that asks what action should be taken based on the input message. The function then uses regular expressions to determine which action corresponds to the generated response.

The function `_get_openai_response` is a helper function that takes a list of messages and a temperature parameter as input, and uses the OpenAI API to generate a response. If no response is generated, it raises an `OpenAIDataError`. 

The script also contains some logging statements for debugging purposes.
```

```json
[
  "openai"
]
```

## apps/slack/eave/slack/brain/subscription_management.py

```
The code in the file `subscription_management.py` is part of a larger application, likely a Slack bot, that interacts with a subscription service. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file defines a class `SubscriptionManagementMixin` that inherits from `CommunicationMixin`. This class has three asynchronous methods: `get_subscription`, `create_subscription`, and `notify_existing_subscription`.

The `get_subscription` method is used to retrieve a subscription from the subscription service. It uses the `GetSubscriptionRequest` operation from the `eave_subscriptions` module to perform this action.

The `create_subscription` method is used to create a new subscription if it doesn't already exist. It uses the `CreateSubscriptionRequest` operation from the `eave_subscriptions` module to perform this action. After creating a subscription, it logs an event named "eave_subscribed" with a description and parameters related to the subscription.

The `notify_existing_subscription` method is used to send a response notifying about an existing subscription. If the subscription has a document reference, it sends a response with a link to the document. If not, it doesn't send any response (the code for sending a response in this case is commented out). 

The methods use various attributes of the class instance such as `eave_ctx`, `eave_team`, and `message` to perform their operations.
```

```json
[]
```

## apps/slack/eave/slack/brain/document_management.py

```
The code in the file `apps/slack/eave/slack/brain/document_management.py` is a Python module that provides functionality for managing documents in a Slack application. It does not start an application server.

The module defines a class `DocumentManagementMixin` which inherits from `ContextBuildingMixin` and `SubscriptionManagementMixin`. This class provides methods for creating, updating, searching, refining, and archiving documentation. 

The `create_documentation_and_subscribe` method subscribes to a thread and creates initial documentation if not already subscribed. If already subscribed, it notifies the user that the conversation is already being watched.

The `create_documentation` method generates documentation from the conversation, parses the generated documentation and adds contextual information, sends the final document to Core API (i.e., saves the document to the organization's documentation destination), and sends a follow-up response to the original Slack thread with a link to the documentation.

The `build_documentation` method generates a document from a conversation, including generating a topic, hierarchy, type of documentation, and resources for the document.

The `search_documentation` method searches for documents based on the context of a conversation and returns relevant documents.

The `update_documentation` method is currently not implemented.

The `refine_documentation` method rebuilds and updates an existing document.

The `archive_documentation` method deletes a document if it exists and there is only one document associated with the conversation.

The `upsert_document` method creates or updates a document in the Core API.

The `search_documents` method uses OpenAI to generate a search query from a conversation and then uses that query to search for documents in the Core API.
```

```json
[
  "slack",
  "core_api",
  "openai"
]
```

## apps/slack/eave/slack/brain/context_building.py

```
The code in the file `context_building.py` is a part of a larger application, possibly a chatbot or conversational AI system, that interacts with the Slack API and the OpenAI GPT-4 model. It does not start an application server.

The file defines a class `ContextBuildingMixin` that inherits from a `Base` class. This class contains methods for building and summarizing the context of a conversation or message thread in Slack. It uses the OpenAI GPT-4 model to format prompts, count tokens, and generate summaries of conversations and content from URLs.

Key methods in the class include:

- `build_message_context`: Builds the context of a message from a user's profile and the expanded text of the message.
- `build_context`: Builds the context of a conversation by concatenating or rolling the context based on the token count.
- `build_concatenated_context`: Builds the context by concatenating all messages in a conversation.
- `build_rolling_context`: Builds the context by rolling over messages in a conversation to maintain important information while removing off-topic or insubstantial content.
- `_summarize_content`: Summarizes content from a URL using the OpenAI GPT-4 model.
- `_rolling_summarize_content`: Summarizes long content by breaking it into digestible chunks and summarizing each chunk.
- `build_link_context_and_subscribe`: Pulls context from any URL links in the message thread, summarizes it, and subscribes to watch for changes in any files.

The code uses Python's asyncio library for asynchronous operations and memoization for caching results of expensive function calls. It also handles exceptions related to Slack data and OpenAI data.
```

```json
[
  "slack",
  "openai_gpt_4"
]
```

## apps/slack/eave/slack/brain/document_metadata.py

```
This Python file, `document_metadata.py`, is part of a larger application and does not start an application server. It is used to generate metadata for a given conversation using OpenAI's GPT-4 model. The file contains several asynchronous functions that interact with the OpenAI API to generate different types of metadata:

1. `get_topic(conversation: str) -> str`: This function generates a short title for the given conversation.

2. `get_hierarchy(conversation: str) -> list[str]`: This function generates a list of parent folder names for the conversation, which can be used to organize the conversation into a directory hierarchy.

3. `get_documentation_type(conversation: str) -> DocumentationType`: This function determines the type of documentation that is most appropriate for the given conversation. It uses an enumeration, `DocumentationType`, which includes `TECHNICAL`, `PROJECT`, `TEAM_ONBOARDING`, `ENGINEER_ONBOARDING`, and `UNKNOWN`.

4. `get_documentation(conversation: str, documentation_type: DocumentationType, link_context: Optional[str]) -> str`: This function generates documentation for the given conversation based on the provided documentation type and link context.

The file also defines a constant, `STRIPPED_CHARS`, which is used to strip certain characters from the beginning and end of strings.
```

```json
[
  "openai"
]
```

## apps/slack/eave/slack/brain/core.py

```
This Python file does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The file is part of a larger application, possibly a chatbot or AI assistant for Slack named 'Eave'. It defines a class 'Brain' that inherits from 'IntentProcessingMixin'. This class is responsible for processing incoming messages and shortcut events from Slack.

The 'process_message' method checks if Eave is mentioned in the message. If Eave is mentioned, it acknowledges the receipt of the message, logs the event, and handles the action. If Eave is not mentioned, it checks if there are any subscriptions for the source of the message. If there are no subscriptions, it ignores the message; otherwise, it logs the event and handles the action.

The 'process_shortcut_event' method acknowledges the receipt of a shortcut event but does not do anything else. It seems like this method is not fully implemented yet as there are commented-out lines of code.

The 'load_data' method retrieves user profile and expanded text from the message. If the expanded text is unexpectedly None, it logs a warning and sets the expanded text to an empty string. It then builds the message context.
```

```json
[
  "slack"
]
```

## apps/slack/eave/slack/brain

```
sentinel
```

## apps/slack/eave/slack

```
eave_slack_app
```

## apps/slack

```
slack_socket_mode
```

## apps/jira/server.ts

```
The code is a server-side script written in Node.js for a Jira application. It imports several modules, including utility functions from the '@eave-fyi/eave-stdlib-ts' library, the main application and addon from './src/app.js', and application configuration settings from './src/config.js'.

The script sets the server port to the value of the 'PORT' environment variable, or defaults to 5500 if 'PORT' is not set. It then starts the server to listen on the specified port and IP address '0.0.0.0'. 

Upon successful startup, it logs a message indicating the port number and environment (NODE_ENV). If the application is running in development mode, it registers the addon with the development application using the 'registerDevApp' function.

Finally, it applies shutdown handlers to the server using the 'applyShutdownHandlers' function. This likely sets up procedures to be followed when the server is shutting down, such as closing database connections or cleaning up resources.

This file does not explicitly start an application server like Express, Flask, Django, Gin, Rack, etc., but it does start a server using the 'app.listen()' method, which is commonly used in Express.js applications.
```

```json
[]
```

## apps/jira/atlassian-connect.json

```
This JSON file is a configuration file for an Atlassian Connect app named "Eave". It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The file contains various settings for the app, including its key, name, description, vendor information, and base URL. It also specifies that the app uses JSON Web Token (JWT) for authentication. 

The lifecycle events of the app are defined with specific endpoints for when the app is installed, enabled, disabled, and uninstalled. 

The app has read and write scopes and it has a webhook module set up to handle the event when a comment is created. 

Finally, the file provides links to the app's JSON configuration file and its website.
```

```json
[]
```

## apps/jira/pm2.config.cjs

```
This code is a configuration file for PM2, a process manager for Node.js applications. It does not directly start an application server like Express, Flask, Django, Gin, Rack, etc., but it does configure how a Node.js application should be managed.

The configuration specifies that a single application named 'jira' should be run using the script located at './server.ts'. The standard output and error of the application are directed to '/dev/stdout' and '/dev/stderr' respectively. The interpreter for the script is specified as 'ts-node', which is a TypeScript execution environment and REPL for Node.js. The '--swc' argument is passed to the interpreter, which likely indicates that the SWC compiler should be used for TypeScript transpilation.

The path to the 'ts-node' interpreter is resolved using the 'node:path' module's 'join' function, with the current directory and 'node_modules/.bin/ts-node' as arguments. This means that the 'ts-node' binary located in the project's 'node_modules' directory will be used to run the script.
```

```json
[]
```

## apps/jira/credentials.json

```
The code is a JSON file that contains the credentials for a Jira host. It does not start an application server. The credentials include the host URL, the product name (Jira), a username, and a password.
```

```json
[]
```

## apps/jira/package.json

```
This is a package.json file for a Node.js application. It does not directly start an application server, but it does specify scripts and dependencies for the application. 

The "start" script uses PM2, a process manager for Node.js applications, to start the application using a configuration file named pm2.config.cjs. The "--no-daemon", "--silent", "--no-pmx", "--no-automation", "--disable-trace", and "--no-vizion" options are used to modify the behavior of PM2.

The application has several dependencies, including "@eave-fyi/eave-stdlib-ts", "@eave-fyi/eave-pubsub-schemas", "@eave-fyi/es-config", "@swc/core", "atlassian-connect-express", "express", "helmet", "pm2", and "ts-node". The versions of these dependencies are specified.

The application also has several development dependencies, including "@types/express", "@types/node", "@types/request", "@typescript-eslint/eslint-plugin", "@typescript-eslint/parser", "eslint", "eslint-config-airbnb-base", "eslint-plugin-import", "eslint-plugin-unused-imports", "eslint-plugin-yaml", "longjohn", "ngrok", "nodemon", "sqlite3", and "typescript". Again, the versions of these dependencies are specified.

The comment at the end of the file notes that the "longjohn" package must be installed, or the atlassian-connect-validator will crash the app in development. 

The presence of "express" in the dependencies indicates that Express.js is likely used as the application server for this project.
```

```json
[]
```

## apps/jira/config.json

```
This JSON file appears to be a configuration file for a Jira application, not a server startup file. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The configuration file contains settings for both development and production environments. For both environments, it specifies a local base URL, a flag for setting up an install route, details about the store including the adapter, app key, product type, and eave origin, and the port number. 

In the development environment, the local base URL is "http://apps.eave.run/jira", and the port number is set to the value of the environment variable "$PORT". 

In the production environment, the local base URL is "https://apps.eave.fyi/jira", and it also includes a whitelist of domains. The port number is also set to the value of the environment variable "$PORT". 

The "store" object in both environments has the same values: "eave-api-store" for adapter, "eave-jira" for app key, "jira" for product type, and "eave_jira_app" for eave origin.
```

```json
[]
```

## apps/jira/src/types.ts

```
The code does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

This TypeScript file defines a series of interfaces that represent the structure of various objects related to the Jira API. These interfaces include `JiraProject`, `JiraIssueType`, `JiraStatusCategory`, `JiraStatus`, `JiraUser`, `JiraIssue`, `JiraAssociatedUsers`, `JiraIssueLinkType`, `JiraChange`, `JiraChangelog`, `JiraComment`, `JiraIdKey`, `JiraStatusId`, `JiraTransition`, `JiraContext`, and some event payloads like `JiraWebhookEvent` and `JiraCommentCreatedEventPayload`.

These interfaces are used to define the shape of data when interacting with the Jira API, ensuring that the data adheres to the correct structure and types. For example, a `JiraProject` has properties like `id`, `key`, `name`, `projectTypeKey`, `simplified`, and `avatarUrls`. 

The file also notes that Atlassian does not publicly provide these type definitions, so they have been defined manually in this file.
```

```json
[
  "jira"
]
```

## apps/jira/src/jira-client.ts

```
The code is from a TypeScript file that defines a class named `JiraClient` which extends the `ConnectClient` class. This class is used to interact with the Jira API. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The `JiraClient` class has three methods:

1. `getAuthedJiraClient`: This static method creates an authenticated instance of `JiraClient`. It takes an object as an argument that includes a request object, an AddOn object, and optionally a teamId and clientKey. It uses these to create an authenticated `ConnectClient` instance and then returns a new `JiraClient` instance.

2. `getUser`: This method retrieves a user from the Jira API. It takes an object with an accountId as an argument, constructs a request object, and sends it to the Jira API. If the response status code is 400 or higher, it returns undefined. Otherwise, it parses the response body as a `JiraUser` object and returns it.

3. `postComment`: This method posts a comment to a Jira issue. It takes an object with an issueId and a commentBody as arguments, constructs a request object, and sends it to the Jira API. If the response status code is 400 or higher, it returns undefined. Otherwise, it parses the response body as a `JiraComment` object and returns it.

The file also imports several modules and types from various libraries and local files.
```

```json
[
  "jira"
]
```

## apps/jira/src/app.ts

```
The code is a part of a Node.js application that uses the Express.js framework to create a server. It also uses the Atlassian Connect Express (ACE) library to integrate with Atlassian applications like Jira.

The code starts by importing necessary modules and libraries. It then registers 'eave-api-store' with the ACE store using an adapter called 'EaveApiAdapter'. 

An Express app and an ACE addon are created. The addon is configured with a descriptorTransformer function that sets the baseUrl of the descriptor to a specific URL if the environment is 'production'.

Several middlewares are applied to the Express app for security, handling common request and response scenarios, internal API routes, and webhooks. 

A Google App Engine (GAE) lifecycle router is also added to the app.

A root router is created and mounted at the '/jira' path on the app. The root router is then configured to use a status router, a webhook router, and an internal API router.

Finally, common response middlewares are applied to the app.

The file does not appear to start the server itself, but it exports the Express app and the ACE addon, which can be used elsewhere to start the server.
```

```json
[
  "atlassian",
  "google_app_engine"
]
```

## apps/jira/src/config.ts

```
The code in the file `apps/jira/src/config.ts` is a TypeScript module that imports two classes, `EaveConfig` and `EaveOrigin`, from the `@eave-fyi/eave-stdlib-ts` package. It then extends the `EaveConfig` class to create a new class `AppConfig`. This new class has two properties: `eaveOrigin`, which is set to `EaveOrigin.eave_jira_app`, and `eaveJiraAppAccountId`, which is set to a specific string value. 

An instance of this `AppConfig` class is created and exported as the default export of the module. This instance can be imported in other parts of the application to access the configuration settings.

This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's just a configuration file.
```

```json
[]
```

## apps/jira/src/events/routes.ts

```
This code is written in TypeScript and is part of a larger application that uses the Express.js framework for handling HTTP requests. It does not start an application server itself, but it exports two functions that are used to set up routes and middleware for handling webhooks in the application.

The `applyWebhookMiddlewares` function sets up middleware for a specific path in the Express app. It applies the `express.json()` middleware to parse incoming requests with JSON payloads and also applies middleware provided by the Atlassian Connect Express (ACE) library.

The `WebhookRouter` function creates a new Express router and sets up a POST route at the root path. This route handles incoming webhook events. It uses the ACE library's authentication middleware to authenticate requests. It then logs the event, creates an authenticated Jira client, and processes the event based on its type. If the event type is 'comment_created', it calls a specific event handler. If the event type is not recognized, it logs a warning and sends a 200 status response.

The router also uses a `LifecycleRouter` from the Eave standard library, which is configured for Atlassian's Jira product and uses a configuration value for the Eave origin.

The file also imports several modules, including Express, ACE, a logger from the Eave standard library, a configuration module, a Jira client module, and a module for handling 'comment_created' events.
```

```json
[
  "atlassian_jira"
]
```

## apps/jira/src/events/comment-created.ts

```
The code in the file `apps/jira/src/events/comment-created.ts` does not start an application server. Instead, it exports an asynchronous function `commentCreatedEventHandler` which handles the event of a comment being created in Jira.

The function takes a request and response object from Express, and a Jira client as arguments. It first checks if the payload of the request contains an issue, and if the author of the comment is not an app. If these conditions are not met, it sends a response with status 400 or 200 respectively and returns.

Next, it checks if the comment body contains any mentions of Eave (a user or app). If Eave is not mentioned, it sends a response with status 200 and returns.

Then, it queries for a connect installation and logs an event if Eave was mentioned in a Jira comment. If there is no team available, it sends a response with status 400 and returns.

The function then cleans the comment body, determines the intent of the comment, and performs a search query if the intent is 'search'. It builds a response based on the search results and posts a comment in Jira. Finally, it sends a response with status 200.

The file also includes helper functions to clean the comment body, get the search query, determine the intent of the comment, build the Eave response, and check if a user is Eave.
```

```json
[
  "jira"
]
```

## apps/jira/src/events

```
sentinel
```

## apps/jira/src/api/routes.ts

```
The code is written in TypeScript and it uses Express, a web application framework for Node.js. It defines a function called `InternalApiRouter` that takes an object with a property `addon` of type `AddOn` from the 'atlassian-connect-express' library as an argument. The function creates a new instance of an Express router and returns it. However, the router is currently not used for any routing. The file does not start an application server itself, it just exports a function to create a router.
```

```json
[]
```

## apps/jira/src/api

```
sentinel
```

## apps/jira/src

```
sentinel
```

## apps/jira

```
jira_server
```

## apps/appengine-default/main.py

```
The code simply prints the string "OK" to the console. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.
```

```json
[]
```

## apps/appengine-default

```
sentinel
```

## apps/github/server.ts

```
The code in the file apps/github/server.ts is used to start an application server. It imports a function called applyShutdownHandlers from a module named '@eave-fyi/eave-stdlib-ts/src/api-util.js' and an object called app from './src/app.js'. It then sets a constant named PORT to the value of the environment variable 'PORT' or to 5300 if 'PORT' is not defined. The server is started by calling the listen method on the app object with PORT and '0.0.0.0' as arguments. A callback function is passed to the listen method which logs a message indicating that the app is listening on the specified port and the current environment. Finally, the applyShutdownHandlers function is called with an object containing the server as a property. This function presumably sets up handlers for shutting down the server gracefully. The specific application server framework (like Express, Flask, Django, etc.) is not explicitly mentioned in the code.
```

```json
[]
```

## apps/github/pm2.config.cjs

```
This code is a configuration file for PM2, a process manager for Node.js applications. It does not directly start an application server like Express, Flask, Django, Gin, Rack, etc., but it configures how a Node.js application should be managed by PM2.

The configuration specifies that the application named 'github' should be run using the script './server.ts'. The standard output and error of the application are directed to '/dev/stdout' and '/dev/stderr' respectively. The interpreter used to run the script is 'ts-node', a TypeScript execution environment and REPL for Node.js, located in the project's node_modules directory. The interpreter is passed the argument '--swc', which might be related to using SWC (a super-fast JavaScript/TypeScript compiler) with ts-node.
```

```json
[]
```

## apps/github/package.json

```
This is a package.json file for a Node.js application. It does not directly start an application server, but it does list "express" as one of its dependencies, which is a popular framework for building web applications and APIs in Node.js.

The "start" script uses PM2, a process manager for Node.js applications, to start the application using a configuration file named pm2.config.cjs.

The application has several dependencies, including libraries for working with GitHub's API (@octokit/graphql-schema and @octokit/webhooks), a TypeScript standard library (@eave-fyi/eave-stdlib-ts), and a library for publishing and subscribing to messages (@eave-fyi/eave-pubsub-schemas).

The application also has several development dependencies, which are likely used for linting and type checking the code. These include ESLint (a linter), TypeScript (a static type checker), and several plugins and configuration packages for ESLint and TypeScript.
```

```json
[
  "github"
]
```

## apps/github/src/types.ts

```
The code does not start an application server. It is a TypeScript file that defines a type for a GitHub operations context. This context includes an instance of Octokit (a GitHub API client) and a logging context from the Eave standard library. The file is part of a larger application, likely used to interact with the GitHub API.
```

```json
[
  "github"
]
```

## apps/github/src/app.ts

```
The code is written in TypeScript and uses the Express.js framework to create a server application. It imports several middleware functions and routers from different modules. 

The server application, `app`, is created using Express.js. The `helmetMiddleware` is applied to the app for security purposes. 

The `applyCommonRequestMiddlewares`, `applyInternalApiMiddlewares`, and `applyWebhookMiddlewares` functions are used to apply various middlewares to the app. The `applyInternalApiMiddlewares` and `applyWebhookMiddlewares` are applied to specific paths, '/github/api' and '/github/events' respectively.

A new router, `rootRouter`, is created and mounted on the '/github' path of the app. The `StatusRouter`, `WebhookRouter`, and `InternalApiRouter` are then applied to this root router at different paths.

Finally, the `applyCommonResponseMiddlewares` function is used to apply common response middlewares to the app.
```

```json
[]
```

## apps/github/src/dispatch.ts

```
The code in this file does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it exports a default asynchronous function named `dispatch` which is designed to handle incoming HTTP requests and responses. 

The `dispatch` function is designed to handle GitHub webhook events. It first extracts necessary information from the request headers and body, such as the event name, delivery ID, signature, installation ID, and payload. It then logs the webhook request information and verifies the signature of the request. 

If the signature is not verified and the application is not in development or dev mode, it sends a 400 status response. If the signature is verified, it gets the GitHub App installation client and calls the appropriate handler for the event with the payload and a context object that includes the Octokit client and logging context. 

The function ends by sending a 200 status response. The `push` event is registered with a handler in this file.
```

```json
[
  "github"
]
```

## apps/github/src/registry.ts

```
The code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it is a TypeScript module that provides a registry for GitHub webhook event handlers. 

It imports necessary types and a logging utility, then declares a type for the handler functions that will be stored in the registry. 

The registry is an object where the keys are strings (presumably the names of the events) and the values are these handler functions.

The module exports two functions: 
1. `registerHandler` which takes a name and a function, binds the function to null (meaning it will not change the context (`this`) when called), stores it in the registry under the provided name, and logs that the handler was registered.
2. `getHandler` which takes a name and returns the handler function registered under that name from the registry, or undefined if no such handler exists.
```

```json
[
  "github"
]
```

## apps/github/src/config.ts

```
The code does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it is a configuration file for a GitHub application. 

The file imports two modules from '@eave-fyi/eave-stdlib-ts', namely 'EaveConfig' and 'EaveOrigin'. It then defines a class 'AppConfig' that extends 'EaveConfig'. 

In this class, it sets the 'eaveOrigin' to 'EaveOrigin.eave_github_app' and 'eaveGithubAppId' to '300560'. It also defines several getter methods that return promises of strings. These methods are used to get secrets for the GitHub app's webhook secret, private key, client ID, and client secret. 

The secrets are presumably stored in a secure location and are accessed by calling the 'getSecret' method with the appropriate key. 

Finally, it exports an instance of 'AppConfig' as 'appConfig'.
```

```json
[
  "github"
]
```

## apps/github/src/events/routes.ts

```
The code is written in TypeScript and uses the Express.js framework to handle HTTP requests. It does not start an application server itself, but it exports functions that can be used to set up routes and middleware in an Express.js application.

The `applyWebhookMiddlewares` function applies a middleware to the Express app at a specified path. This middleware uses the `raw` function from Express to parse incoming requests as raw data, specifically JSON data, with a limit of 5mb. This is done instead of using the standard `express.json()` parser due to GitHub signature verification requirements.

The `WebhookRouter` function creates and returns a new Express router. This router is set up to handle POST requests at its root path (`/`). When a POST request is received, it dispatches the request and response objects to a function imported from `../dispatch.js`. If the dispatch function completes successfully, it ends the response. If an error is thrown during the dispatch, it passes the error to the next middleware in the chain.
```

```json
[]
```

## apps/github/src/events/push.ts

```
The code in the file `push.ts` is a handler function for GitHub's push events. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The handler function processes GitHub push events using the Octokit library. It first checks if the event is a branch push event and ignores tag pushes. It then fetches the team id from the GitHub installation. 

For each commit in the push event, it fetches the file contents of modified files and checks if there is a subscription for these files. If a subscription exists, it fetches the file contents using a GraphQL query and builds a description of the file. 

It then uses the OpenAI API to generate an explanation of the code changes in the file. This explanation is then used to create a document which is stored using the `upsertDocument` function.

The handler function uses various utility functions and libraries such as `OpenAIClient` for interacting with OpenAI, `eaveLogger` for logging, and `GraphQLUtil` for loading GraphQL queries. It also uses various types and models from the Octokit library and the Eave standard library.
```

```json
[
  "github",
  "openai"
]
```

## apps/github/src/events

```
sentinel
```

## apps/github/src/graphql/getResource.graphql

```
This code does not start an application server. It is a GraphQL query that fetches a resource from a given URL. The resource in this case is a GitHub repository. The query retrieves the login of the repository owner and the name of the repository.
```

```json
[
  "github"
]
```

## apps/github/src/graphql/getFileContentsByPath.graphql

```
This file does not start an application server. Instead, it contains a GraphQL query that fetches the contents of a file from a GitHub repository. The query takes three parameters: the owner of the repository, the name of the repository, and an expression that specifies the file path. The query returns various details about the file, including its type, commit resource path, ID, and OID. If the file is a blob (a type of object that can store data), it also returns the file's text content. If the file is a tree (a type of object that can store directories), it returns a list of entries in the directory, each with its name and details about its blob objects.
```

```json
[
  "github"
]
```

## apps/github/src/graphql/getFileContents.graphql

```
This is a GraphQL query that fetches file contents from a GitHub repository. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The query takes four parameters: the repository owner's username (`repoOwner`), the repository name (`repoName`), the commit ID (`commitOid`), and the file path (`filePath`). 

It retrieves the following information from the specified repository: 
- The repository's ID, owner's name (if the owner is an organization), and name.
- The specified commit's ID and OID (Object ID).
- The specified file's OID (Object ID), name, path, language, and text content.
```

```json
[
  "github"
]
```

## apps/github/src/graphql/getRefs.graphql

```
This code is a GraphQL query that fetches data from a GitHub repository. It does not start an application server. 

The query takes four parameters: the owner of the repository, the name of the repository, a query string to filter the references, and a prefix string to filter the references. 

The query fetches the first 10 references (refs) from the repository, ordered by the date of the commit associated with each tag in descending order. The references are filtered by the provided prefix and query string. 

For each reference, the query fetches its name.
```

```json
[
  "github"
]
```

## apps/github/src/graphql

```
sentinel
```

## apps/github/src/api/routes.ts

```
The code is a part of a Node.js application using the Express.js framework. It does not start an application server itself but defines a part of the application's API routes.

The file exports a function `InternalApiRouter` that returns an Express router. This router has two POST endpoints: `/content` and `/subscribe`. 

The `/content` endpoint uses the `getSummary` function imported from the `content.js` file. It takes a request and a response as parameters. If the function executes successfully, it ends the response; if there's an error, it passes the error to the next middleware function.

Similarly, the `/subscribe` endpoint uses the `subscribe` function imported from the `subscribe.js` file. It also takes a request and a response as parameters and follows the same error handling pattern as the `/content` endpoint.
```

```json
[]
```

## apps/github/src/api/content.ts

```
The code in the file `content.ts` is a part of a larger application, possibly a server-side application, but it does not start an application server itself. It uses Express.js for handling HTTP requests and responses, and Octokit, a client for the GitHub API.

The main function exported from this module is `getSummary(req: Request, res: Response)`. This function is an Express.js middleware that handles a request to fetch the content of a file from a GitHub repository. It expects the request body to contain a URL of the file in a GitHub repository. It uses the Octokit client to fetch the file content and sends it back in the response.

The module also contains several helper functions that are used to fetch the file content from GitHub:

- `getFileContent(client: Octokit, url: string, ctx: LogContext)`: This function fetches the content of a file located at a given URL. It returns null if the GitHub API request fails.

- `getRepositoryByUrl(client: Octokit, url: string, ctx: LogContext)`: This function fetches a GitHub repository by its URL.

- `getFileInfoFromUrl(client: Octokit, repository: Repository, url: URL, ctx: LogContext)`: This function extracts information about a file from its URL.

- `getRawContent(client: Octokit, url: string, ctx: LogContext)`: This function fetches the raw content of a file from its URL using the raw.githubusercontent.com feature. It returns null if the URL is not a path to a file or if some other error was encountered.
```

```json
[
  "github"
]
```

## apps/github/src/api/subscribe.ts

```
The file `subscribe.ts` does not start an application server. It is a module that exports a single asynchronous function named `subscribe`. This function is designed to handle HTTP requests and responses in an Express.js application.

The `subscribe` function takes in a request and response object, logs the context, validates the request body, fetches the installation ID, and retrieves information about a GitHub repository. If all validations pass and all necessary information is retrieved successfully, it creates a subscription using the `createSubscription` function imported from the `@eave-fyi/eave-stdlib-ts/src/core-api/operations/subscriptions.js` module. The response from this function is then sent back to the client as a JSON response.

The module also contains two helper functions: `getRepo` and `getRepoLocation`. The `getRepo` function uses the Octokit client to fetch data about a GitHub repository. The `getRepoLocation` function parses a GitHub URL to extract the organization name and repository name.
```

```json
[
  "github"
]
```

## apps/github/src/api/repos.ts

```
The code in the file `repos.ts` does not start an application server. Instead, it provides functionality to interact with GitHub repositories using the Octokit library, which is a client for the GitHub API.

The main function exported from this file is `getSummary()`, which is an asynchronous function that takes in a request and a response object. It retrieves the content of a file from a GitHub repository based on a URL provided in the request body. If the URL is not provided or invalid, or if there are issues with the GitHub installation ID, it sends back an error response.

The `getSummary()` function uses several helper functions to accomplish its task:

- `getFileContent()`: This function fetches the content of a file located at a given URL. It returns null if there's an error with the GitHub API request.

- `getRepositoryByUrl()`: This function fetches a GitHub repository based on a given URL. It returns null if the URL is invalid or if the resource fetched is not a repository.

- `getFileInfoFromUrl()`: This function retrieves information about a file from a given URL. It returns null if the URL is invalid or if no branches match the URL.

- `getRawContent()`: This function fetches raw content from a GitHub file using the raw.githubusercontent.com feature. It returns null if the URL is not a path to a file or if there's an error encountered.

The code also includes extensive logging for error handling and debugging purposes.
```

```json
[
  "github"
]
```

## apps/github/src/api

```
sentinel
```

## apps/github/src/lib/graphql-util.ts

```
The file `graphql-util.ts` is a utility file that contains functions for interacting with GitHub's GraphQL API. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file exports four asynchronous functions:

1. `loadQuery(name: string)`: This function reads a GraphQL query from a file, validates it, and caches it for future use. If the query is already in the cache, it retrieves it from there instead of reading from the file again.

2. `getProjectV2ItemFieldValue(itemNodeId: string, fieldName: string, context: GitHubOperationsContext)`: This function uses the `loadQuery` function to load a specific query and then executes it using the provided context and variables. The result is a `ProjectV2Item`.

3. `getIssueByNodeId(nodeId: string, context: GitHubOperationsContext)`: This function is similar to the previous one but retrieves an `Issue` by its node ID.

There are also two commented-out functions that seem to be designed to retrieve a label and a project field from GitHub, respectively. These functions also use the `loadQuery` function and cache their results.
```

```json
[
  "github"
]
```

## apps/github/src/lib/octokit-util.ts

```
The code in this file does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it is a utility file that provides functions to interact with GitHub's API using the Octokit library. 

The file exports three functions:

1. `createOctokitClient`: This function takes an installation ID as an argument and returns an Octokit client instance for that installation. It does this by first creating an App client and then using it to get the Octokit client for the given installation ID.

2. `createAppClient`: This function creates and returns a new instance of the App client. It does this by using the app configuration to get the necessary credentials (app ID, private key, and webhook secret) and then using these to instantiate the App client.

3. `getInstallationId`: This function takes a team ID and a logging context as arguments and returns the installation ID for the GitHub integration of the given team. It does this by first getting the team's information from the Eave API and then extracting the installation ID from the team's GitHub integration data. If the team does not have a GitHub integration, it logs an error message and returns null.
```

```json
[
  "github",
  "eave"
]
```

## apps/github/src/lib/cache.ts

```
The code is importing a module named 'EphemeralCache' from a package '@eave-fyi/eave-stdlib-ts/src/cache.js'. Then it exports an instance of 'EphemeralCache'. This file does not start an application server like Express, Flask, Django, Gin, Rack etc. It's just a module that exports a cache object.
```

```json
[]
```

## apps/github/src/lib

```
sentinel
```

## apps/github/src

```
github_server
```

## apps/github

```
github_server
```

## apps/confluence/server.ts

```
The code is written in Node.js and it starts an application server. It imports several modules, including a module for handling shutdowns, a module for registering a development application, the main application module, and a configuration module. 

The server is set to listen on a specified port, defaulting to 5400 if no port is specified in the environment variables. When the server starts, it logs a message to the console indicating that it's listening and on which port. If the application is running in development mode, it registers the development application.

Finally, it applies shutdown handlers to the server, which presumably handle any necessary cleanup or other tasks when the server is shutting down.
```

```json
[]
```

## apps/confluence/atlassian-connect.json

```
This JSON file appears to be a configuration file for an Atlassian Connect app called "Eave". It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The file contains metadata about the app such as its key, name, description, and vendor information. It also specifies that the app uses JWT (JSON Web Tokens) for authentication. 

The "lifecycle" section defines endpoints for different lifecycle events of the app, such as when it's installed, enabled, disabled, or uninstalled. 

The "scopes" section indicates that the app has read and write permissions. 

The "modules" section is currently empty, which means no modules are defined for this app. 

Finally, the "links" section provides URLs for the app's own configuration file and its website.
```

```json
[]
```

## apps/confluence/pm2.config.cjs

```
This code is a configuration file for PM2, a process manager for Node.js applications. It does not directly start an application server like Express, Flask, Django, Gin, Rack, etc., but it does manage the Node.js process that could be running such a server.

The configuration exports an object with an "apps" array. Each object in this array represents a different application that PM2 should manage. In this case, there's only one application named 'confluence'. 

The 'script' property points to the entry point of the application ('./server.ts'), which is a TypeScript file. The 'out_file' and 'error_file' properties redirect standard output and standard error to '/dev/stdout' and '/dev/stderr' respectively.

The 'interpreter' property specifies the path to the TypeScript Node interpreter ('ts-node') located in the project's node_modules directory. The 'interpreter_args' property passes the '--swc' argument to the interpreter, which is a JavaScript/TypeScript compiler.
```

```json
[]
```

## apps/confluence/credentials.json

```
The provided code is a JSON file that contains credentials for accessing a Confluence product hosted on "https://eave-fyi-dev.atlassian.net". The credentials include a username and a password. This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's just a configuration file used to store sensitive data.
```

```json
[
  "confluence"
]
```

## apps/confluence/package.json

```
This is a package.json file for a Node.js application. It does not directly start an application server, but it does specify scripts that can be used to start the application, and it lists the dependencies that the application needs to run.

The "scripts" section defines three scripts: 

- "start": This script uses PM2, a process manager for Node.js applications, to start the application using the configuration specified in pm2.config.cjs.
- "start-dev": This script first tries to kill any running instances of ngrok (a tool for exposing local servers to the internet), then starts the application using nodemon (a tool that automatically restarts the application when file changes are detected) and the server.ts file.
- "test": This script runs tests using Ava, a test runner for Node.js, with a specific configuration file.

The "dependencies" section lists the libraries that the application needs to run. These include several custom libraries (eave-stdlib-ts, eave-pubsub-schemas, es-config), as well as several widely-used libraries such as Express (a web application framework for Node.js), Helmet (a security middleware for Express), and PM2.

The "devDependencies" section lists the libraries that are needed for development but not for running the application. These include various typescript and eslint plugins, Ava for testing, nodemon for automatic restarting during development, and several others.

The file also includes a comment indicating that the "longjohn" library must be installed or else the atlassian-connect-validator will crash the app in development.
```

```json
[]
```

## apps/confluence/config.json

```
The code is a configuration file in JSON format for a product named "confluence". It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The configuration file contains two main sections: "development" and "production". Each section contains the base URL for the application, a flag to determine whether to set up an install route, the store configuration, and the port number. 

In the "development" section, the base URL is a placeholder that will be overridden at runtime with the ngrok host. The store configuration includes the adapter name, app key, product type, and origin.

In the "production" section, the base URL is a fixed URL. The store configuration is similar to the development section. Additionally, there is a "whitelist" array that contains a list of domains that are allowed to access the application.
```

```json
[]
```

## apps/confluence/src/app.ts

```
The code is a Node.js application using the Express.js framework. It sets up an Atlassian Connect Express (ACE) application for the Confluence product. The ACE framework is used to build Atlassian Apps.

The code imports several modules and middleware functions, including security policies, API utilities, an API adapter, common middleware, API routes, and webhook routes. It also imports a configuration file.

The ACE store is registered with an 'eave-api-store' using the EaveApiAdapter.

An Express application and an ACE addon are created. The addon's configuration includes a descriptorTransformer function that sets the baseUrl to a production URL if the environment is set to 'production'.

Several middleware functions are applied to the Express app for security, common request handling, internal API handling, and webhook handling. 

A Google App Engine (GAE) lifecycle router is also used.

A root router is created and mounted at the '/confluence' path. The root router uses a status router and routes for webhooks and internal APIs.

Finally, common response middleware is applied to the app.
```

```json
[
  "atlassian_confluence",
  "google_app_engine"
]
```

## apps/confluence/src/confluence-client.ts

```
The code in the file `apps/confluence/src/confluence-client.ts` does not start an application server. Instead, it defines a class `ConfluenceClient` that extends `ConnectClient`. This class is used to interact with the Confluence API, a service for managing content in Atlassian's Confluence software.

The `ConfluenceClient` class includes methods for various operations such as:

- `getAuthedConfluenceClient`: This static method returns an authenticated Confluence client.
- `getSpaceByKey`: This method retrieves a Confluence space by its key.
- `getPageByTitle`: This method retrieves a Confluence page by its title.
- `getPageById`: This method retrieves a Confluence page by its ID.
- `getPageChildren`: This method retrieves the children of a Confluence page.
- `getSpaceRootPage`: This method retrieves the root page of a Confluence space.
- `createPage`: This method creates a new Confluence page.
- `archivePage`: This method archives a Confluence page.
- `getSpaces`: This method retrieves all Confluence spaces.
- `search`: This method performs a search in Confluence.
- `updatePage`: This method updates a Confluence page.
- `getSystemInfo`: This method retrieves system information from Confluence.

Each of these methods makes an HTTP request to the Confluence API and returns a Promise that resolves with the response data.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/config.ts

```
The code in the file `apps/confluence/src/config.ts` does not start an application server. Instead, it defines and exports a configuration for an application. 

The configuration is defined in a class called `AppConfig`, which extends `EaveConfig` from the `@eave-fyi/eave-stdlib-ts` package. The `AppConfig` class has two properties: `eaveOrigin` and `eaveConfluenceAppAccountId`. 

The `eaveOrigin` property is set to `EaveOrigin.eave_confluence_app`, which is imported from the same package as `EaveConfig`. 

The `eaveConfluenceAppAccountId` property is set to a hardcoded string, which is noted to be the same across all installations for the "eave-confluence" app key.

Finally, an instance of the `AppConfig` class is created and exported as `appConfig`.
```

```json
[]
```

## apps/confluence/src/events/routes.ts

```
The code is written in TypeScript and is part of a larger application that uses the Express.js framework to handle HTTP requests. It does not start an application server itself, but it defines and exports two functions, `applyWebhookMiddlewares` and `WebhookRouter`, which are likely used elsewhere in the application to set up routes and middleware.

The `applyWebhookMiddlewares` function takes an Express app, an Atlassian AddOn, and a path as arguments. It applies two middleware functions to the specified path: `express.json()` for parsing JSON request bodies, and `addon.middleware()` which is likely specific to the Atlassian AddOn.

The `WebhookRouter` function takes an Atlassian AddOn as an argument and returns a router. It first creates a new router and a lifecycle router, which is then used as middleware for the router. It also defines a POST route at the root path ('/') of the router. This route uses the `addon.authenticate()` middleware to authenticate requests, logs the event with `eaveLogger`, and does not send any response back to the client.
```

```json
[]
```

## apps/confluence/src/events

```
sentinel
```

## apps/confluence/src/api/routes.ts

```
This code is a part of an Express application server in Node.js. It defines a router for the internal API of a Confluence client application. The router has five routes:

1. POST /spaces/query: This route queries available spaces in Confluence. It uses the `getAvailableSpaces` function to perform the query.

2. POST /content/search: This route searches for content in Confluence. It uses the `searchContent` function to perform the search.

3. POST /content/create: This route creates new content in Confluence. It uses the `createContent` function to create the content.

4. POST /content/update: This route updates existing content in Confluence. It uses the `updateContent` function to update the content.

5. POST /content/delete: This route deletes existing content in Confluence. It uses the `deleteContent` function to delete the content.

Each route handler is an asynchronous function that creates a Confluence client, performs an operation (query, search, create, update, or delete), and then ends the response. If an error occurs during any of these operations, it is passed to the next middleware function for error handling.

The `getConfluenceClient` function is used to create an authenticated Confluence client for a specific team. The team ID is retrieved from the request headers.

The code also includes a commented-out route handler for a potential proxy to the Confluence API.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/util.ts

```
The code in this file does not start an application server. It is a utility file for a Confluence API. It imports a library called 'html-entities' and a module called 'ConfluenceClient' from a local file. 

The file exports two things: a function and a type. 

The function 'cleanDocument' takes a string as an argument, decodes any HTML entities in the string, replaces decoded ampersands with their encoded equivalent (since Confluence can't handle decoded ampersands), and replaces any '<br>' tags with self-closing '<br/>' tags (since Confluence can't handle unclosed br tags). The function then returns the cleaned string.

The exported type 'ConfluenceClientArg' is an object that has one property 'confluenceClient' of type 'ConfluenceClient'.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/search-content.ts

```
This code does not start an application server. 

The code is a module that exports a single asynchronous function, `searchContent`, which is used to search for content in Confluence, a team collaboration software. 

The function takes an object as an argument, which includes an HTTP request (`req`), HTTP response (`res`), and a Confluence client (`confluenceClient`). 

It first loads a logging context from the response and extracts the search parameters from the request body. If a `space_key` is provided, it is added to the `cqlcontext`. If a `text` is provided and it is not empty, it is added to the `cqlConditions` array. 

Then, it joins all conditions in the `cqlConditions` array with 'AND' to form a CQL (Confluence Query Language) query. If the CQL query is empty, it logs an error and sends a 500 status code as the response. 

Otherwise, it sends the CQL query to the Confluence client to perform the search. It filters out any results that do not have a body and sends the filtered results back in the response as JSON.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/create-content.ts

```
The code in the file `apps/confluence/src/api/create-content.ts` does not start an application server. Instead, it exports a function `createContent` which is used to create content on Confluence, a popular team collaboration software. 

The function takes an object as an argument which includes a request, response, and a Confluence client. It then extracts the document and the destination from the request body. The function checks if the space and homepage exist in the destination. If not, it logs a warning and sends a 400 status response.

If the document does not have any parent, it is placed in the root of the space. A unique name for the document is generated using the `resolveTitleConflict` function to avoid any naming conflicts. The document is then created using the Confluence client and the response is sent back.

If the document has at least one parent, a hierarchy is built. The function then traverses through the hierarchy to find the correct location for the document in the Confluence space. If a directory with the same name exists at that level, it enters it. If not, it creates a new directory at that level with a unique name.

Finally, the function creates a new document in the parent directory with a unique name and sends back the response.

The `resolveTitleConflict` function is used to generate a unique title for a document or directory. It checks if a page with the same title exists in the space. If it does, it appends a number to the title to make it unique. If after 20 attempts, a unique title is not found, it appends a UUID to the title.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/delete-content.ts

```
The code in the file `apps/confluence/src/api/delete-content.ts` is a module that exports an asynchronous function named `deleteContent`. This function takes an object as an argument, which includes a request (`req`) and a `confluenceClient`. The request body is expected to be of type `DeleteContentRequestBody` and it should contain the content to be deleted. The function then calls the `archivePage` method of the `confluenceClient` with the `content_id` of the content to be deleted. 

This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It is a utility module that provides a function for deleting content in a Confluence page.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/get-available-spaces.ts

```
The code does not start an application server. It is a module that exports a single asynchronous function called `getAvailableSpaces`. This function takes an object as an argument, which should contain a `res` property (an Express.js response object) and a `confluenceClient` property (a client for interacting with the Confluence API).

The function uses the `confluenceClient` to asynchronously fetch a list of spaces from the Confluence API. It then constructs a response body object, which includes these spaces under the key `confluence_spaces`. Finally, it sends this response body back to the client as a JSON response.
```

```json
[
  "confluence"
]
```

## apps/confluence/src/api/update-content.ts

```
The code in the file `update-content.ts` is not starting an application server. Instead, it exports a single asynchronous function `updateContent`. This function is designed to handle HTTP requests in an Express.js application, specifically requests to update content on a Confluence page.

The function takes an object as an argument, which includes the HTTP request and response objects (`req` and `res`), and a `confluenceClient` object for interacting with the Confluence API.

The function first retrieves the page to be updated using the `confluenceClient`. If the page doesn't exist, it logs an error and sends a 500 status response.

If the page does exist, it retrieves the existing body of the page and the new body from the request. If there is an existing body, it constructs a prompt for merging the existing and new content. It then checks which OpenAI model to use based on the token count of the prompt.

If a suitable model is found, it uses an authenticated OpenAI client to create a chat completion with the prompt. If the OpenAI response indicates that it was unable to merge the documents, it logs a warning and uses the new content as is. If the prompt is too big for OpenAI, it logs a warning and overwrites the document.

Finally, it uses the `confluenceClient` to update the page with the new or merged content, constructs a response body, and sends it as a JSON response.
```

```json
[
  "confluence",
  "openai"
]
```

## apps/confluence/src/api

```
confluence_server
```

## apps/confluence/src

```
confluence_server
```

## apps/confluence

```
confluence_server
```

## apps/marketing/package.json

```
This is a package.json file, which is a manifest file that's used to manage project dependencies in a Node.js application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The "engines" field specifies the versions of Node and npm that this project is compatible with. The "type" field indicates that this project uses ES6 modules.

The "scripts" field is currently empty, but it's typically used to define script commands that can be run from the command line.

The "dependencies" field lists the libraries that the project needs to run. These include various React libraries, Material-UI for user interface components, classnames for conditionally joining classNames together, email-validator for validating email addresses, react-cookie for handling cookies in React applications, and uuid for creating unique identifiers.

The "devDependencies" field lists the libraries that are needed for development but not for running the application. These include Babel for transpiling ES6 code to ES5, eslint for linting, webpack for bundling the application's assets, and various loaders and plugins for handling different types of files and code. The "@eave-fyi/es-config" dependency appears to be a local file used for configuration.
```

```json
[]
```

## apps/marketing/webpack.config.cjs

```
This JavaScript file is a configuration for Webpack, a static module bundler for modern JavaScript applications. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The configuration is set to development mode and specifies the entry point of the application to be the index.js file in the eave/marketing/js directory. It uses 'eval-source-map' as its devtool which provides a way of mapping the code within a compressed file back to its original position in a source file which helps in debugging.

The output of the webpack process will be placed in the eave/marketing/static/dist directory. 

The module rules specify how different types of files should be processed:
- JavaScript and JSX files are transpiled using Babel with the env and react presets.
- CSS files are processed using style-loader and css-loader.
- Image files (png, jpg, jpeg, gif) are processed using file-loader.

The devServer configuration is currently not used in development. If it were, it would serve static files from the eave/marketing/static directory over HTTP and disable client-side overlay.
```

```json
[]
```

## apps/marketing/eave/marketing/app.py

```
This Python script is a Flask application server for a web application. It imports various modules and sets up several routes for handling HTTP requests.

The script starts by importing necessary modules and setting the time to UTC. It then creates a Flask application instance and sets its secret key.

The script defines several routes:

- "/status" returns a JSON payload indicating the status of the application.
- "/_ah/warmup", "/_ah/start", and "/_ah/stop" are used for application warmup, start, and stop operations respectively.
- "/authcheck" checks the authentication state of the user based on cookies.
- "/dashboard/me/team" retrieves the authenticated user's team integrations.
- "/dashboard/me/team/destinations/confluence/spaces/query" retrieves available spaces for Confluence, a team collaboration software.
- "/dashboard/me/team/destinations/confluence/upsert" updates or inserts a new Confluence destination.
- "/dashboard/logout" logs out the user by deleting authentication cookies.
- A catch-all route serves a single page application (SPA) and sets tracking cookies.

The script also defines helper functions for rendering the SPA, cleaning responses, and creating JSON responses.
```

```json
[
  "confluence"
]
```

## apps/marketing/eave/marketing/config.py

```
The code in this file does not start an application server. Instead, it defines a configuration class for an application, presumably a web application given the presence of web session encryption keys and asset base paths.

The AppConfig class is a subclass of EaveConfig from the eave.stdlib.config module. It sets the eave_origin attribute to EaveOrigin.eave_www, which seems to be a constant from the eave.stdlib.eave_origins module.

The AppConfig class has two properties: asset_base and eave_web_session_encryption_key. The asset_base property returns the value of the EAVE_ASSET_BASE environment variable if it exists, otherwise, it defaults to "/static". 

The eave_web_session_encryption_key property is a cached property, meaning its value is computed once and then stored for future use. It returns the value of the EAVE_WEB_SESSION_ENCRYPTION_KEY environment variable. If the application is in development mode, it defaults to "dev-encryption-key". Otherwise, it retrieves the key as a secret, presumably from a secure storage.

At the end of the file, an instance of AppConfig is created and assigned to the app_config variable.
```

```json
[]
```

## apps/marketing/eave/marketing/templates/index.html.jinja

```
This code is a Jinja template for a HTML file. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The template is used to generate the main index page of a web application. It includes several scripts and meta tags in the head section of the HTML document. 

The scripts include a data layer for Google Tag Manager, a script for Google Fonts, and a main JavaScript file that is deferred until the page has finished parsing. 

The meta tags provide information about the webpage such as its character encoding, viewport settings, description, and title. The title is set to a variable `page_title` with a default value of "Eave, for your information."

The body of the document contains a noscript tag to inform users that JavaScript is required to run the application, and a div with an id of "root" where the main application will likely be mounted.

The template also includes conditional rendering of Google Tag Manager scripts based on whether analytics are enabled or not. This is determined by the `analytics_enabled` variable. 

The template uses several variables (`cookie_domain`, `api_base`, `asset_base`, `page_title`, `analytics_enabled`) which are expected to be provided when rendering the template.
```

```json
[
  "google_tag_manager",
  "google_fonts"
]
```

## apps/marketing/eave/marketing/templates

```
sentinel
```

## apps/marketing/eave/marketing/js/App.js

```
This JavaScript file is part of a React application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file imports various modules and components from different libraries and local files. It uses the React Router library for routing, the react-cookie library for handling cookies, and the Material-UI library for theming and CSS baseline. It also uses the react-helmet library for managing changes to the document head.

The App component is defined as a class component which renders a component tree that includes a CookiesProvider, an AppStoreProvider, a ThemeProvider, and a Router. Inside the Router, different routes are defined for different paths ("/terms", "/privacy", "/dashboard", and "/"). The default route redirects to the home page ("/").

The App component is then exported as a default export, wrapped with the withCookies higher-order component from the react-cookie library. This allows the App component to have access to cookies.
```

```json
[]
```

## apps/marketing/eave/marketing/js/asset-helpers.js

```
This JavaScript file does not start an application server. Instead, it exports two helper functions, imageUrl and jsUrl, which are used to generate URLs for image and JavaScript assets respectively. These functions take a filename as an argument and return a string that represents the URL of the asset. The base URL for the assets is retrieved from window.eave.assetBase.
```

```json
[]
```

## apps/marketing/eave/marketing/js/index.js

```
This JavaScript file is using React, a popular JavaScript library for building user interfaces. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The code imports the React library, the ReactDOM library (specifically the client-side version), and an App component from a local file named 'App.js'. 

It then gets a DOM element with the id 'root' and creates a root React container at that element using ReactDOM.createRoot(). After that, it renders the imported App component into this root container. 

In summary, this code is responsible for rendering a React application into a specified DOM element on a webpage.
```

```json
[]
```

## apps/marketing/eave/marketing/js/constants.js

```
This JavaScript file does not start an application server. Instead, it exports several constants that are likely used throughout a web application. These constants include a URL for feedback, header and footer dimensions for both mobile and desktop views, image sources and alt text for various affiliate and integration logos, and modal states for authentication. The image sources are generated using a function imported from another file, 'asset-helpers.js'.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Footer/index.jsx

```
This file does not start an application server. It is a React component file that defines the Footer component of a web application. 

The Footer component is styled using the makeStyles function from the Material-UI library. The styles are defined in the makeClasses constant, which includes styles for different elements of the Footer component such as the outer and inner containers, copyright text, and links.

The Footer component itself is a functional component that returns a footer element. Inside this footer, there is a Copy component (imported from '../Copy/index.jsx') that wraps around copyright text and two Link components (from the react-router-dom library) that link to the Terms and Privacy Policy pages of the website.

The copyright text includes the current year, which is obtained by creating a new Date object and calling its getFullYear method. 

The Footer component is then exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Footer

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Copy/index.jsx

```
This code is a React component named "Copy" that is used to render text with different styles based on the "variant" prop. The component uses Material-UI's makeStyles hook to create CSS classes for different text styles (h1, h2, h3, footnote, pSmall, p, bold). 

The component takes in four props: children (the content to be displayed), className (additional CSS classes), variant (the text style), and bold (a boolean indicating whether the text should be bold). 

Based on the "variant" prop, the component will render different HTML elements (h1, h2, h3, or p) with the corresponding CSS classes. If the "bold" prop is true, the "bold" class will be added. If the "className" prop is provided, it will also be added to the class list.

This file does not start an application server. It is a component file meant to be used within a React application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Copy

```
sentinel
```

## apps/marketing/eave/marketing/js/components/EaveLogo/index.jsx

```
The code is a React component for a logo. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file imports necessary modules and then defines a set of classes using the makeStyles function from Material-UI. These classes are used to style the logo and its wrapper.

The EaveLogo component itself is a functional component that takes a className as a prop. It uses the makeClasses function to generate the classes for styling, and the classNames function to combine these with any additional classes passed in through the className prop.

The component returns a Link element (from react-router-dom) that navigates to the root ("/") when clicked. The text of the link is "eave", with "Beta" appearing below it in smaller text. The "eave" and "Beta" text are styled according to the classes defined earlier.

Finally, the EaveLogo component is exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/EaveLogo

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Header/index.jsx

```
The code is a React component for a header of a web application. It does not start an application server. 

The header component uses Material UI for styling and components such as IconButton and Drawer. It also uses custom hooks `useAuthModal` and `useUser` to manage authentication state and user data. 

The header component has a logo, a hamburger menu icon for mobile view, and different buttons depending on whether the user is authenticated or not. If the user is authenticated, the header shows "Send Feedback" and "Log Out" buttons. If the user is not authenticated, it shows "Log In" and "Get Early Access" buttons.

The header also has a Drawer component from Material UI that opens when the hamburger menu icon is clicked. This drawer contains the same buttons as the header but in a mobile-friendly layout.

The `simpleHeader` prop can be passed to the Header component to render a simplified version of the header without the buttons and the hamburger menu icon.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Header

```
sentinel
```

## apps/marketing/eave/marketing/js/components/hoc/withTitle.js

```
This JavaScript file is a Higher Order Component (HOC) in React, named withTitle. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The withTitle function takes another component (WrappedComponent) as its argument and returns a new component (ComponentWithTitle). This new component sets the document's title to the value of the pageTitle prop if it's provided, otherwise it defaults to 'Eave, for your information.' 

The new component then renders the WrappedComponent, passing all the original props to it. This is a common pattern in React for reusing component logic. The eslint-disable-next-line comment is used to prevent the linter from throwing an error about the use of the spread operator to pass props.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/hoc

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Block/index.js

```
This JavaScript file is a React component named 'Block'. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The Block component takes in three props: classes, copy, and img. It renders a div with a class name from the classes prop. Inside this div, it renders an image with the source and alt text from the img prop. It also renders a 'Copy' component with the copy prop as its children.

The styles constant is a function that returns an object containing CSS styles. These styles are applied to the Block component using the withStyles higher-order component from Material-UI.

The styles are responsive and change based on the screen size. For example, on screens larger than 'sm' size, the block style changes to have a left text alignment, display flex, align items center, and other properties.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Block

```
sentinel
```

## apps/marketing/eave/marketing/js/components/AuthUser/index.jsx

```
This JavaScript file is a React component named AuthUser. It does not start an application server. 

The component uses Material-UI for styling and a CircularProgress component for displaying a loading spinner. It also uses a custom hook, useUser, to get the user's authentication state and a function to check the user's authentication state.

The makeStyles function from Material-UI is used to create CSS classes for the component. The loader class is used to style a div that will cover the entire viewport and center the CircularProgress component.

The useEffect hook is used to call the checkUserAuthState function when the component mounts if the user's authentication state is null. 

If the user's authentication state is null, the component renders a div with the CircularProgress component. If the user's authentication state is not null, it renders its children. This means that this component is used to protect other components or routes that should only be accessible to authenticated users.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/AuthUser

```
sentinel
```

## apps/marketing/eave/marketing/js/components/PrivateRoutes/index.jsx

```
This code is a React component named PrivateRoutes. It does not start an application server. It uses the react-router-dom library to handle routing in a React application. 

The component uses a custom hook, useUser, to get the current user state. If the user is authenticated (i.e., logged in), it renders the Outlet component, which is a placeholder where child routes can render their content. If the user is not authenticated, it redirects the user to the home page ("/"). 

This component is used to protect certain routes in the application, ensuring that only authenticated users can access them.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/PrivateRoutes

```
sentinel
```

## apps/marketing/eave/marketing/js/components/AuthModal/index.jsx

```
The code is a React component named `AuthModal` from a marketing application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The `AuthModal` component is a modal dialog box that provides a user interface for authentication. It uses Material UI's Dialog and IconButton components, along with custom components like Copy, Button, and various Icons. The modal can be in either login mode or sign-up mode, which changes the text and functionality displayed.

The component uses a custom hook `useAuthModal` to manage its state, including whether it's open, whether it's in login or sign-up mode, and a function to close the modal. 

The modal contains a close button, a header that changes based on the mode, a subheader with additional information, and a button to continue with Google for authentication. There's commented-out code for a similar button for Slack authentication. If the modal is in sign-up mode, it also includes a disclaimer with links to the terms of service and privacy policy.

The component uses Material UI's makeStyles function to define CSS classes for its elements. The styles are responsive and adjust based on the screen size.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/AuthModal

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Button/index.jsx

```
This JavaScript file defines a Button component using React, a popular JavaScript library for building user interfaces. The Button component is styled using Material-UI, a popular React UI framework. The file does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The Button component takes several props including children (the content of the button), className (additional CSS classes), lg (a flag for large size), color, variant, to (a link for the button to navigate to), target (where to open the link), and any other props that are passed in.

The makeStyles function from Material-UI is used to define custom styles for the button. These styles include different sizes (root and large) and a link style.

The component first creates a MaterialButton with the appropriate classes, color, variant, and target. If the 'to' prop is provided, the button is wrapped in a Link component from react-router-dom, which will navigate to the provided 'to' prop when clicked. If 'to' is not provided, the button is returned as is.

The Button component is then exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Button

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Icons/DownIcon.js

```
The code defines a React component named DownIcon. This component renders an SVG image of a downward arrow. The color of the arrow can be customized by passing a 'stroke' prop, and if no color is provided, it defaults to black. The component also accepts a 'className' prop to allow for custom styling. The file does not start an application server like Express, Flask, Django, Gin, Rack, etc.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/CloseIcon.js

```
This JavaScript file is a React component for a close icon. The CloseIcon class extends the React.Component class and has a render method that returns an SVG element. The SVG element represents a close icon (an "X" shape) and its properties such as className, width, height, and viewBox are defined. It also contains two path elements that define the shape of the "X". The stroke color of the paths can be passed as a prop, and if not provided, it defaults to black. The file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/LockIcon.js

```
The code defines a React component called LockIcon. This component does not start an application server. It returns a SVG (Scalable Vector Graphics) that represents a lock icon. The icon's appearance can be customized through properties passed to the component, such as className, stroke, lockFill, and circleFill. The className property is used to apply CSS styles to the SVG element. The stroke property defines the color of the outline of the lock. The lockFill property defines the fill color of the lock body, and the circleFill property defines the fill color of the circle in the lock. If these properties are not provided, default colors are used. The component is exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/HamburgerIcon.js

```
This JavaScript file defines a React component called HamburgerIcon. This component renders an SVG image of a hamburger icon (commonly used in web design for a menu button). The color of the lines in the icon can be customized via the 'stroke' prop, and if no color is provided, it defaults to black. The component also accepts a 'className' prop to apply CSS classes. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/GoogleIcon.jsx

```
This code defines a React component called GoogleIcon. This component returns an SVG (Scalable Vector Graphics) that represents the Google logo. The SVG is defined with a specific width, height, and viewbox. The SVG consists of multiple paths, each with a specific fill color and transformation, which together form the Google logo. 

The GoogleIcon component accepts a prop called className, which is applied to the SVG element. This allows for custom styling of the icon from outside the component.

This file does not start an application server like Express, Flask, Django, Gin, Rack, etc. It's just a React component for rendering an icon.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/PurpleCheckIcon.jsx

```
This file does not start an application server. It is a React component that defines a purple check icon. The icon is created using SVG and the color of the icon is defined by the stroke property. The shape of the icon is defined by the 'd' attribute of the 'path' element. The component receives a 'className' prop which is applied to the SVG element, allowing for external styling. The component is exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/DocumentIcon.js

```
The code is a JavaScript file that uses React, a popular JavaScript library for building user interfaces
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/SlackIcon.jsx

```
This file does not start an application server. It is a React component that renders an SVG icon of the Slack logo. The SlackIcon function takes a className as a prop and applies it to the SVG element. The SVG paths and groups are used to create the different parts of the Slack logo with different colors. The component is then exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/ConnectIcon.js

```
The code is a React component that defines an SVG icon. The icon is named "ConnectIcon" and it is exported at the end of the file to be used in other parts of the application. The icon's appearance is defined by a series of path elements within the SVG. The color of the icon is set to be the current color of the text in its environment (currentColor). This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/AtlassianIcon.jsx

```
This code defines a React component that renders an SVG icon of the Atlassian logo. The component takes a `className` prop which can be used to apply CSS styles to the icon. The SVG itself is quite complex, containing multiple `path` elements that define the shape and color of the logo. The file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/SnapIcon.js

```
The code defines a React component called SnapIcon. This component renders an SVG image when it is included in a React application. The SVG image is defined by a series of path elements within the SVG element. The color of the SVG image is set to the current color of the text in the parent element. The component also accepts a className prop which can be used to apply CSS styles to the SVG image. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/ConfluenceIcon.jsx

```
This code defines a React component named `ConfluenceIcon` that renders an SVG icon. The SVG icon is defined with two linear gradients and two paths. The `className` prop is passed to the SVG element's `className` attribute, allowing for custom styling from the parent component. The component is then exported for use in other parts of the application. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/ChatboxIcon.jsx

```
This code defines a React component called `ChatboxIcon` that renders an SVG image of a chatbox icon. The SVG image is defined with specific paths and styles. The component accepts a `className` prop which can be used to apply additional CSS styles to the SVG element. The `ChatboxIcon` component is then exported for use in other parts of the application. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons/SyncIcon.js

```
This JavaScript file is a React component that defines a SyncIcon. This icon is represented as an SVG (Scalable Vector Graphics) image. The file does not start an application server. It simply exports the SyncIcon component which can be imported and used in other parts of a React application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Icons

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard/StepIcon.jsx

```
This code defines a React component called `StepIcon` that is used to display a step in a process. The component uses Material-UI's `makeStyles` function to define CSS styles for the step and a purple check icon. The styles are responsive and change based on the screen size (with different styles for screens wider than 'md' or medium size).

The `StepIcon` component takes a `props` object as an argument. If the `completed` property of `props` is `true`, it displays a purple check icon inside the step.

This file does not start an application server. It is a component file that exports a single React component, which can be imported and used in other parts of a React application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard/Steps.jsx

```
The code is a React component named "Steps" that is part of a marketing dashboard. It does not start an application server. 

The component is responsible for guiding the user through a series of steps to set up the Eave application. The steps include adding Eave to Atlassian, connecting to the user's Confluence account, selecting a Confluence space, and integrating business tools such as GitHub, Slack, and Jira. 

The component uses Material-UI for styling and layout, including components like Stepper, Step, StepLabel, StepContent, Button, and Select. It also uses custom hooks and components for user-related operations and displaying specific icons. 

The state of the component is managed using React's useState and useEffect hooks. The state includes the current step, the selected Confluence space, whether the user is editing the space, and whether the user has clicked on certain buttons. 

The component also contains several event handlers for button clicks and select changes. These handlers update the state and call functions from the useUser hook to perform actions like updating the Confluence space. 

The render method of the component returns a section containing a series of steps with labels, content, and buttons for each step. The steps are wrapped in a Stepper component for vertical orientation. The Footnote component is displayed at the end.
```

```json
[
  "atlassian",
  "confluence",
  "github",
  "slack",
  "jira"
]
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard/Thanks.jsx

```
The code is a React component named "Thanks" that is used to display a thank you message to users who have signed up. It uses Material-UI for styling. The component displays a heading saying "Thanks for Signing Up!" and a paragraph informing the user that they have been added to the waitlist and will be notified via email when availability opens up. It also provides an email link for inquiries. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard/Footnote.jsx

```
This JavaScript file, Footnote.jsx, is a React component that defines a footer section for a webpage. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The component uses Material-UI for styling and defines some custom styles using the makeStyles hook from Material-UI. The styles are responsive and change based on the screen size (breakpoints).

The footer section contains a chat icon (ChatboxIcon) and two text blocks (Copy components). The text blocks contain a message from the Eave team and a request for feedback from users. The feedback can be submitted through a form (the URL is stored in the FEEDBACK_URL constant) or by sending an email to info@eave.fyi.

The component is exported as a default export, meaning it can be imported in other files using any name.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard/index.jsx

```
This is a React component file for a Dashboard page. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The Dashboard component uses several hooks and components:

- `useUser` hook: This custom hook is used to manage user-related data and operations. It provides user state, a loading state for getting user info, a function to get user info, and any error that might occur during the process.
- `useEffect` hook: This built-in React hook is used to perform side effects in function components. In this case, it's used to fetch user info when the component mounts and whenever the `teamInfo` changes.
- `makeStyles` hook: This is a hook from Material-UI library used to define CSS classes in JavaScript.
- `CircularProgress` component: This is a Material-UI component that displays a circular loading spinner.
- `Page`, `PageSection`, `Thanks`, `Steps`, and `Copy` components: These are custom components used to structure the page.

The Dashboard component renders a `Page` component that contains a `PageSection`. Inside the `PageSection`, it conditionally renders different components based on the state of the user info:

- If the user info is not available or is still loading, it displays a loading spinner or an error message.
- If the user info is available and the team is not in beta whitelist, it displays a `Thanks` component.
- If the user info is available and the team is in beta whitelist, it displays a `Steps` component.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/Dashboard

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Pages/PrivacyPage/index.jsx

```
This JavaScript file is a React component for a Privacy Policy page. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The file imports necessary dependencies and components, including React, makeStyles from Material-UI for styling, a HEADER constant, and two components: Page and Copy. 

The makeStyles function is used to define CSS classes for the component. 

The PrivacyPage component is a functional component that uses these classes to style its elements. It returns a Page component with a simpleHeader prop and a main element containing several Copy components. These Copy components display the text of the privacy policy, including sections on information collection, usage, sharing and disclosure, data security, user rights and choices, policy changes, and contact information.

Finally, the PrivacyPage component is exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/PrivacyPage

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Pages/Page/index.jsx

```
This JavaScript file is a React component named 'Page'. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file imports the React library, a function called makeStyles from the @material-ui/styles library, and three other components: Header, Footer, and AuthModal.

The makeStyles function is used to create a CSS-in-JS styling solution. It defines a class called 'container' with several CSS properties.

The Page component is a functional component that accepts 'children' and 'simpleHeader' as props. It uses the makeStyles function to create a classes object and uses it to apply styles to the div that wraps the entire component. Inside this div, it renders the Header, Footer, and AuthModal components and any children passed to it.

The Page component is then exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/Page

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Pages/HomePage/index.jsx

```
This code defines the HomePage component in a React application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The HomePage component uses several hooks and components:

- The `useUser` hook is used to get the user's state, particularly whether the user is authenticated or not.
- The `useNavigate` hook from `react-router-dom` is used to programmatically navigate to different routes in the application.
- The `Hero`, `DocumentationBanner`, `IntegrationsBanner`, `SlackBanner`, `PrivacyBanner`, and `Page` components are used to structure the content of the HomePage.

The `copy` object contains the text that will be displayed in the different components of the HomePage.

The `useEffect` hook is used to redirect authenticated users to the '/dashboard' route.

The HomePage component returns a JSX structure that includes all the aforementioned components, passing them their respective props from the `copy` object.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/HomePage

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Pages/TermsPage/index.jsx

```
This code is a React component for a Terms of Service page. It doesn't start an application server like Express, Flask, Django, Gin, Rack, etc. 

The component uses Material-UI's makeStyles hook to define CSS styles for the page. The styles are responsive and adjust based on the screen size (mobile, tablet, desktop). 

The TermsPage component renders a Page component with a simpleHeader prop. Inside the Page component, it renders a main section with various Copy components. Each Copy component represents a section of the terms of service, such as "Use of Services", "User Accounts", "Fees", "Intellectual Property", "Disclaimer of Warranties", "Limitation of Liability", "Indemnification", "Termination", "Governing Law", "Changes to Terms", and "Contact Us". 

Each section of the terms of service is styled with the classes defined earlier. The email address at the end is a clickable link that opens the user's default email client to send an email to info@eave.fyi.

The TermsPage component is exported as a default export at the end of the file.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Pages/TermsPage

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Banners/PrivacyBanner/index.jsx

```
This file does not start an application server. 

This is a React component file that exports a component named PrivacyBanner. The PrivacyBanner component takes in two props: title and subtitle. It uses the makeStyles hook from the Material-UI library to create CSS classes for styling the component. 

The component returns a PageSection component with two children: an image and a div. The image uses the imageUrl helper function to get the source URL for the image. The div contains two Copy components, which are likely text components, that display the title and subtitle props.

The styling of the component is responsive, with different styles applied at different viewport sizes (breakpoints). For example, the flexDirection of the wrapper changes from 'column' to 'row' at the 'md' breakpoint.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Banners/PrivacyBanner

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Banners/DocumentationBanner/index.jsx

```
This code defines a React component named `DocumentationBanner` that is used to display a banner with a title, subtitle, and an image. The image displayed is responsive and changes based on the width of the viewport. 

The component uses Material-UI's `makeStyles` function to define CSS styles for the banner. The styles are responsive and change based on the viewport's width. 

The `DocumentationBanner` component uses two other components, `Copy` and `PageSection`, which are imported from other files in the same project. The `Copy` component is used to display the title and subtitle of the banner, and the `PageSection` component is used to structure the layout of the banner.

The `imageUrl` function is imported from an asset helper file and is used to generate the URLs for the images displayed in the banner.

This code does not start an application server. It is a component of a React application, which is a client-side JavaScript library for building user interfaces.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Banners/DocumentationBanner

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Banners/IntegrationsBanner/index.jsx

```
This code defines a React component called IntegrationsBanner. The component displays a section of a page with a title, subtitle, and logos for Slack, GitHub, and Jira. The logos are imported from a constants file. The component uses Material-UI's makeStyles hook for styling, which allows for responsive design based on different screen sizes (breakpoints). The styles are applied to the wrapper, copy, logos, and each individual logo. The IntegrationsBanner component is exported for use in other parts of the application. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Banners/IntegrationsBanner

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Banners/SlackBanner/index.jsx

```
This file does not start an application server. 

The file is a React component for a banner that appears to be used for marketing purposes. It uses Material-UI for styling and classNames for combining multiple styles. The banner is designed to be responsive, with different layouts and padding depending on the screen size (breakpoints are defined for medium 'md' and large 'lg' screens). 

The banner contains an image (with different sources depending on screen size) and two sections of copy text (titles and subtitles). The text and image are arranged in a grid layout, with the image and text sections swapping places on larger screens. 

The SlackBanner component receives two props: titles and subtitles, which are arrays. The first elements of these arrays are used in the upper copy section, and the second elements are used in the lower copy section. The Copy component is used to render the text, with different variants ('h2' for titles and 'pSmall' for subtitles). 

The imageUrl function is used to generate URLs for the images. The image sources are set to be different depending on the screen width, with a smaller image used for screens up to 599px wide, and a larger image used for screens 600px wide or larger.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Banners/SlackBanner

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Hero/index.jsx

```
This code defines a React component named "Hero". It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The Hero component takes three props: title, subtitle, and cta (call to action). It uses the makeStyles hook from Material-UI to create CSS classes for the title and subtitle. The CSS classes define the margin-bottom and max-width properties for different screen sizes.

The component uses a custom hook called useAuthModal to get a function named openModal. This function is used to open an authentication modal when the button in the Hero component is clicked. The button's text is the cta prop.

The Hero component returns a PageSection component with a Copy component for the title and subtitle, and a Button component for the call to action. The Copy and Button components are also custom components imported from other files.

The Hero component is exported as a default export at the end of the file.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Hero

```
sentinel
```

## apps/marketing/eave/marketing/js/components/PageSection/index.jsx

```
This code defines a React component named `PageSection`. This component is used to create a section of a webpage with certain styles and properties. The styles are defined using Material-UI's `makeStyles` function, which creates a hook that can be used to generate class names for the CSS classes defined within it. 

The `PageSection` component accepts several props: `children`, `alternateBackground`, `topSection`, `sectionClassName`, `wrapperClassName`, and `id`. These props are used to customize the behavior and appearance of the section. 

The `children` prop is used to pass in the content of the section. The `alternateBackground` prop, if true, applies a dark background color to the section. The `topSection` prop, if true, adds extra padding to the top of the section. The `sectionClassName` and `wrapperClassName` props are used to apply additional CSS classes to the section and its wrapper, respectively. The `id` prop is used to assign an ID to the section.

The code does not start an application server. It is just a component file in React.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/PageSection

```
sentinel
```

## apps/marketing/eave/marketing/js/components/Affiliates/index.js

```
The code is a React component that displays a section with affiliate logos. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The component, named Affiliates, renders a div that contains a Copy component and a div with affiliate logos. The Copy component displays the text "Trusted by employees from". The div with logos contains four images, each representing a logo of an affiliate: Amazon, PayPal, Disney, and Honey. The source and alt text for these images are imported from a constants file.

The component uses Material-UI's withStyles function to apply styles to the elements. The styles are responsive, with different values for screen widths at or above the 'sm' (small) breakpoint. The styles control the layout of the logos (displayed as a flex container), their alignment, spacing, and specific dimensions.

The Affiliates component is exported as the default export from this module, with the styles applied.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/Affiliates

```
sentinel
```

## apps/marketing/eave/marketing/js/components/BlockStack/index.js

```
The code is a React component named BlockStack. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

This component uses Material-UI's withStyles function for styling. It imports two other components: Copy and Block. 

In the render method, it destructures classes, title, and blocks from this.props. It then returns a section element with a className of classes.section. Inside this section, it uses the Copy component to display a title, and maps over the blocks array to display a series of Block components.

The styles object defines CSS styles for the component. It uses theme breakpoints to apply different styles for different screen sizes. The styles are then passed to the withStyles function from Material-UI and applied to the BlockStack component before it is exported.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/BlockStack

```
sentinel
```

## apps/marketing/eave/marketing/js/components/ScrollToTop/index.jsx

```
This code defines a React component named ScrollToTop. It uses the useLocation hook from react-router-dom to get the current location's pathname. The useEffect hook is used to execute the window.scrollTo(0, 0) function whenever the pathname changes. This function scrolls the window view to the top. The component does not render anything, it returns null. This file does not start an application server.
```

```json
[]
```

## apps/marketing/eave/marketing/js/components/ScrollToTop

```
sentinel
```

## apps/marketing/eave/marketing/js/hooks/useAuthModal.js

```
The code defines a custom React hook called `useAuthModal` that provides functionality related to an authentication modal. This hook uses the `useContext` hook from React to access the `authModal` state from the `AppContext`. 

The `useAuthModal` hook returns an object with several properties and methods:

- `modalState`: The current state of the authentication modal.
- `setModalState`: A function to update the state of the authentication modal.
- `isOpen`: A boolean indicating whether the modal is currently open.
- `openModal`: A function that opens the modal and optionally sets its mode (e.g., login or signup).
- `closeModal`: A function that closes the modal.
- `isLoginMode`: A boolean indicating whether the modal is currently in login mode.
- `isSignupMode`: A boolean indicating whether the modal is currently in signup mode.

The file does not start an application server. It is a JavaScript module that exports a single function, `useAuthModal`.
```

```json
[]
```

## apps/marketing/eave/marketing/js/hooks/useUser.js

```
The code is a custom React Hook called `useUser` that provides user-related state and functions to components that use it. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The hook uses the `useContext` hook to access the user state from the `AppContext` and the `useState` hook to manage local state for available spaces, errors, and loading states for various operations.

The hook returns an object with the following properties:

- `userState` and `setUserState`: The current user state and a function to update it.
- `availableSpaces`: The available spaces for the user.
- `loadingGetUserInfo`, `loadingAvailableSpaces`, and `loadingUpdateConfluenceSpace`: Flags indicating whether the corresponding operations are in progress.
- `getUserError` and `updateConfluenceError`: Errors that occurred during the corresponding operations.
- `checkUserAuthState`: A function that checks whether the user is authenticated.
- `getUserInfo`: A function that fetches the user's team information.
- `loadAvailableSpaces`: A function that fetches the available spaces for the user.
- `updateConfluenceSpace`: A function that updates the current selected confluence space.
- `logOut`: A function that logs the user out.

All the fetch operations are performed against endpoints on the same domain as the current page. The responses are expected to be in JSON format. Errors during fetch operations are logged to the console.
```

```json
[]
```

## apps/marketing/eave/marketing/js/hooks/useError.js

```
This code does not start an application server. It is a JavaScript file that exports a custom React Hook called useError. This hook is used to access and manipulate the error state from the AppContext, which is a React Context.

The useError hook uses the useContext React Hook to access the error state from the AppContext. It then destructures the error state into errorState and setErrorState. errorState is the current state of the error, and setErrorState is a function that can be used to update the error state.

The hook then returns an object containing errorState and setErrorState, which can be used by components that use this hook to read and update the error state.
```

```json
[]
```

## apps/marketing/eave/marketing/js/hooks

```
sentinel
```

## apps/marketing/eave/marketing/js/context/Provider.js

```
This JavaScript file is part of a React application and it does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The file defines a context provider for the application. Context provides a way to pass data through the component tree without having to pass props down manually at every level. 

The `AppContextProvider` component maintains three pieces of state: `modalState`, `userState`, and `errorState`. These states are initialized with `useState` and stored in the `store` object. 

The `modalState` is used to control the visibility and mode of an authentication modal. The `userState` is used to keep track of whether a user is authenticated and their team information. The `errorState` is used to store any error that occurs.

The `store` object is then passed as a value to the `AppContext.Provider` component, which makes it available to all child components. This means that any child component can access and update the `modalState`, `userState`, and `errorState`. 

The `children` prop is rendered inside the `AppContext.Provider`, which means that all child components will have access to the context.
```

```json
[]
```

## apps/marketing/eave/marketing/js/context

```
sentinel
```

## apps/marketing/eave/marketing/js/theme/index.js

```
This JavaScript file is part of a marketing application and it is used to define the theme for the application's user interface. It does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file uses the 'createTheme' function from the '@material-ui/core' library to create a theme. The theme includes color palettes for primary colors and background colors, typography colors, and font family. 

The primary color palette includes a main color and a darker variant. The background color palette includes main, dark, and secondary colors. 

The typography color palette includes light, main, dark, inactive, and link colors. The font family is set to 'DM Sans' and 'sans-serif'. 

The created theme is then exported for use in other parts of the application.
```

```json
[]
```

## apps/marketing/eave/marketing/js/theme

```
sentinel
```

## apps/marketing/eave/marketing/js

```
sentinel
```

## apps/marketing/eave/marketing

```
eave_marketing_server
```

## apps/marketing

```
sentinel
```

## apps/archer/eave/archer/main.py

```
The code is a Python script that uses asyncio for asynchronous I/O. It does not start an application server like Express, Flask, Django, Gin, or Rack.

The script imports several modules and functions from the 'eave.archer' package and the 'eave.stdlib' package. It defines an asynchronous function 'run' that takes an 'OpenAIModel' object as an argument and does not return anything. Inside this function, it creates a 'Service' object, a 'GithubContext' object, and builds a file system hierarchy. It then performs a chained query on the file contents. The function also writes run information.

In the main part of the script, it sets up an argument parser to get command-line arguments, specifically the '--model' argument which defaults to 'OpenAIModel.GPT4.value'. It then creates an 'OpenAIModel' object using the value of the '--model' argument and runs the 'run' function with this model as an argument.
```

```json
[
  "openai",
  "github"
]
```

## apps/archer/eave/archer/graph_builder.py

```
The code does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

This Python script is part of a larger application, possibly related to a microservices architecture. It defines a function `build_graph` that recursively builds a service graph from a file system hierarchy. 

The function takes four arguments: a file system hierarchy (`FSHierarchy`), an OpenAI model (`OpenAIModel`), a Github context (`GithubContext`), and a parent service (`Service`). 

For each file in the hierarchy, it queries the file contents using the `query_file_contents_chained` function. If the query returns a response with a service name, it creates a new `Service` instance and registers it in the `SERVICE_REGISTRY`. It then adds any API references from the file query response to the service's subgraph.

For each directory in the hierarchy, it recursively calls `build_graph` to build the service graph for the subdirectory.

The script imports several modules and functions, including chained queries, service registry, file queries, service dependencies, OpenAI client, Github context, service graph, and file system hierarchy.
```

```json
[
  "openai",
  "github"
]
```

## apps/archer/eave/archer/tree_sitter_build.py

```
The code in the file `tree_sitter_build.py` does not start an application server. Instead, it is used to build a library for the `tree-sitter` package, which is a parser generator tool and an incremental parsing library. 

The code first imports the necessary modules and sets the `_build_root` variable to a specific path in the system's environment variables. 

Then, it calls the `build_library` method from the `Language` class of the `tree-sitter` package. This method is used to compile and link a dynamic library that can be used to parse one or more languages. The method takes two arguments: the path where the library should be created and a list of paths to the language's source directories. In this case, it is building a library for TypeScript language.
```

```json
[]
```

## apps/archer/eave/archer/render.py

```
The code in this file does not start an application server. Instead, it is a Python script that is part of a larger application, likely used for managing and visualizing service dependencies within the application.

The script imports several modules and functions, including datetime, json, math, os, sys, textwrap, and typing. It also imports several custom modules and functions from the same application, including a service registry, a configuration file, a utility module, a file system hierarchy module, and a service graph module.

The script defines several functions that are used to gather services from a service graph, render subgraphs and root graphs, render file system hierarchies, and write various types of information to markdown files. These include services, file queries, dependencies, prompts, OpenAI requests, hierarchies, graphs, and run information.

The script also includes a function to create a directory based on a timestamp.

The script includes commented-out code for generating a Mermaid C4 Content diagram, which is a type of diagram used for visualizing system architecture. However, the comments note that as of July 2023, C4 diagrams in Mermaid are experimental and not viable for this use-case.

Overall, this script appears to be used for managing and visualizing service dependencies within an application, as well as writing various types of information to markdown files.
```

```json
[]
```

## apps/archer/eave/archer/service_graph.py

```
The code does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

This Python script defines classes and methods for managing a service graph in a project. The service graph is a data structure that represents the services in the project and their relationships.

The `OpenAIResponseService` class is a TypedDict that represents the structure of a service response. It has three fields: `service_name`, `service_description`, and `service_root`.

The `parse_service_response` function takes a string response and returns a list of `OpenAIResponseService` objects by parsing the JSON in the response.

The `Service` class represents a service in the project. It has several attributes including `id`, `name`, `description`, `subgraph`, `root`, and `visited`. The class also has methods to initialize an instance, get the definition of the service, and get the full root path of the service.

The `ServiceGraph` class represents a graph of services. It has a dictionary attribute `services` that maps service IDs to `Service` objects. The class also has methods to add a service to the graph, and merge another service graph into this one.
```

```json
[]
```

## apps/archer/eave/archer/util.py

```
The code in this file does not start an application server. It is a utility file in a Python application, possibly related to processing and analyzing code files from a Github repository. The file contains several utility functions for handling and manipulating file paths, file contents, and making requests to the OpenAI API.

Here's a summary of what each function does:

- `GithubContext`: A data class that holds the organization name and the repository name of a Github repository.
- `get_lang`: Returns the programming language of a file based on its extension.
- `get_filename`: Returns the base name of a file from its path.
- `clean_fpath`: Cleans up a file path by removing a specified prefix.
- `get_file_contents`: Reads the contents of a file, optionally stripping import statements. It skips files that match patterns specified in `CONTENT_EXCLUDES`.
- `remove_imports`: Removes import statements from the contents of a Python file.
- `get_tokens`: Encodes the content of a file into tokens using the specified model from OpenAI.
- `truncate_file_contents_for_model`: Truncates the contents of a file so that the number of tokens it contains does not exceed the maximum allowed by the specified OpenAI model.
- `make_prompt_content`: Joins a list of messages into a single string, separated by newlines.
- `make_openai_request`: Makes a request to the OpenAI API with the specified parameters and returns the response. It also updates a global dictionary `TOTAL_TOKENS` with the number of tokens used in the request. If the request fails due to maximum retry attempts or timeout, it returns None.
```

```json
[
  "github",
  "openai"
]
```

## apps/archer/eave/archer/service_registry.py

```
This Python code defines a class called `ServiceRegistry` which is used to manage services in an application. The `ServiceRegistry` class has two methods: `register` and `get`. The `register` method is used to add a service to the registry, while the `get` method is used to retrieve a service from the registry using its ID. 

The `ServiceRegistry` class does not start an application server like Express, Flask, Django, Gin, or Rack. It is just a utility class for managing services. 

At the end of the file, an instance of `ServiceRegistry` is created and assigned to the `SERVICE_REGISTRY` variable. This instance can be imported and used in other parts of the application.

There is also a comment indicating that the code needs to be fixed for thread safety, implying that it may not currently be safe to use in a multi-threaded environment.
```

```json
[]
```

## apps/archer/eave/archer/config.py

```
This Python script is a configuration file for an application. It does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The script imports necessary modules and sets up several constants and configurations for the application. It sets the project root directory from an environment variable "EAVE_HOME", specifies the model to be used as OpenAI's GPT4, and sets up a timestamp. 

It also creates a directory for output files, although the actual creation line is commented out. 

The script then sets up a list of files and directories to be excluded from the application's hierarchy. These exclusions range from specific directories like "node_modules" and "__pycache__" to file types like ".md" and ".txt". 

Additionally, it sets up an empty set for files that should be excluded from dependency collection but still shown in the hierarchy. 

There are also two TODO comments indicating future development tasks: automatically excluding files in gitignore and parsing HTML files to exclude SVG documents.
```

```json
[]
```

## apps/archer/eave/archer/fs_hierarchy.py

```
The Python script `fs_hierarchy.py` does not start an application server like Express, Flask, Django, Gin, Rack, etc. Instead, it defines a structure for managing a file system hierarchy. 

The script imports necessary modules and then defines two classes: `FileReference` and `FSHierarchy`. 

`FileReference` represents a file in the system with attributes like path, basename, extension, summary, and service references. It has methods to read the file and get a clean path.

`FSHierarchy` represents a directory in the file system with attributes like root, directories, files, summary, and service name. It also has a method to get a clean path.

The `build_hierarchy` function is used to create a hierarchy of the file system starting from a root directory. It recursively scans through all directories and files under the root directory (excluding those matching patterns in `EXCLUDES`), and builds up a tree-like structure using instances of `FSHierarchy` and `FileReference`. This hierarchy can be used for further processing or analysis of the file system.
```

```json
[]
```

## apps/archer/eave/archer/strategies/service_normalization.py

```
The code in the file `service_normalization.py` does not start an application server. Instead, it defines a function `normalize_services` that takes a list of service objects and an OpenAI model as input. The function prepares the services by extracting their names, descriptions, and dependencies, and then sends this data to the OpenAI model for processing. 

The OpenAI model is expected to reduce the list of services by combining similar ones. If two or more services have similar names and descriptions, they are considered duplicates and are combined into one, with their dependencies also combined. The function then parses the response from the OpenAI model, creates new service objects from the parsed data, and returns a dictionary of these new services.

The function `_normalize_service_name` is a helper function that removes parentheses from a given service name. 

The code also includes some commented-out lines that seem to be for debugging purposes, such as printing the list of services and the response from the OpenAI model.
```

```json
[
  "openai"
]
```

## apps/archer/eave/archer/strategies/file_queries.py

```
The file `file_queries.py` is part of a larger application, and it does not start an application server like Express, Flask, Django, Gin, Rack, etc.

The file appears to be part of a system that analyzes code files, specifically looking for references to external services or APIs. It uses OpenAI's GPT-4 model to generate prompts and parse responses. The prompts are designed to ask about the presence of HTTP server frameworks and external APIs in the given code.

The main function `query_file_contents` takes a file path, an OpenAI model, a Github context, and an optional parent service. It builds a prompt based on the code context in the file and sends it to the OpenAI model. The response from the model is then parsed into a JSON object and returned as a `FileQueryResponse` dataclass instance.

The file also contains helper functions to load the file content (`_load_file`), build the prompt for code context (`_build_prompt_for_code_context`), and make a request to the OpenAI model (`_make_openai_request`). 

The script also handles exceptions such as maximum retry attempts reached and timeout errors. It logs the total tokens used for prompt and completion in the OpenAI model.
```

```json
[
  "openai",
  "github"
]
```

## apps/archer/eave/archer/strategies/package_json_parsing.py

```
This Python script does not start an application server. Instead, it is a utility script that parses `package.json` files in a project hierarchy to gather information about dependencies. 

The script uses the `tree_sitter` library to parse TypeScript code and the OpenAI GPT-4 model to categorize the dependencies into four categories: internal/private package, third-party service SDK, other, and unsure. 

The script traverses the file system hierarchy starting from a root directory (`PROJECT_ROOT`), looking for `package.json` files. For each `package.json` file found, it reads the file contents and extracts the dependencies. 

Then, it sends a formatted prompt to the OpenAI API, asking it to categorize each dependency and group them into the four categories. The response from the OpenAI API is then added to a dictionary (`tree`) with the file path as the key and the categorized dependencies as the value.

Finally, the script writes this dictionary to a markdown file (`deptree.md`) in a specified output directory (`OUTDIR`), formatted as a JSON object. 

The script is designed to be run as a standalone program, with the main execution starting in the `if __name__ == "__main__":` block at the end of the script.
```

```json
[
  "openai"
]
```

## apps/archer/eave/archer/strategies/rolling_summaries.py

```
This Python script is not starting an application server. It appears to be a utility script used for analyzing and summarizing the structure and content of a project's source code files. It uses OpenAI's GPT-3 model to generate summaries of the code in each file and identify any external services or APIs referenced in the code. 

The script performs the following tasks:

1. It builds a hierarchy of the project's file system.
2. It writes a markdown file, `rolling_summaries.md`, with summaries of each file's code.
3. It generates a Graphviz dot file, `graph-gen.dot`, representing the connections between different services in the project.
4. It identifies and normalizes the names of any external services or APIs referenced in the code.
5. It determines if a directory contains a file that starts an application server and, if so, assigns a short name to the application.

The script is designed to be run asynchronously using Python's asyncio library.
```

```json
[
  "openai"
]
```

## apps/archer/eave/archer/strategies/service_info.py

```
This Python code does not start an application server. Instead, it defines a function `get_services_from_hierarchy` that is used to identify and describe public services hosted in a GitHub repository. 

The function takes as input a file system hierarchy of a repository, an OpenAI model, and a GitHub context (which includes the organization name and repository name). It then uses the OpenAI model to generate a human-readable name and description for each public service found in the repository. 

The function constructs a chat message with the OpenAI model, providing it with detailed instructions and the repository's directory hierarchy. It then sends this message to the OpenAI chat completion API, which returns a response. 

If the maximum number of retry attempts is reached without getting a response, the function prints a warning message and returns an empty list. Otherwise, it parses the response to extract information about the services, creates `Service` objects for each service, registers them in a service registry, and returns a list of these services.

The code also updates counters for the total number of tokens used in the prompt, completion, and total. It stores the parameters and answer for the "get_services" prompt in a dictionary called `PROMPT_STORE`.
```

```json
[
  "github",
  "openai_chat_completion"
]
```

## apps/archer/eave/archer/strategies/chained_queries.py

```
The Python code in the file `chained_queries.py` does not start an application server. Instead, it defines two asynchronous functions: `query_file_contents_chained` and `query_file_contents`. 

The function `query_file_contents_chained` is designed to query the contents of a specific file, `google_oauth.py`, using a given model from the OpenAI library. The function is currently commented out to process all files in a given hierarchy and all directories in the hierarchy.

The function `query_file_contents` takes a filepath and a model as input. It defines an inner asynchronous function `_do_request` that makes a request to the OpenAI API with specific parameters and processes the response. If the model is GPT4, it waits for 2 seconds before proceeding. The function then opens a markdown file, writes the cleaned filepath to it, retrieves the file contents, and truncates them for the model. It then creates a message asking to list the external services referenced in the code and sends this message to `_do_request`. The response is processed, converted from JSON, and checked for length. If it's not empty, it's returned. There are commented out lines of code that would create a formatted list of external services and send another message asking if there are any references to Google Cloud, AWS, or Azure products.
```

```json
[
  "openai"
]
```

## apps/archer/eave/archer/strategies/service_dependencies.py

```
This Python script is part of a larger application, but it does not start an application server like Express, Flask, Django, Gin, Rack, etc. 

The script defines a function `get_service_references` that takes a file path, a model, and a GitHub context as arguments. The function reads the contents of the file at the given path and checks if the file is empty or matches any patterns in `CONTENT_EXCLUDES`. If either condition is met, the function returns `None`.

If the file is not empty and does not match any patterns in `CONTENT_EXCLUDES`, the function generates a prompt for an OpenAI model. The prompt includes information about the GitHub organization and repository, the file path, and the code in the file. If there are known services in `SERVICE_REGISTRY`, these are also included in the prompt.

The function then sends a chat completion request to the OpenAI API using the generated prompt and parameters that include a model, a top_p value, and penalties for presence and frequency. The function waits for a response from the API.

If the API response is received without exceeding the maximum number of retry attempts or a timeout, the function processes the response to extract service references from the code in the file. These service references are registered in `SERVICE_REGISTRY` and added to a `ServiceGraph` object, which is returned by the function.

If the maximum number of retry attempts is reached or a timeout occurs while waiting for the API response, the function returns `None`.
```

```json
[
  "github",
  "openai"
]
```

## apps/archer/eave/archer/strategies/component_name.py

```
The provided information does not include any actual code, so it's impossible to determine what the code does, whether it sets up routes and middleware for a web application, or if it starts an application server like Express, Flask, Django, Gin, Rack, etc. Please provide the actual code for analysis.
```

```json
[]
```

## apps/archer/eave/archer/strategies

```
sentinel
```

## apps/archer/eave/archer

```
sentinel
```

