## apps/slack/socketmode.py

```
The code in the file `apps/slack/socketmode.py` defines an asynchronous Socket Mode handler for a Slack app using the Bolt framework. It imports necessary libraries and sets the time to UTC. The `AsyncSocketModeWithImmediateAckHandler` class is defined, which inherits from `AsyncSocketModeHandler`. This class overrides the `handle` function to immediately acknowledge messages from Slack, allowing the app to process messages without time constraints.

The `start_socket_mode` function is defined to start the Socket Mode handler with the Slack app and app token. If the file is run as the main module, it starts the Socket Mode handler using asyncio.

This file does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/slack_app.py

```
The code in the file `apps/slack/eave/slack/slack_app.py` defines an asynchronous Slack app using the Slack Bolt framework. It imports necessary modules and classes, defines custom exceptions, and implements an `authorize` function for handling authorization. The app is not used directly to handle incoming event requests from Slack but is used only during background processing. Several middlewares are disabled, such as Request Verification, SSL Check, and URL Verification, as they are already handled manually in the Slack Event API endpoint. The `process_before_response` option is enabled to ensure that the event is done being processed before returning a response. The app does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/event_handlers.py

```
The code is from a file called event_handlers.py in the apps/slack/eave/slack directory. It does not start an application server. The file defines event handlers for a Slack bot using the Slack Bolt library. The event handlers are registered using the register_event_handlers function, which takes an AsyncApp instance as an argument. The file contains handlers for various events such as shortcuts, messages, and member_joined_channel events. It also includes an error handler function that logs exceptions that occur during event handling.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/slack_models.py

```
The code in the file `apps/slack/eave/slack/slack_models.py` defines various classes and methods related to Slack data models, such as messages, conversations, reactions, and user profiles. It does not start an application server. The file imports several libraries, including asyncio, enum, re, and slack_sdk, among others. The main classes defined in the file are _SlackContext, SlackProfile, SlackConversationTopic, SlackConversation, SlackMessageLinkType, SlackReaction, SlackPermalink, and SlackMessage. Each class has its own set of methods and properties to handle various aspects of Slack data.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/app.py

```
The code is from a file called app.py in the apps/slack/eave/slack directory. It sets up a Starlette application server with various routes and middleware. The routes include warmup, start, stop, and Slack event processing. The server also has a graceful shutdown function to close the cache client if it's initialized.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/config.py

```
The code is a configuration file for a Slack application. It imports necessary modules and defines constants related to Slack event processing. The AppConfig class extends EaveConfig and includes properties for Slack app signing secret and socket mode token. It also has a property to check if the application is running in socket mode. The file does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/requests/warmup.py

```
The code in the file apps/slack/eave/slack/requests/warmup.py defines three classes: WarmupRequest, StartRequest, and StopRequest, which are all subclasses of HTTPEndpoint from the Starlette library. The WarmupRequest class has a get method that preloads configurations, public keys, and attempts to create a Redis connection. If the Redis connection fails, it logs an error but does not prevent the app from warming up. The StartRequest and StopRequest classes have simple get methods that return an OK response. The file does not start an application server.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/requests/event_processor.py

```
The code in event_processor.py is a part of a Slack application. It imports necessary libraries and modules, defines a class called SlackEventProcessorTask, which inherits from HTTPEndpoint. The class has an asynchronous post method that processes incoming POST requests to the /_tasks/slack-events endpoint. It checks for a valid signature, logs the request, and handles the request using the AsyncSlackRequestHandler from the slack_bolt library. The file does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[
  "slack"
]
```

```json
[
  "slack_app"
]
```

## apps/slack/eave/slack/requests/event_callback.py

```
The code defines a SlackEventCallbackHandler class that extends HTTPEndpoint, which is part of the Starlette framework. The class handles POST requests to the "/slack/events" endpoint. It processes incoming Slack events, verifies the request's signature, and filters out events that are not of interest. If an event is valid and matches a listener in the slack_app, it creates a task and adds it to a queue for further processing. The file does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[]
```

```json
[
  "slackeventcallbackhandler"
]
```

## apps/slack/eave/slack/requests

```
sentinel
```

## apps/slack/eave/slack/brain/base.py

```
The code is from a file called base.py in the apps/slack/eave/slack/brain directory. It defines a class called Base, which serves as the base class for all Brain mixins. The class contains attributes such as message, user_profile, expanded_text, message_context, eave_team, subscriptions, slack_context, message_action, and eave_ctx. It also has an __init__ method to initialize these attributes and an async log_event method to log events using the analytics module. Additionally, it has a property called execution_count that retrieves the task execution count from the slack_context. The file does not start an application server.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain/intent_processing.py

```
The code in the intent_processing.py file is part of a larger application and does not start an application server. It defines a class called IntentProcessingMixin, which inherits from DocumentManagementMixin and SubscriptionManagementMixin. The class has an asynchronous method called handle_action that takes a message_action as input and processes it based on the type of action. The possible actions include creating documentation, watching/unwatching a conversation, searching, updating, refining, and deleting documentation. There is also a method to handle unknown requests, which logs a warning and sends a response to the user. The unwatch_conversation method is used to delete a subscription and log the event.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain/communication.py

```
The code is from a file called communication.py in the apps/slack/eave/slack/brain directory. It defines a class called CommunicationMixin, which inherits from the Base class. The class contains four asynchronous methods: send_response, notify_failure, acknowledge_receipt, and _add_reaction. These methods are used for sending responses, notifying failures, acknowledging receipt of messages, and adding reactions to messages in a Slack application. The file does not start an application server.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain/message_prompts.py

```
The code in the file `message_prompts.py` defines an enumeration called `MessageAction` and two asynchronous functions: `message_action()` and `_get_openai_response()`. The `message_action()` function takes a context string and an optional LogContext object as input, formats a prompt, and calls the `_get_openai_response()` function to get a response from the OpenAI API. The response is then processed to determine the appropriate action to take based on the message. The `_get_openai_response()` function takes a list of messages and a temperature value as input, creates a ChatCompletionParameters object, and calls the OpenAI API to get a completion. The file does not start an application server.
```

```json
[
  "openai"
]
```

```json
[]
```

## apps/slack/eave/slack/brain/subscription_management.py

```
The code in this file defines a class called SubscriptionManagementMixin, which inherits from CommunicationMixin. This class has three asynchronous methods: get_subscription, create_subscription, and notify_existing_subscription. The get_subscription method retrieves a subscription, while the create_subscription method either gets and returns an existing subscription or creates and returns a new one. The notify_existing_subscription method sends a response to the user based on the existence of a document reference in the subscription. The file does not start an application server.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain/document_management.py

```
The code in the file document_management.py is a part of a larger application and does not start an application server. It defines a class called DocumentManagementMixin, which is responsible for managing documents in a Slack application. The class has several methods for creating, updating, searching, and archiving documents. It also interacts with the Core API to perform operations on documents and subscriptions. The class inherits from ContextBuildingMixin and SubscriptionManagementMixin, which provide additional functionality for building context and managing subscriptions.
```

```json
[]
```

```json
[
  "core_api",
  "contextbuildingmixin",
  "subscriptionmanagementmixin"
]
```

## apps/slack/eave/slack/brain/context_building.py

```
The code in context_building.py is part of a larger application and does not start an application server. It defines a class called ContextBuildingMixin, which is a subclass of the Base class. This class is responsible for building context from messages, links, and user profiles in a Slack conversation. It uses OpenAI's GPT-4 model to generate summaries and condensed versions of the conversation. The class also includes methods for handling links in the conversation, such as filtering supported links, mapping URL content, and subscribing to file changes.
```

```json
[
  "openai",
  "slack"
]
```

```json
[]
```

## apps/slack/eave/slack/brain/document_metadata.py

```
The code in the file `document_metadata.py` defines several asynchronous functions to generate metadata for a given conversation using OpenAI's GPT-4 model. It does not start an application server.

The functions are:
1. `get_topic(conversation: str) -> str`: Generates a short title for the given conversation.
2. `get_hierarchy(conversation: str) -> list[str]`: Generates a list of parent folder names for organizing the conversation in a directory hierarchy.
3. `get_documentation_type(conversation: str) -> DocumentationType`: Determines the most appropriate type of documentation for the given conversation from a predefined list of types (Technical Documentation, Project One-Pager, Team Onboarding, Engineer Onboarding, and Other).
4. `get_documentation(conversation: str, documentation_type: DocumentationType, link_context: Optional[str]) -> str`: Generates documentation for the given conversation based on the specified documentation type and optional link context.

The file also defines an enumeration `DocumentationType` to represent different types of documentation.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain/core.py

```
The code is from a file called core.py in the apps/slack/eave/slack/brain directory. It defines a class called Brain, which inherits from IntentProcessingMixin. The class has three main asynchronous methods: process_message, process_shortcut_event, and load_data. The process_message method handles processing of messages, checking if Eave is mentioned or subscribed to a thread, and takes appropriate actions based on the message context. The process_shortcut_event method acknowledges receipt of a shortcut event but does not have any further implementation. The load_data method retrieves user profile and expanded text information for the message and builds the message context.

The file does not start an application server like Express, Flask, Django, Gin, or Rack.
```

```json
[]
```

```json
[]
```

## apps/slack/eave/slack/brain

```
sentinel
```

## apps/slack/eave/slack

```
starlette_app
```

## apps/slack

```
sentinel
```

