### get_services_from_repo

#### system

```

You will be provided a GitHub organization name, a repository name, and the directory hierarchy for that repository (starting from the root of the repository). Your task is to create a short, human-readable name and a description for any public HTTP services hosted in this repository. It's likely that there is exactly one service in the repository, however there may be more than one in the case of a monorepo hosting multiple applications, and there may be none in the case of a repository hosting only shared library code, developer tools, configuration, etc.

The directory hierarchy will be delimited by three exclamation points, and formatted this way:

- <directory name>
    - <directory name>
        - <file name>
        - <file name>
    - <directory name>
        - <file name>
    - ...

The service name(s) will be used in a high-level system architecture diagram. Go through the hierarchy a few times before you make your decision, each time refining your understanding of the repository.

Output your answer as a JSON array of objects, with each object containing the following keys:

- "service_name": the name that you created for the service
- "service_description": the description that you wrote for the service
- "service_root": The path to the directory in the provided hierarchy that can be considered the root directory of the service.

Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.

```

#### user

```

GitHub organization: eave-fyi

Repository: eave-monorepo

Directory Hierarchy:
!!!


- 
    - bin
    - terraform
        - terraform/eavefyi-dev
    - develop
        - develop/proxy
            - develop/proxy/bin
            - develop/proxy/mitm_router.py
        - develop/deploy
            - develop/deploy/eave-builder-python
            - develop/deploy/bin
            - develop/deploy/eave-builder-gcloudsdk
            - develop/deploy/eave-builder-node
        - develop/shared
            - develop/shared/bin
        - develop/javascript
            - develop/javascript/es-config
                - develop/javascript/es-config/eslint
                - develop/javascript/es-config/bin
                - develop/javascript/es-config/typescript
            - develop/javascript/bin
        - develop/certs
            - develop/certs/eave-localhost
            - develop/certs/eave-run
            - develop/certs/bin
        - develop/python
            - develop/python/build
                - develop/python/build/lib
                    - develop/python/build/lib/eave
                        - develop/python/build/lib/eave/dev
                            - develop/python/build/lib/eave/dev/pretty_errors.py
                            - develop/python/build/lib/eave/dev/dotenv_loader.py
                        - develop/python/build/lib/eave/dev_tooling
                            - develop/python/build/lib/eave/dev_tooling/pretty_errors.py
                            - develop/python/build/lib/eave/dev_tooling/dotenv_loader.py
                    - develop/python/build/lib/pretty_errors.py
                    - develop/python/build/lib/dotenv_loader.py
                - develop/python/build/bdist.linux-x86_64
            - develop/python/src
                - develop/python/src/eave_dev_tooling.egg-info
                - develop/python/src/eave.egg-info
                - develop/python/src/eave
                    - develop/python/src/eave/dev_tooling
                        - develop/python/src/eave/dev_tooling/pretty_errors.py
                        - develop/python/src/eave/dev_tooling/dotenv_loader.py
                - develop/python/src/UNKNOWN.egg-info
            - develop/python/bin
            - develop/python/configs
            - develop/python/setup.py
    - apps
        - apps/core
            - apps/core/eave
                - apps/core/eave/core
                    - apps/core/eave/core/public
                        - apps/core/eave/core/public/requests
                            - apps/core/eave/core/public/requests/oauth
                                - apps/core/eave/core/public/requests/oauth/base.py
                                - apps/core/eave/core/public/requests/oauth/slack_oauth.py
                                - apps/core/eave/core/public/requests/oauth/github_oauth.py
                                - apps/core/eave/core/public/requests/oauth/shared.py
                                - apps/core/eave/core/public/requests/oauth/__init__.py
                                - apps/core/eave/core/public/requests/oauth/atlassian_oauth.py
                                - apps/core/eave/core/public/requests/oauth/google_oauth.py
                            - apps/core/eave/core/public/requests/atlassian_integration.py
                            - apps/core/eave/core/public/requests/team.py
                            - apps/core/eave/core/public/requests/authed_account.py
                            - apps/core/eave/core/public/requests/github_integration.py
                            - apps/core/eave/core/public/requests/subscriptions.py
                            - apps/core/eave/core/public/requests/status.py
                            - apps/core/eave/core/public/requests/slack_integration.py
                            - apps/core/eave/core/public/requests/__init__.py
                            - apps/core/eave/core/public/requests/documents.py
                            - apps/core/eave/core/public/requests/connect_integration.py
                            - apps/core/eave/core/public/requests/noop.py
                        - apps/core/eave/core/public/middlewares
                            - apps/core/eave/core/public/middlewares/authentication.py
                            - apps/core/eave/core/public/middlewares/team_lookup.py
                            - apps/core/eave/core/public/middlewares/__init__.py
                            - apps/core/eave/core/public/middlewares/development_bypass.py
                        - apps/core/eave/core/public/http_endpoint.py
                        - apps/core/eave/core/public/exception_handlers.py
                        - apps/core/eave/core/public/__init__.py
                    - apps/core/eave/core/internal
                        - apps/core/eave/core/internal/oauth
                            - apps/core/eave/core/internal/oauth/slack.py
                            - apps/core/eave/core/internal/oauth/google.py
                            - apps/core/eave/core/internal/oauth/__init__.py
                            - apps/core/eave/core/internal/oauth/state_cookies.py
                            - apps/core/eave/core/internal/oauth/atlassian.py
                            - apps/core/eave/core/internal/oauth/models.py
                        - apps/core/eave/core/internal/orm
                            - apps/core/eave/core/internal/orm/slack_installation.py
                            - apps/core/eave/core/internal/orm/connect_installation.py
                            - apps/core/eave/core/internal/orm/base.py
                            - apps/core/eave/core/internal/orm/github_installation.py
                            - apps/core/eave/core/internal/orm/team.py
                            - apps/core/eave/core/internal/orm/account.py
                            - apps/core/eave/core/internal/orm/subscription.py
                            - apps/core/eave/core/internal/orm/__init__.py
                            - apps/core/eave/core/internal/orm/util.py
                            - apps/core/eave/core/internal/orm/atlassian_installation.py
                            - apps/core/eave/core/internal/orm/document_reference.py
                            - apps/core/eave/core/internal/orm/resource_mutex.py
                            - apps/core/eave/core/internal/orm/confluence_destination.py
                        - apps/core/eave/core/internal/destinations
                        - apps/core/eave/core/internal/document_client.py
                        - apps/core/eave/core/internal/__init__.py
                        - apps/core/eave/core/internal/database.py
                        - apps/core/eave/core/internal/config.py
                    - apps/core/eave/core/__init__.py
                    - apps/core/eave/core/app.py
            - apps/core/bin
                - apps/core/bin/repl.py
        - apps/slack
            - apps/slack/eave
                - apps/slack/eave/slack
                    - apps/slack/eave/slack/requests
                        - apps/slack/eave/slack/requests/warmup.py
                        - apps/slack/eave/slack/requests/event_processor.py
                        - apps/slack/eave/slack/requests/__init__.py
                        - apps/slack/eave/slack/requests/event_callback.py
                    - apps/slack/eave/slack/brain
                        - apps/slack/eave/slack/brain/base.py
                        - apps/slack/eave/slack/brain/intent_processing.py
                        - apps/slack/eave/slack/brain/communication.py
                        - apps/slack/eave/slack/brain/message_prompts.py
                        - apps/slack/eave/slack/brain/subscription_management.py
                        - apps/slack/eave/slack/brain/document_management.py
                        - apps/slack/eave/slack/brain/context_building.py
                        - apps/slack/eave/slack/brain/document_metadata.py
                        - apps/slack/eave/slack/brain/core.py
                    - apps/slack/eave/slack/slack_app.py
                    - apps/slack/eave/slack/__init__.py
                    - apps/slack/eave/slack/event_handlers.py
                    - apps/slack/eave/slack/slack_models.py
                    - apps/slack/eave/slack/app.py
                    - apps/slack/eave/slack/config.py
            - apps/slack/bin
            - apps/slack/socketmode.py
        - apps/jira
            - apps/jira/src
                - apps/jira/src/events
                    - apps/jira/src/events/routes.ts
                    - apps/jira/src/events/comment-created.ts
                - apps/jira/src/api
                    - apps/jira/src/api/routes.ts
                - apps/jira/src/types.ts
                - apps/jira/src/jira-client.ts
                - apps/jira/src/app.ts
                - apps/jira/src/config.ts
            - apps/jira/bin
            - apps/jira/server.ts
        - apps/appengine-default
            - apps/appengine-default/main.py
        - apps/github
            - apps/github/src
                - apps/github/src/events
                    - apps/github/src/events/routes.ts
                    - apps/github/src/events/push.ts
                - apps/github/src/graphql
                - apps/github/src/api
                    - apps/github/src/api/routes.ts
                    - apps/github/src/api/content.ts
                    - apps/github/src/api/subscribe.ts
                    - apps/github/src/api/repos.ts
                - apps/github/src/lib
                    - apps/github/src/lib/graphql-util.ts
                    - apps/github/src/lib/octokit-util.ts
                    - apps/github/src/lib/cache.ts
                - apps/github/src/types.ts
                - apps/github/src/app.ts
                - apps/github/src/dispatch.ts
                - apps/github/src/registry.ts
                - apps/github/src/config.ts
            - apps/github/bin
            - apps/github/server.ts
        - apps/confluence
            - apps/confluence/src
                - apps/confluence/src/events
                    - apps/confluence/src/events/routes.ts
                - apps/confluence/src/api
                    - apps/confluence/src/api/routes.ts
                    - apps/confluence/src/api/util.ts
                    - apps/confluence/src/api/search-content.ts
                    - apps/confluence/src/api/create-content.ts
                    - apps/confluence/src/api/delete-content.ts
                    - apps/confluence/src/api/get-available-spaces.ts
                    - apps/confluence/src/api/update-content.ts
                - apps/confluence/src/app.ts
                - apps/confluence/src/confluence-client.ts
                - apps/confluence/src/config.ts
            - apps/confluence/bin
            - apps/confluence/server.ts
        - apps/marketing
            - apps/marketing/eave
                - apps/marketing/eave/marketing
                    - apps/marketing/eave/marketing/static
                        - apps/marketing/eave/marketing/static/dist
                        - apps/marketing/eave/marketing/static/images
                    - apps/marketing/eave/marketing/templates
                    - apps/marketing/eave/marketing/js
                        - apps/marketing/eave/marketing/js/components
                            - apps/marketing/eave/marketing/js/components/Footer
                            - apps/marketing/eave/marketing/js/components/Copy
                            - apps/marketing/eave/marketing/js/components/EaveLogo
                            - apps/marketing/eave/marketing/js/components/Header
                            - apps/marketing/eave/marketing/js/components/hoc
                            - apps/marketing/eave/marketing/js/components/Block
                            - apps/marketing/eave/marketing/js/components/AuthUser
                            - apps/marketing/eave/marketing/js/components/PrivateRoutes
                            - apps/marketing/eave/marketing/js/components/AuthModal
                            - apps/marketing/eave/marketing/js/components/Button
                            - apps/marketing/eave/marketing/js/components/Icons
                            - apps/marketing/eave/marketing/js/components/Pages
                                - apps/marketing/eave/marketing/js/components/Pages/Dashboard
                                - apps/marketing/eave/marketing/js/components/Pages/PrivacyPage
                                - apps/marketing/eave/marketing/js/components/Pages/Page
                                - apps/marketing/eave/marketing/js/components/Pages/HomePage
                                - apps/marketing/eave/marketing/js/components/Pages/TermsPage
                            - apps/marketing/eave/marketing/js/components/Banners
                                - apps/marketing/eave/marketing/js/components/Banners/PrivacyBanner
                                - apps/marketing/eave/marketing/js/components/Banners/DocumentationBanner
                                - apps/marketing/eave/marketing/js/components/Banners/IntegrationsBanner
                                - apps/marketing/eave/marketing/js/components/Banners/SlackBanner
                            - apps/marketing/eave/marketing/js/components/Hero
                            - apps/marketing/eave/marketing/js/components/PageSection
                            - apps/marketing/eave/marketing/js/components/Affiliates
                            - apps/marketing/eave/marketing/js/components/BlockStack
                            - apps/marketing/eave/marketing/js/components/ScrollToTop
                        - apps/marketing/eave/marketing/js/hooks
                        - apps/marketing/eave/marketing/js/context
                        - apps/marketing/eave/marketing/js/theme
                    - apps/marketing/eave/marketing/__init__.py
                    - apps/marketing/eave/marketing/app.py
                    - apps/marketing/eave/marketing/config.py
            - apps/marketing/bin
        - apps/archer
            - apps/archer/eave
                - apps/archer/eave/archer
                    - apps/archer/eave/archer/main.py
                    - apps/archer/eave/archer/graph_builder.py
                    - apps/archer/eave/archer/service_info.py
                    - apps/archer/eave/archer/render.py
                    - apps/archer/eave/archer/service_graph.py
                    - apps/archer/eave/archer/service_dependencies.py
                    - apps/archer/eave/archer/__init__.py
                    - apps/archer/eave/archer/util.py
                    - apps/archer/eave/archer/service_registry.py
                    - apps/archer/eave/archer/prompt_exp.py
                    - apps/archer/eave/archer/config.py
                    - apps/archer/eave/archer/fs_hierarchy.py
            - apps/archer/bin
    - libs
        - libs/eave-pubsub-schemas
            - libs/eave-pubsub-schemas/bin
            - libs/eave-pubsub-schemas/protos
            - libs/eave-pubsub-schemas/typescript
                - libs/eave-pubsub-schemas/typescript/src
                    - libs/eave-pubsub-schemas/typescript/src/generated
                        - libs/eave-pubsub-schemas/typescript/src/generated/eave_event.ts
                - libs/eave-pubsub-schemas/typescript/bin
            - libs/eave-pubsub-schemas/python
                - libs/eave-pubsub-schemas/python/build
                    - libs/eave-pubsub-schemas/python/build/lib
                        - libs/eave-pubsub-schemas/python/build/lib/eave
                            - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas
                                - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas/generated
                                    - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas/generated/eave_user_action_pb2.py
                                    - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas/generated/__init__.py
                                    - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas/generated/eave_event_pb2.py
                                - libs/eave-pubsub-schemas/python/build/lib/eave/pubsub_schemas/__init__.py
                    - libs/eave-pubsub-schemas/python/build/bdist.linux-x86_64
                - libs/eave-pubsub-schemas/python/src
                    - libs/eave-pubsub-schemas/python/src/eave
                        - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas
                            - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas/generated
                                - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas/generated/eave_event_pb2.pyi
                                - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas/generated/__init__.py
                                - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas/generated/eave_event_pb2.py
                            - libs/eave-pubsub-schemas/python/src/eave/pubsub_schemas/__init__.py
                    - libs/eave-pubsub-schemas/python/src/eave_pubsub_schemas.egg-info
                - libs/eave-pubsub-schemas/python/bin
                - libs/eave-pubsub-schemas/python/test.py
                - libs/eave-pubsub-schemas/python/setup.py
            - libs/eave-pubsub-schemas/sync_schemas.py
        - libs/eave-stdlib-ts
            - libs/eave-stdlib-ts/src
                - libs/eave-stdlib-ts/src/connect
                    - libs/eave-stdlib-ts/src/connect/types
                        - libs/eave-stdlib-ts/src/connect/types/adf.ts
                    - libs/eave-stdlib-ts/src/connect/dev-tunnel-config.ts
                    - libs/eave-stdlib-ts/src/connect/connect-client.ts
                    - libs/eave-stdlib-ts/src/connect/eave-api-store-adapter.ts
                    - libs/eave-stdlib-ts/src/connect/security-policy-middlewares.ts
                    - libs/eave-stdlib-ts/src/connect/lifecycle-router.ts
                - libs/eave-stdlib-ts/src/jira-api
                    - libs/eave-stdlib-ts/src/jira-api/models.ts
                - libs/eave-stdlib-ts/src/middleware
                    - libs/eave-stdlib-ts/src/middleware/request-integrity.ts
                    - libs/eave-stdlib-ts/src/middleware/exception-handling.ts
                    - libs/eave-stdlib-ts/src/middleware/logging.ts
                    - libs/eave-stdlib-ts/src/middleware/development-bypass.ts
                    - libs/eave-stdlib-ts/src/middleware/body-parser.ts
                    - libs/eave-stdlib-ts/src/middleware/signature-verification.ts
                    - libs/eave-stdlib-ts/src/middleware/origin.ts
                    - libs/eave-stdlib-ts/src/middleware/common-middlewares.ts
                    - libs/eave-stdlib-ts/src/middleware/require-headers.ts
                - libs/eave-stdlib-ts/src/core-api
                    - libs/eave-stdlib-ts/src/core-api/operations
                        - libs/eave-stdlib-ts/src/core-api/operations/status.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/team.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/github.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/subscriptions.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/connect.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/slack.ts
                        - libs/eave-stdlib-ts/src/core-api/operations/documents.ts
                    - libs/eave-stdlib-ts/src/core-api/models
                        - libs/eave-stdlib-ts/src/core-api/models/integrations.ts
                        - libs/eave-stdlib-ts/src/core-api/models/team.ts
                        - libs/eave-stdlib-ts/src/core-api/models/atlassian.ts
                        - libs/eave-stdlib-ts/src/core-api/models/github.ts
                        - libs/eave-stdlib-ts/src/core-api/models/subscriptions.ts
                        - libs/eave-stdlib-ts/src/core-api/models/account.ts
                        - libs/eave-stdlib-ts/src/core-api/models/connect.ts
                        - libs/eave-stdlib-ts/src/core-api/models/slack.ts
                        - libs/eave-stdlib-ts/src/core-api/models/documents.ts
                    - libs/eave-stdlib-ts/src/core-api/enums.ts
                - libs/eave-stdlib-ts/src/confluence-api
                    - libs/eave-stdlib-ts/src/confluence-api/models.ts
                    - libs/eave-stdlib-ts/src/confluence-api/operations.ts
                - libs/eave-stdlib-ts/src/github-api
                    - libs/eave-stdlib-ts/src/github-api/client.ts
                    - libs/eave-stdlib-ts/src/github-api/models.ts
                    - libs/eave-stdlib-ts/src/github-api/operations.ts
                - libs/eave-stdlib-ts/src/link-handler.ts
                - libs/eave-stdlib-ts/src/eave-origins.ts
                - libs/eave-stdlib-ts/src/signing.ts
                - libs/eave-stdlib-ts/src/logging.ts
                - libs/eave-stdlib-ts/src/util.ts
                - libs/eave-stdlib-ts/src/types.ts
                - libs/eave-stdlib-ts/src/exceptions.ts
                - libs/eave-stdlib-ts/src/openai.ts
                - libs/eave-stdlib-ts/src/api-util.ts
                - libs/eave-stdlib-ts/src/requests.ts
                - libs/eave-stdlib-ts/src/analytics.ts
                - libs/eave-stdlib-ts/src/headers.ts
                - libs/eave-stdlib-ts/src/cache.ts
                - libs/eave-stdlib-ts/src/config.ts
            - libs/eave-stdlib-ts/bin
        - libs/eave-stdlib-py
            - libs/eave-stdlib-py/build
                - libs/eave-stdlib-py/build/lib
                    - libs/eave-stdlib-py/build/lib/eave
                        - libs/eave-stdlib-py/build/lib/eave/stdlib
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/confluence_api
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/confluence_api/operations.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/confluence_api/__init__.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/confluence_api/models.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/base.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/exception_handling.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/body_parsing.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/request_integrity.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/signature_verification.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/__init__.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/logging.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/origin.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/middleware/development_bypass.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/slack.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/team.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/subscriptions.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/account.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/status.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/connect.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/__init__.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/github.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/documents.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/operations/atlassian.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/slack.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/error.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/team.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/subscriptions.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/account.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/connect.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/__init__.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/github.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/documents.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/atlassian.py
                                    - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/models/integrations.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/__init__.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/core_api/enums.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/github_api
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/github_api/operations.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/github_api/client.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/github_api/__init__.py
                                - libs/eave-stdlib-py/build/lib/eave/stdlib/github_api/models.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/cookies.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/slack.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/jwt.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/signing.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/requests.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/request_state.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/cache.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/test_util.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/link_handler.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/api_util.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/__init__.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/endpoints.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/util.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/task_queue.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/analytics.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/logging.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/openai_client.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/headers.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/checksum.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/atlassian.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/eave_origins.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/typing.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/config.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/time.py
                            - libs/eave-stdlib-py/build/lib/eave/stdlib/exceptions.py
                - libs/eave-stdlib-py/build/bdist.linux-x86_64
            - libs/eave-stdlib-py/src
                - libs/eave-stdlib-py/src/eave
                    - libs/eave-stdlib-py/src/eave/stdlib
                        - libs/eave-stdlib-py/src/eave/stdlib/confluence_api
                            - libs/eave-stdlib-py/src/eave/stdlib/confluence_api/operations.py
                            - libs/eave-stdlib-py/src/eave/stdlib/confluence_api/__init__.py
                            - libs/eave-stdlib-py/src/eave/stdlib/confluence_api/models.py
                        - libs/eave-stdlib-py/src/eave/stdlib/middleware
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/base.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/exception_handling.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/body_parsing.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/request_integrity.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/signature_verification.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/__init__.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/logging.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/origin.py
                            - libs/eave-stdlib-py/src/eave/stdlib/middleware/development_bypass.py
                        - libs/eave-stdlib-py/src/eave/stdlib/core_api
                            - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/slack.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/team.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/subscriptions.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/account.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/status.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/connect.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/__init__.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/github.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/documents.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/operations/atlassian.py
                            - libs/eave-stdlib-py/src/eave/stdlib/core_api/models
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/slack.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/error.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/team.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/subscriptions.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/account.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/connect.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/__init__.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/github.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/documents.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/atlassian.py
                                - libs/eave-stdlib-py/src/eave/stdlib/core_api/models/integrations.py
                            - libs/eave-stdlib-py/src/eave/stdlib/core_api/__init__.py
                            - libs/eave-stdlib-py/src/eave/stdlib/core_api/enums.py
                        - libs/eave-stdlib-py/src/eave/stdlib/github_api
                            - libs/eave-stdlib-py/src/eave/stdlib/github_api/operations.py
                            - libs/eave-stdlib-py/src/eave/stdlib/github_api/client.py
                            - libs/eave-stdlib-py/src/eave/stdlib/github_api/__init__.py
                            - libs/eave-stdlib-py/src/eave/stdlib/github_api/models.py
                        - libs/eave-stdlib-py/src/eave/stdlib/cookies.py
                        - libs/eave-stdlib-py/src/eave/stdlib/slack.py
                        - libs/eave-stdlib-py/src/eave/stdlib/jwt.py
                        - libs/eave-stdlib-py/src/eave/stdlib/signing.py
                        - libs/eave-stdlib-py/src/eave/stdlib/requests.py
                        - libs/eave-stdlib-py/src/eave/stdlib/request_state.py
                        - libs/eave-stdlib-py/src/eave/stdlib/cache.py
                        - libs/eave-stdlib-py/src/eave/stdlib/test_util.py
                        - libs/eave-stdlib-py/src/eave/stdlib/link_handler.py
                        - libs/eave-stdlib-py/src/eave/stdlib/api_util.py
                        - libs/eave-stdlib-py/src/eave/stdlib/__init__.py
                        - libs/eave-stdlib-py/src/eave/stdlib/endpoints.py
                        - libs/eave-stdlib-py/src/eave/stdlib/util.py
                        - libs/eave-stdlib-py/src/eave/stdlib/task_queue.py
                        - libs/eave-stdlib-py/src/eave/stdlib/analytics.py
                        - libs/eave-stdlib-py/src/eave/stdlib/logging.py
                        - libs/eave-stdlib-py/src/eave/stdlib/openai_client.py
                        - libs/eave-stdlib-py/src/eave/stdlib/headers.py
                        - libs/eave-stdlib-py/src/eave/stdlib/checksum.py
                        - libs/eave-stdlib-py/src/eave/stdlib/atlassian.py
                        - libs/eave-stdlib-py/src/eave/stdlib/eave_origins.py
                        - libs/eave-stdlib-py/src/eave/stdlib/typing.py
                        - libs/eave-stdlib-py/src/eave/stdlib/config.py
                        - libs/eave-stdlib-py/src/eave/stdlib/time.py
                        - libs/eave-stdlib-py/src/eave/stdlib/exceptions.py
                - libs/eave-stdlib-py/src/eave_stdlib_py.egg-info
            - libs/eave-stdlib-py/bin
            - libs/eave-stdlib-py/setup.py
    - .python-version

!!!
```

### get_dependencies

#### system

```

You will be given a GitHub organization name, a repository name, some code from that repository (delimited by three exclamation marks), and a comma-separated list of service names. Your task is to find which (if any) of the provided APIs/services the code references, uses, calls, or depends on. Your answer will be used to create a high-level system architecture diagram.

Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name.

Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.

```

#### user

```

GitHub organization: eave-fyi

Repository: eave-monorepo

Service names: Eave Core Service, Eave Slack Service, Eave Jira Service, Eave Github Service, Eave Confluence Service, Eave Marketing Service, Eave Archer Service

 Code:
!!!


from eave.stdlib.core_api.models.subscriptions import SubscriptionInfo
from . import message_prompts


from eave.stdlib.logging import eaveLogger
from .intent_processing import IntentProcessingMixin


class Brain(IntentProcessingMixin):
    async def process_message(self) -> None:
        eaveLogger.debug("Brain.process_message", self.eave_ctx)

        await self.load_data()

        subscription_response = await self.get_subscription()
        if subscription_response.subscription:
            self.subscriptions.append(
                SubscriptionInfo(
                    subscription=subscription_response.subscription,
                    document_reference=subscription_response.document_reference,
                )
            )

        i_am_mentioned = await self.message.check_eave_is_mentioned()
        if i_am_mentioned is True:
            """
            Eave is mentioned in this message.
            1. Acknowledge receipt of the message.
            1. If she's being asked for thread information, handle that and stop processing.
            1. Otherwise, send a preliminary response and continue processing.
            """
            await self.acknowledge_receipt()

            self.message_action = await message_prompts.message_action(context=self.message_context)

            self.log_event(
                event_name="eave_mentioned",
                event_description="Eave was mentioned in Slack",
                opaque_params={
                    "action": self.message_action,
                },
            )

        else:
            """
            Eave is not mentioned in this message.
            1. Lookup an existing subscription for this source.
            1. If she is not subscribed, then ignore the message and stop processing.
            1. Otherwise, continue processing.
            """
            if len(self.subscriptions) == 0:
                eaveLogger.debug("Eave is not subscribed to this thread; ignoring.", self.eave_ctx)
                return

            self.message_action = message_prompts.MessageAction.REFINE_DOCUMENTATION

        self.log_event(
            event_name="slack_eave_action",
            event_description="Eave is taking an action based on a Slack message",
            opaque_params={
                "action": self.message_action,
            },
        )

        await self.handle_action(message_action=self.message_action)

    async def process_shortcut_event(self) -> None:
        await self.acknowledge_receipt()

        # source = eave_models.SubscriptionSource(
        #     event=eave_models.SubscriptionSourceEvent.slack_message,
        #     id=message.subscription_id,
        # )

        # response = await eave_models.client.get_or_create_subscription(source=source)
        # manager = DocumentManager(message=message, subscription=response.subscription)
        # await manager.process_message()

    async def load_data(self) -> None:
        user_profile = await self.message.get_user_profile()
        self.user_profile = user_profile

        expanded_text = await self.message.get_expanded_text()
        if expanded_text is None:
            eaveLogger.warning(
                "slack message expanded_text is unexpectedly None",
                self.eave_ctx,
                {"message_text": self.message.text},
            )

            # FIXME: Brain should allow None expanded_text so it can retry.
            expanded_text = ""

        self.expanded_text = expanded_text

        await self.build_message_context()


!!!
```

