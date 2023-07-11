### get_services_from_repo

```
SYSTEM:

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
Tokens: 298
```

```
USER:

GitHub organization: eave-fyi

Repository: eave-monorepo

Directory hierarchy:
!!!

- (root)
  - bin
    - http-proxy
    - lint
    - format
    - clean
    - proxy
    - setup
    - deploy
    - cloud-sql-proxy
    - pg-shell
    - pushcheck
    - test
    - ngrok-tunnel
  - terraform
    - eavefyi-dev
      - monitoring.tf
      - metadata.tf
      - vpc-access.tf
      - logging.tf
      - cloud-sql.tf
      - appengine.tf
      - main.tf
      - secret-manager.tf
      - imports.tf
      - cloud-tasks.tf
      - network.tf
      - certificate-manager.tf
      - redis.tf
      - cloud-build.tf
      - pubsub.tf
      - kms.tf
      - project.tf
      - bigquery.tf
      - runtime-config.tf
  - develop
    - proxy
      - bin
        - serve
      - mitm_router.py
    - deploy
      - eave-builder-python
        - Dockerfile
      - bin
        - push
      - eave-builder-gcloudsdk
        - Dockerfile
      - eave-builder-node
      - README.md
    - shared
      - bin
        - deploy-appengine
        - setup-deployment-workspace
        - build-dotenv
        - run-with-dotenv
        - status
      - _functions.bash
    - javascript
      - es-config
        - eslint
          - typescript.js
          - graphql.js
          - yaml.js
          - index.js
          - react.js
        - bin
          - setup
        - typescript
          - ava.config.mjs
          - tsconfig.json
        - package-lock.json
        - package.json
      - bin
        - lint
        - format
        - deploy-appengine
        - setup
        - test
      - package-lock.json
      - package.json
      - _functions.bash
    - certs
      - eave-localhost
        - eave-localhost.crt
        - eave-localhost.pem
        - eave-localhost.key
      - eave-run
        - eave-run.key
        - eave-run.crt
        - eave-run.pem
      - bin
        - make-cert
        - install-certs
    - python
      - src
        - eave
          - dev_tooling
            - pretty_errors.py
            - dotenv_loader.py
      - bin
        - lint
        - format
        - deploy-appengine
        - setup
        - test
      - configs
        - pyproject.toml
      - pyproject.toml
      - requirements-dev.txt
      - setup.py
      - _functions.bash
      - setup.cfg
    - wrap-key-kms.bash
    - requirements-dev.txt
    - functions.bash
  - apps
    - core
      - eave_alembic
        - versions
          - 2023_05_23_2002-e66762912ba4_add_emails_to_accounts_table.py
          - 2023_05_04_1934-7077e9067e19_remove_auth_token_table.py
          - 2023_06_08_0808-23d85d98202d_add_index_to_org_url.py
          - 2023_05_05_1959-271e6339d054_add_github_installations.py
          - 2023_06_09_1818-e8115fe8febb_add_index_to_team_id.py
          - 2023_05_02_1911-25534cc72fa4_add_account_tracking_params.py
          - 2023_05_15_1555-389edb075d5e_.py
          - 2023_06_02_1845-8b9901c4cc2c_atlassian_connect.py
          - 2023_06_05_1541-cb9ab45eb78f_confluence_dest_update.py
          - 2023_05_29_0301-b2eb47841833_forge_tables.py
          - 2023_05_17_2051-a4ee5f0e5c49_remove_document_reference_unique_.py
          - 2023_06_06_0135-a61fd4303d02_add_org_url_to_connect_installs.py
          - 2023_05_23_2150-920f9d3ede4c_add_identifiers_to_installation_tables.py
        - migrate.py
        - script.py.mako
        - seed_database.py
        - init_database.py
        - __init__.py
        - env.py
      - eave
        - core
          - public
            - requests
              - oauth
                - base.py
                - slack_oauth.py
                - github_oauth.py
                - shared.py
                - __init__.py
                - atlassian_oauth.py
                - google_oauth.py
              - atlassian_integration.py
              - team.py
              - authed_account.py
              - github_integration.py
              - subscriptions.py
              - status.py
              - slack_integration.py
              - __init__.py
              - documents.py
              - connect_integration.py
              - noop.py
            - middlewares
              - authentication.py
              - team_lookup.py
              - __init__.py
              - development_bypass.py
            - http_endpoint.py
            - exception_handlers.py
            - __init__.py
          - internal
            - oauth
              - slack.py
              - google.py
              - __init__.py
              - state_cookies.py
              - atlassian.py
              - models.py
            - orm
              - slack_installation.py
              - connect_installation.py
              - base.py
              - github_installation.py
              - team.py
              - account.py
              - subscription.py
              - __init__.py
              - util.py
              - atlassian_installation.py
              - document_reference.py
              - resource_mutex.py
              - confluence_destination.py
            - destinations
            - document_client.py
            - __init__.py
            - database.py
            - config.py
          - __init__.py
          - app.py
      - bin
        - lint
        - format
        - repl
        - setup
        - appengine-dev-server
        - logs
        - run-db-migration
        - deploy
        - setup-db
        - repl.py
        - test
        - status
        - create-db-migration
      - tests
        - core
          - signature_verification_test.py
          - base.py
          - delete_document_test.py
          - atlassian_oauth_test.py
          - confluence_destination_test.py
          - installations_test.py
          - subscription_test.py
          - resource_mutex_test.py
          - slack_oauth_test.py
          - search_documents_test.py
          - connect_integration_test.py
          - team_test.py
          - body_parser_middleware_test.py
          - status_endpoint_test.py
          - origin_middleware_test.py
          - __init__.py
          - authed_account_test.py
          - team_requests_test.py
          - slack_installation_test.py
          - google_oauth_test.py
          - subscription_requests_test.py
          - team_lookup_middleware_test.py
      - app.eave-production.yaml
      - README.md
      - requirements-vendor.txt
      - alembic.ini
      - requirements.txt
      - app.eavefyi-dev.yaml
      - requirements-dev.txt
      - cloudbuild.yaml
    - slack
      - eave
        - slack
          - requests
            - warmup.py
            - event_processor.py
            - __init__.py
            - event_callback.py
          - brain
            - base.py
            - intent_processing.py
            - communication.py
            - message_prompts.py
            - subscription_management.py
            - document_management.py
            - context_building.py
            - document_metadata.py
            - core.py
          - slack_app.py
          - __init__.py
          - event_handlers.py
          - slack_models.py
          - app.py
          - config.py
      - bin
        - lint
        - format
        - setup
        - appengine-dev-server
        - logs
        - deploy
        - test
        - status
      - tests
        - slack
          - base.py
          - warmup_test.py
          - event_processor_test.py
          - subscription_management_test.py
          - document_management_test.py
          - brain_test.py
          - __init__.py
          - intent_processing_test.py
          - prompt_tester.py
          - events_endpoint_test.py
          - communication_test.py
      - app.eave-production.yaml
      - README.md
      - requirements-vendor.txt
      - requirements.txt
      - socketmode.py
      - app.eavefyi-dev.yaml
      - requirements-dev.txt
    - jira
      - src
        - events
          - routes.ts
          - comment-created.ts
        - api
          - routes.ts
        - types.ts
        - jira-client.ts
        - app.ts
        - config.ts
      - bin
        - lint
        - format
        - setup
        - logs
        - deploy
        - test
        - status
      - server.ts
      - app.eave-production.yaml
      - README.md
      - atlassian-connect.json
      - pm2.config.cjs
      - package-lock.json
      - credentials.json
      - app.eavefyi-dev.yaml
      - tsconfig.json
      - package.json
      - config.json
    - appengine-default
      - main.py
      - README.md
      - app.yaml
    - github
      - src
        - events
          - routes.ts
          - push.ts
        - graphql
          - getResource.graphql
          - getFileContentsByPath.graphql
          - getFileContents.graphql
          - getRefs.graphql
        - api
          - routes.ts
          - content.ts
          - subscribe.ts
          - repos.ts
        - lib
          - graphql-util.ts
          - octokit-util.ts
          - cache.ts
        - types.ts
        - app.ts
        - dispatch.ts
        - registry.ts
        - config.ts
      - bin
        - lint
        - format
        - setup
        - appengine-dev-server
        - logs
        - deploy
        - test
        - status
      - tests
        - signing.test.ts
      - server.ts
      - app.eave-production.yaml
      - README.md
      - pm2.config.cjs
      - package-lock.json
      - app.eavefyi-dev.yaml
      - tsconfig.json
      - package.json
    - confluence
      - src
        - events
          - routes.ts
        - api
          - routes.ts
          - util.ts
          - search-content.ts
          - create-content.ts
          - delete-content.ts
          - get-available-spaces.ts
          - update-content.ts
        - app.ts
        - confluence-client.ts
        - config.ts
      - bin
        - lint
        - format
        - setup
        - logs
        - deploy
        - test
        - status
      - tests
        - status.test.ts
        - create-content.test.ts
      - server.ts
      - app.eave-production.yaml
      - README.md
      - atlassian-connect.json
      - pm2.config.cjs
      - package-lock.json
      - credentials.json
      - app.eavefyi-dev.yaml
      - tsconfig.json
      - package.json
      - config.json
    - marketing
      - eave
        - marketing
          - static
            - images
              - eave-slack-2x.png
              - slack-logo-3x.png
              - notion-logo-3x.png
              - github-logo-3x.png
              - sharepoint-logo-3x.png
              - figma-logo-3x.png
              - confluence-mock.png
              - amazon-logo-3x.png
              - eave-slack-small-2x.png
              - paypal-logo-3x.png
              - outlook-logo-3x.png
              - confluence-mock-mobile.png
              - disney-logo-3x.png
              - teams-logo-3x.png
              - gmail-logo-3x.png
              - jira-logo-3x.png
              - google-drive-logo-3x.png
              - privacy-icons-3x.png
              - honey-logo-3x.png
              - e-icon-small.png
              - github-logo-inline.png
              - confluence-logo-3x.png
          - templates
            - index.html.jinja
          - js
            - components
              - Footer
                - index.jsx
              - Copy
                - index.jsx
              - EaveLogo
                - index.jsx
              - Header
                - index.jsx
              - hoc
                - withTitle.js
              - Block
                - index.js
              - AuthUser
                - index.jsx
              - PrivateRoutes
                - index.jsx
              - AuthModal
                - index.jsx
              - Button
                - index.jsx
              - Icons
                - DownIcon.js
                - CloseIcon.js
                - LockIcon.js
                - HamburgerIcon.js
                - GoogleIcon.jsx
                - PurpleCheckIcon.jsx
                - DocumentIcon.js
                - SlackIcon.jsx
                - ConnectIcon.js
                - AtlassianIcon.jsx
                - SnapIcon.js
                - ConfluenceIcon.jsx
                - ChatboxIcon.jsx
                - SyncIcon.js
              - Pages
                - Dashboard
                  - StepIcon.jsx
                  - Steps.jsx
                  - Thanks.jsx
                  - Footnote.jsx
                  - index.jsx
                - PrivacyPage
                  - index.jsx
                - Page
                  - index.jsx
                - HomePage
                  - index.jsx
                - TermsPage
                  - index.jsx
              - Banners
                - PrivacyBanner
                  - index.jsx
                - DocumentationBanner
                  - index.jsx
                - IntegrationsBanner
                  - index.jsx
                - SlackBanner
                  - index.jsx
              - Hero
                - index.jsx
              - PageSection
                - index.jsx
              - Affiliates
                - index.js
              - BlockStack
                - index.js
              - ScrollToTop
                - index.jsx
            - hooks
              - useAuthModal.js
              - useUser.js
              - useError.js
            - context
              - Provider.js
            - theme
              - index.js
            - App.js
            - asset-helpers.js
            - index.js
            - constants.js
            - cookies.js
          - __init__.py
          - app.py
          - config.py
      - bin
        - remove-unused-images
        - lint
        - format
        - setup
        - appengine-dev-server
        - logs
        - deploy
        - test
        - status
      - app.eave-production.yaml
      - README.md
      - requirements-vendor.txt
      - requirements.txt
      - package-lock.json
      - app.eavefyi-dev.yaml
      - requirements-dev.txt
      - package.json
      - webpack.config.cjs
    - archer
      - eave
        - archer
          - main.py
          - graph_builder.py
          - service_info.py
          - render.py
          - test-repos.md
          - service_graph.py
          - service_dependencies.py
          - __init__.py
          - util.py
          - service_registry.py
          - prompt_exp.py
          - config.py
          - fs_hierarchy.py
      - bin
        - lint
        - format
        - setup
        - run-exp
        - logs
        - deploy
        - test
        - status
      - tests
        - archer
          - lorem
            - long.txt
            - short.txt
          - file_contents_test.py
          - __init__.py
      - requirements-vendor.txt
      - requirements.txt
      - requirements-dev.txt
      - graph.mermaid
  - libs
    - eave-pubsub-schemas
      - bin
        - lint
        - format
        - sync
        - setup
        - test
      - protos
        - eave_event.proto
      - typescript
        - src
          - generated
            - eave_event.ts
        - bin
          - lint
          - format
          - test
        - package-lock.json
        - tsconfig.json
        - package.json
      - python
        - src
          - eave
            - pubsub_schemas
              - generated
                - eave_event_pb2.pyi
                - __init__.py
                - eave_event_pb2.py
              - __init__.py
        - bin
          - lint
          - format
          - test
        - pyproject.toml
        - test.py
        - setup.py
        - setup.cfg
      - sync_schemas.py
      - README.md
      - package-lock.json
      - requirements-dev.txt
      - package.json
    - eave-stdlib-ts
      - src
        - connect
          - types
            - adf.ts
          - dev-tunnel-config.ts
          - connect-client.ts
          - eave-api-store-adapter.ts
          - security-policy-middlewares.ts
          - lifecycle-router.ts
        - jira-api
          - models.ts
        - middleware
          - request-integrity.ts
          - exception-handling.ts
          - logging.ts
          - development-bypass.ts
          - body-parser.ts
          - signature-verification.ts
          - origin.ts
          - common-middlewares.ts
          - require-headers.ts
        - core-api
          - operations
            - status.ts
            - team.ts
            - github.ts
            - subscriptions.ts
            - connect.ts
            - slack.ts
            - documents.ts
          - models
            - integrations.ts
            - team.ts
            - atlassian.ts
            - github.ts
            - subscriptions.ts
            - account.ts
            - connect.ts
            - slack.ts
            - documents.ts
          - enums.ts
        - confluence-api
          - models.ts
          - operations.ts
        - github-api
          - client.ts
          - models.ts
          - operations.ts
        - link-handler.ts
        - eave-origins.ts
        - signing.ts
        - logging.ts
        - util.ts
        - types.ts
        - exceptions.ts
        - openai.ts
        - api-util.ts
        - requests.ts
        - analytics.ts
        - headers.ts
        - cache.ts
        - config.ts
      - bin
        - lint
        - format
        - setup
        - test
      - package-lock.json
      - tsconfig.json
      - package.json
    - eave-stdlib-py
      - src
        - eave
          - stdlib
            - confluence_api
              - operations.py
              - __init__.py
              - models.py
            - middleware
              - base.py
              - exception_handling.py
              - body_parsing.py
              - request_integrity.py
              - signature_verification.py
              - __init__.py
              - logging.py
              - origin.py
              - development_bypass.py
            - core_api
              - operations
                - slack.py
                - team.py
                - subscriptions.py
                - account.py
                - status.py
                - connect.py
                - __init__.py
                - github.py
                - documents.py
                - atlassian.py
              - models
                - slack.py
                - error.py
                - team.py
                - subscriptions.py
                - account.py
                - connect.py
                - __init__.py
                - github.py
                - documents.py
                - atlassian.py
                - integrations.py
              - __init__.py
              - enums.py
            - github_api
              - operations.py
              - client.py
              - __init__.py
              - models.py
            - cookies.py
            - slack.py
            - jwt.py
            - signing.py
            - requests.py
            - request_state.py
            - cache.py
            - test_util.py
            - link_handler.py
            - api_util.py
            - __init__.py
            - endpoints.py
            - util.py
            - task_queue.py
            - analytics.py
            - logging.py
            - openai_client.py
            - headers.py
            - checksum.py
            - atlassian.py
            - eave_origins.py
            - typing.py
            - config.py
            - time.py
            - exceptions.py
      - bin
        - lint
        - format
        - setup
        - test
      - tests
        - stdlib
          - core_api
            - connect_test.py
            - __init__.py
          - link_handler_test.py
          - __init__.py
          - util_test.py
          - analytics_test.py
        - __init__.py
      - pyproject.toml
      - requirements-dev.txt
      - setup.py
      - setup.cfg
  - README.md
  - ngrok.yml

!!!
Tokens: 4692
```

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You will be provided a GitHub organization name, a repository name, and the directory hierarchy for that repository (starting from the root of the repository). Your task is to create a short, human-readable name and a description for any public HTTP services hosted in this repository. It's likely that there is exactly one service in the repository, however there may be more than one in the case of a monorepo hosting multiple applications, and there may be none in the case of a repository hosting only shared library code, developer tools, configuration, etc.\n\nThe directory hierarchy will be delimited by three exclamation points, and formatted this way:\n\n- <directory name>\n    - <directory name>\n        - <file name>\n        - <file name>\n    - <directory name>\n        - <file name>\n    - ...\n\nThe service name(s) will be used in a high-level system architecture diagram. Go through the hierarchy a few times before you make your decision, each time refining your understanding of the repository.\n\nOutput your answer as a JSON array of objects, with each object containing the following keys:\n\n- \"service_name\": the name that you created for the service\n- \"service_description\": the description that you wrote for the service\n- \"service_root\": The path to the directory in the provided hierarchy that can be considered the root directory of the service.\n\nYour full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser."
    },
    {
      "role": "user",
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nDirectory hierarchy:\n!!!\n\n- (root)\n  - bin\n    - http-proxy\n    - lint\n    - format\n    - clean\n    - proxy\n    - setup\n    - deploy\n    - cloud-sql-proxy\n    - pg-shell\n    - pushcheck\n    - test\n    - ngrok-tunnel\n  - terraform\n    - eavefyi-dev\n      - monitoring.tf\n      - metadata.tf\n      - vpc-access.tf\n      - logging.tf\n      - cloud-sql.tf\n      - appengine.tf\n      - main.tf\n      - secret-manager.tf\n      - imports.tf\n      - cloud-tasks.tf\n      - network.tf\n      - certificate-manager.tf\n      - redis.tf\n      - cloud-build.tf\n      - pubsub.tf\n      - kms.tf\n      - project.tf\n      - bigquery.tf\n      - runtime-config.tf\n  - develop\n    - proxy\n      - bin\n        - serve\n      - mitm_router.py\n    - deploy\n      - eave-builder-python\n        - Dockerfile\n      - bin\n        - push\n      - eave-builder-gcloudsdk\n        - Dockerfile\n      - eave-builder-node\n      - README.md\n    - shared\n      - bin\n        - deploy-appengine\n        - setup-deployment-workspace\n        - build-dotenv\n        - run-with-dotenv\n        - status\n      - _functions.bash\n    - javascript\n      - es-config\n        - eslint\n          - typescript.js\n          - graphql.js\n          - yaml.js\n          - index.js\n          - react.js\n        - bin\n          - setup\n        - typescript\n          - ava.config.mjs\n          - tsconfig.json\n        - package-lock.json\n        - package.json\n      - bin\n        - lint\n        - format\n        - deploy-appengine\n        - setup\n        - test\n      - package-lock.json\n      - package.json\n      - _functions.bash\n    - certs\n      - eave-localhost\n        - eave-localhost.crt\n        - eave-localhost.pem\n        - eave-localhost.key\n      - eave-run\n        - eave-run.key\n        - eave-run.crt\n        - eave-run.pem\n      - bin\n        - make-cert\n        - install-certs\n    - python\n      - src\n        - eave\n          - dev_tooling\n            - pretty_errors.py\n            - dotenv_loader.py\n      - bin\n        - lint\n        - format\n        - deploy-appengine\n        - setup\n        - test\n      - configs\n        - pyproject.toml\n      - pyproject.toml\n      - requirements-dev.txt\n      - setup.py\n      - _functions.bash\n      - setup.cfg\n    - wrap-key-kms.bash\n    - requirements-dev.txt\n    - functions.bash\n  - apps\n    - core\n      - eave_alembic\n        - versions\n          - 2023_05_23_2002-e66762912ba4_add_emails_to_accounts_table.py\n          - 2023_05_04_1934-7077e9067e19_remove_auth_token_table.py\n          - 2023_06_08_0808-23d85d98202d_add_index_to_org_url.py\n          - 2023_05_05_1959-271e6339d054_add_github_installations.py\n          - 2023_06_09_1818-e8115fe8febb_add_index_to_team_id.py\n          - 2023_05_02_1911-25534cc72fa4_add_account_tracking_params.py\n          - 2023_05_15_1555-389edb075d5e_.py\n          - 2023_06_02_1845-8b9901c4cc2c_atlassian_connect.py\n          - 2023_06_05_1541-cb9ab45eb78f_confluence_dest_update.py\n          - 2023_05_29_0301-b2eb47841833_forge_tables.py\n          - 2023_05_17_2051-a4ee5f0e5c49_remove_document_reference_unique_.py\n          - 2023_06_06_0135-a61fd4303d02_add_org_url_to_connect_installs.py\n          - 2023_05_23_2150-920f9d3ede4c_add_identifiers_to_installation_tables.py\n        - migrate.py\n        - script.py.mako\n        - seed_database.py\n        - init_database.py\n        - __init__.py\n        - env.py\n      - eave\n        - core\n          - public\n            - requests\n              - oauth\n                - base.py\n                - slack_oauth.py\n                - github_oauth.py\n                - shared.py\n                - __init__.py\n                - atlassian_oauth.py\n                - google_oauth.py\n              - atlassian_integration.py\n              - team.py\n              - authed_account.py\n              - github_integration.py\n              - subscriptions.py\n              - status.py\n              - slack_integration.py\n              - __init__.py\n              - documents.py\n              - connect_integration.py\n              - noop.py\n            - middlewares\n              - authentication.py\n              - team_lookup.py\n              - __init__.py\n              - development_bypass.py\n            - http_endpoint.py\n            - exception_handlers.py\n            - __init__.py\n          - internal\n            - oauth\n              - slack.py\n              - google.py\n              - __init__.py\n              - state_cookies.py\n              - atlassian.py\n              - models.py\n            - orm\n              - slack_installation.py\n              - connect_installation.py\n              - base.py\n              - github_installation.py\n              - team.py\n              - account.py\n              - subscription.py\n              - __init__.py\n              - util.py\n              - atlassian_installation.py\n              - document_reference.py\n              - resource_mutex.py\n              - confluence_destination.py\n            - destinations\n            - document_client.py\n            - __init__.py\n            - database.py\n            - config.py\n          - __init__.py\n          - app.py\n      - bin\n        - lint\n        - format\n        - repl\n        - setup\n        - appengine-dev-server\n        - logs\n        - run-db-migration\n        - deploy\n        - setup-db\n        - repl.py\n        - test\n        - status\n        - create-db-migration\n      - tests\n        - core\n          - signature_verification_test.py\n          - base.py\n          - delete_document_test.py\n          - atlassian_oauth_test.py\n          - confluence_destination_test.py\n          - installations_test.py\n          - subscription_test.py\n          - resource_mutex_test.py\n          - slack_oauth_test.py\n          - search_documents_test.py\n          - connect_integration_test.py\n          - team_test.py\n          - body_parser_middleware_test.py\n          - status_endpoint_test.py\n          - origin_middleware_test.py\n          - __init__.py\n          - authed_account_test.py\n          - team_requests_test.py\n          - slack_installation_test.py\n          - google_oauth_test.py\n          - subscription_requests_test.py\n          - team_lookup_middleware_test.py\n      - app.eave-production.yaml\n      - README.md\n      - requirements-vendor.txt\n      - alembic.ini\n      - requirements.txt\n      - app.eavefyi-dev.yaml\n      - requirements-dev.txt\n      - cloudbuild.yaml\n    - slack\n      - eave\n        - slack\n          - requests\n            - warmup.py\n            - event_processor.py\n            - __init__.py\n            - event_callback.py\n          - brain\n            - base.py\n            - intent_processing.py\n            - communication.py\n            - message_prompts.py\n            - subscription_management.py\n            - document_management.py\n            - context_building.py\n            - document_metadata.py\n            - core.py\n          - slack_app.py\n          - __init__.py\n          - event_handlers.py\n          - slack_models.py\n          - app.py\n          - config.py\n      - bin\n        - lint\n        - format\n        - setup\n        - appengine-dev-server\n        - logs\n        - deploy\n        - test\n        - status\n      - tests\n        - slack\n          - base.py\n          - warmup_test.py\n          - event_processor_test.py\n          - subscription_management_test.py\n          - document_management_test.py\n          - brain_test.py\n          - __init__.py\n          - intent_processing_test.py\n          - prompt_tester.py\n          - events_endpoint_test.py\n          - communication_test.py\n      - app.eave-production.yaml\n      - README.md\n      - requirements-vendor.txt\n      - requirements.txt\n      - socketmode.py\n      - app.eavefyi-dev.yaml\n      - requirements-dev.txt\n    - jira\n      - src\n        - events\n          - routes.ts\n          - comment-created.ts\n        - api\n          - routes.ts\n        - types.ts\n        - jira-client.ts\n        - app.ts\n        - config.ts\n      - bin\n        - lint\n        - format\n        - setup\n        - logs\n        - deploy\n        - test\n        - status\n      - server.ts\n      - app.eave-production.yaml\n      - README.md\n      - atlassian-connect.json\n      - pm2.config.cjs\n      - package-lock.json\n      - credentials.json\n      - app.eavefyi-dev.yaml\n      - tsconfig.json\n      - package.json\n      - config.json\n    - appengine-default\n      - main.py\n      - README.md\n      - app.yaml\n    - github\n      - src\n        - events\n          - routes.ts\n          - push.ts\n        - graphql\n          - getResource.graphql\n          - getFileContentsByPath.graphql\n          - getFileContents.graphql\n          - getRefs.graphql\n        - api\n          - routes.ts\n          - content.ts\n          - subscribe.ts\n          - repos.ts\n        - lib\n          - graphql-util.ts\n          - octokit-util.ts\n          - cache.ts\n        - types.ts\n        - app.ts\n        - dispatch.ts\n        - registry.ts\n        - config.ts\n      - bin\n        - lint\n        - format\n        - setup\n        - appengine-dev-server\n        - logs\n        - deploy\n        - test\n        - status\n      - tests\n        - signing.test.ts\n      - server.ts\n      - app.eave-production.yaml\n      - README.md\n      - pm2.config.cjs\n      - package-lock.json\n      - app.eavefyi-dev.yaml\n      - tsconfig.json\n      - package.json\n    - confluence\n      - src\n        - events\n          - routes.ts\n        - api\n          - routes.ts\n          - util.ts\n          - search-content.ts\n          - create-content.ts\n          - delete-content.ts\n          - get-available-spaces.ts\n          - update-content.ts\n        - app.ts\n        - confluence-client.ts\n        - config.ts\n      - bin\n        - lint\n        - format\n        - setup\n        - logs\n        - deploy\n        - test\n        - status\n      - tests\n        - status.test.ts\n        - create-content.test.ts\n      - server.ts\n      - app.eave-production.yaml\n      - README.md\n      - atlassian-connect.json\n      - pm2.config.cjs\n      - package-lock.json\n      - credentials.json\n      - app.eavefyi-dev.yaml\n      - tsconfig.json\n      - package.json\n      - config.json\n    - marketing\n      - eave\n        - marketing\n          - static\n            - images\n              - eave-slack-2x.png\n              - slack-logo-3x.png\n              - notion-logo-3x.png\n              - github-logo-3x.png\n              - sharepoint-logo-3x.png\n              - figma-logo-3x.png\n              - confluence-mock.png\n              - amazon-logo-3x.png\n              - eave-slack-small-2x.png\n              - paypal-logo-3x.png\n              - outlook-logo-3x.png\n              - confluence-mock-mobile.png\n              - disney-logo-3x.png\n              - teams-logo-3x.png\n              - gmail-logo-3x.png\n              - jira-logo-3x.png\n              - google-drive-logo-3x.png\n              - privacy-icons-3x.png\n              - honey-logo-3x.png\n              - e-icon-small.png\n              - github-logo-inline.png\n              - confluence-logo-3x.png\n          - templates\n            - index.html.jinja\n          - js\n            - components\n              - Footer\n                - index.jsx\n              - Copy\n                - index.jsx\n              - EaveLogo\n                - index.jsx\n              - Header\n                - index.jsx\n              - hoc\n                - withTitle.js\n              - Block\n                - index.js\n              - AuthUser\n                - index.jsx\n              - PrivateRoutes\n                - index.jsx\n              - AuthModal\n                - index.jsx\n              - Button\n                - index.jsx\n              - Icons\n                - DownIcon.js\n                - CloseIcon.js\n                - LockIcon.js\n                - HamburgerIcon.js\n                - GoogleIcon.jsx\n                - PurpleCheckIcon.jsx\n                - DocumentIcon.js\n                - SlackIcon.jsx\n                - ConnectIcon.js\n                - AtlassianIcon.jsx\n                - SnapIcon.js\n                - ConfluenceIcon.jsx\n                - ChatboxIcon.jsx\n                - SyncIcon.js\n              - Pages\n                - Dashboard\n                  - StepIcon.jsx\n                  - Steps.jsx\n                  - Thanks.jsx\n                  - Footnote.jsx\n                  - index.jsx\n                - PrivacyPage\n                  - index.jsx\n                - Page\n                  - index.jsx\n                - HomePage\n                  - index.jsx\n                - TermsPage\n                  - index.jsx\n              - Banners\n                - PrivacyBanner\n                  - index.jsx\n                - DocumentationBanner\n                  - index.jsx\n                - IntegrationsBanner\n                  - index.jsx\n                - SlackBanner\n                  - index.jsx\n              - Hero\n                - index.jsx\n              - PageSection\n                - index.jsx\n              - Affiliates\n                - index.js\n              - BlockStack\n                - index.js\n              - ScrollToTop\n                - index.jsx\n            - hooks\n              - useAuthModal.js\n              - useUser.js\n              - useError.js\n            - context\n              - Provider.js\n            - theme\n              - index.js\n            - App.js\n            - asset-helpers.js\n            - index.js\n            - constants.js\n            - cookies.js\n          - __init__.py\n          - app.py\n          - config.py\n      - bin\n        - remove-unused-images\n        - lint\n        - format\n        - setup\n        - appengine-dev-server\n        - logs\n        - deploy\n        - test\n        - status\n      - app.eave-production.yaml\n      - README.md\n      - requirements-vendor.txt\n      - requirements.txt\n      - package-lock.json\n      - app.eavefyi-dev.yaml\n      - requirements-dev.txt\n      - package.json\n      - webpack.config.cjs\n    - archer\n      - eave\n        - archer\n          - main.py\n          - graph_builder.py\n          - service_info.py\n          - render.py\n          - test-repos.md\n          - service_graph.py\n          - service_dependencies.py\n          - __init__.py\n          - util.py\n          - service_registry.py\n          - prompt_exp.py\n          - config.py\n          - fs_hierarchy.py\n      - bin\n        - lint\n        - format\n        - setup\n        - run-exp\n        - logs\n        - deploy\n        - test\n        - status\n      - tests\n        - archer\n          - lorem\n            - long.txt\n            - short.txt\n          - file_contents_test.py\n          - __init__.py\n      - requirements-vendor.txt\n      - requirements.txt\n      - requirements-dev.txt\n      - graph.mermaid\n  - libs\n    - eave-pubsub-schemas\n      - bin\n        - lint\n        - format\n        - sync\n        - setup\n        - test\n      - protos\n        - eave_event.proto\n      - typescript\n        - src\n          - generated\n            - eave_event.ts\n        - bin\n          - lint\n          - format\n          - test\n        - package-lock.json\n        - tsconfig.json\n        - package.json\n      - python\n        - src\n          - eave\n            - pubsub_schemas\n              - generated\n                - eave_event_pb2.pyi\n                - __init__.py\n                - eave_event_pb2.py\n              - __init__.py\n        - bin\n          - lint\n          - format\n          - test\n        - pyproject.toml\n        - test.py\n        - setup.py\n        - setup.cfg\n      - sync_schemas.py\n      - README.md\n      - package-lock.json\n      - requirements-dev.txt\n      - package.json\n    - eave-stdlib-ts\n      - src\n        - connect\n          - types\n            - adf.ts\n          - dev-tunnel-config.ts\n          - connect-client.ts\n          - eave-api-store-adapter.ts\n          - security-policy-middlewares.ts\n          - lifecycle-router.ts\n        - jira-api\n          - models.ts\n        - middleware\n          - request-integrity.ts\n          - exception-handling.ts\n          - logging.ts\n          - development-bypass.ts\n          - body-parser.ts\n          - signature-verification.ts\n          - origin.ts\n          - common-middlewares.ts\n          - require-headers.ts\n        - core-api\n          - operations\n            - status.ts\n            - team.ts\n            - github.ts\n            - subscriptions.ts\n            - connect.ts\n            - slack.ts\n            - documents.ts\n          - models\n            - integrations.ts\n            - team.ts\n            - atlassian.ts\n            - github.ts\n            - subscriptions.ts\n            - account.ts\n            - connect.ts\n            - slack.ts\n            - documents.ts\n          - enums.ts\n        - confluence-api\n          - models.ts\n          - operations.ts\n        - github-api\n          - client.ts\n          - models.ts\n          - operations.ts\n        - link-handler.ts\n        - eave-origins.ts\n        - signing.ts\n        - logging.ts\n        - util.ts\n        - types.ts\n        - exceptions.ts\n        - openai.ts\n        - api-util.ts\n        - requests.ts\n        - analytics.ts\n        - headers.ts\n        - cache.ts\n        - config.ts\n      - bin\n        - lint\n        - format\n        - setup\n        - test\n      - package-lock.json\n      - tsconfig.json\n      - package.json\n    - eave-stdlib-py\n      - src\n        - eave\n          - stdlib\n            - confluence_api\n              - operations.py\n              - __init__.py\n              - models.py\n            - middleware\n              - base.py\n              - exception_handling.py\n              - body_parsing.py\n              - request_integrity.py\n              - signature_verification.py\n              - __init__.py\n              - logging.py\n              - origin.py\n              - development_bypass.py\n            - core_api\n              - operations\n                - slack.py\n                - team.py\n                - subscriptions.py\n                - account.py\n                - status.py\n                - connect.py\n                - __init__.py\n                - github.py\n                - documents.py\n                - atlassian.py\n              - models\n                - slack.py\n                - error.py\n                - team.py\n                - subscriptions.py\n                - account.py\n                - connect.py\n                - __init__.py\n                - github.py\n                - documents.py\n                - atlassian.py\n                - integrations.py\n              - __init__.py\n              - enums.py\n            - github_api\n              - operations.py\n              - client.py\n              - __init__.py\n              - models.py\n            - cookies.py\n            - slack.py\n            - jwt.py\n            - signing.py\n            - requests.py\n            - request_state.py\n            - cache.py\n            - test_util.py\n            - link_handler.py\n            - api_util.py\n            - __init__.py\n            - endpoints.py\n            - util.py\n            - task_queue.py\n            - analytics.py\n            - logging.py\n            - openai_client.py\n            - headers.py\n            - checksum.py\n            - atlassian.py\n            - eave_origins.py\n            - typing.py\n            - config.py\n            - time.py\n            - exceptions.py\n      - bin\n        - lint\n        - format\n        - setup\n        - test\n      - tests\n        - stdlib\n          - core_api\n            - connect_test.py\n            - __init__.py\n          - link_handler_test.py\n          - __init__.py\n          - util_test.py\n          - analytics_test.py\n        - __init__.py\n      - pyproject.toml\n      - requirements-dev.txt\n      - setup.py\n      - setup.cfg\n  - README.md\n  - ngrok.yml\n\n!!!"
    }
  ],
  "temperature": 0,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

---

### get_dependencies

```
SYSTEM:

You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known service names. Your task is to find which (if any) of the provided APIs/services the code references, uses, calls, or depends on. Your answer will be used to create a high-level system architecture diagram.

Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name. Your full response should be JSON-parseable.
Tokens: 128
```

```
USER:

GitHub organization: eave-fyi

Repository: eave-monorepo

Known services:
- Eave Core Service
- Eave Slack Service
- Eave Jira Service
- Eave Github Service
- Eave Confluence Service
- Eave Marketing Service
- Eave Archer Service
- Eave PubSub Schemas Library
- Eave Standard Library (TypeScript)
- Eave Standard Library (Python)
File path: /home/bryan/code/eave/eave-monorepo/apps/slack/tests/slack/communication_test.py

python Code:
!!!
import re

from slack_sdk.errors import SlackApiError

from eave.stdlib.exceptions import HTTPException
from .base import BaseTestCase


class CommunicationMixinTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_send_response(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        await self.sut.send_response(
            text=self.anystring("text"),
            eave_message_purpose=self.anystring("purpose"),
            opaque_params=self.anydict("params"),
        )

        assert mock.call_count == 1
        assert mock.call_args.kwargs["text"] == f"<@{self._data_message.user}> {self.getstr('text')}"
        assert mock.call_args.kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args.kwargs["thread_ts"] == self.getstr("message.thread_ts")
        assert self.logged_event(
            event_name="eave_sent_message",
            opaque_params={
                "eave_message_purpose": self.getstr("purpose"),
                "eave_message_content": self.getstr("text"),
                **self.getdict("params"),
            },
        )

    async def test_send_response_no_params(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        await self.sut.send_response(text=self.anystring("text"), eave_message_purpose=self.anystring("purpose"))

        assert mock.call_count == 1
        assert self.logged_event(
            event_name="eave_sent_message",
            opaque_params={
                "eave_message_purpose": self.getstr("purpose"),
                "eave_message_content": self.getstr("text"),
            },
        )

    async def test_notify_failure(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        exc = HTTPException(status_code=500, request_id=self.anystring("request id"))
        await self.sut.notify_failure(e=exc)

        assert mock.call_count == 1
        assert re.search("technical issue", mock.call_args.kwargs["text"])
        assert self.logged_event(
            event_name="eave_sent_message",
            opaque_params={
                "eave_request_id": self.getstr("request id"),
            },
        )

    async def test_notify_failure_other_exception(self) -> None:
        mock = self._data_slack_context.client.chat_postMessage
        assert mock.call_count == 0

        exc = ValueError("test error")
        await self.sut.notify_failure(e=exc)

        assert mock.call_count == 1
        assert re.search("technical issue", mock.call_args.kwargs["text"])
        assert self.logged_event(
            event_name="eave_sent_message",
            opaque_params={
                "eave_request_id": None,
            },
        )

    async def test_acknowledge_receipt_with_eave_emoji(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        assert mock.call_count == 0

        await self.sut.acknowledge_receipt()

        assert mock.call_count == 2  # Once for message, once for parent
        assert mock.call_args_list[0].kwargs["name"] == "eave"
        assert mock.call_args_list[0].kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args_list[0].kwargs["timestamp"] == self.getstr("message.ts")

        assert mock.call_args_list[1].kwargs["name"] == "eave"
        assert mock.call_args_list[1].kwargs["channel"] == self.getstr("message.channel")
        assert mock.call_args_list[1].kwargs["timestamp"] == self.getstr("message.thread_ts")

        assert self.logged_event(
            event_name="eave_acknowledged_receipt",
            opaque_params={
                "reaction": "eave",
            },
        )

    async def test_acknowledge_receipt_with_no_eave_emoji(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        mock_response = {"error": "invalid_name"}
        mock.side_effect = [SlackApiError(message=self.anystring(), response=mock_response), None, None]
        assert mock.call_count == 0

        await self.sut.acknowledge_receipt()

        assert mock.call_count == 3  # Once for message, second for message re-try, third for parent.
        assert mock.call_args_list[0].kwargs["name"] == "eave"
        assert mock.call_args_list[1].kwargs["name"] == "large_purple_circle"

        assert self.logged_event(
            event_name="eave_acknowledged_receipt",
            opaque_params={
                "reaction": "large_purple_circle",
            },
        )

        assert not self.logged_event(
            event_name="eave_acknowledged_receipt",
            opaque_params={
                "reaction": "eave",
            },
        )

    async def test_acknowledge_receipt_with_some_other_error(self) -> None:
        mock = self._data_slack_context.client.reactions_add
        mock_response = {"error": self.anystring()}
        mock.side_effect = SlackApiError(message=self.anystring(), response=mock_response)

        await self.sut.acknowledge_receipt()
        # error not raised

!!!
Tokens: 1248
```

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known service names. Your task is to find which (if any) of the provided APIs/services the code references, uses, calls, or depends on. Your answer will be used to create a high-level system architecture diagram.\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name. Your full response should be JSON-parseable."
    },
    {
      "role": "user",
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\n- Eave PubSub Schemas Library\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\nFile path: /home/bryan/code/eave/eave-monorepo/apps/slack/tests/slack/communication_test.py\n\npython Code:\n!!!\nimport re\n\nfrom slack_sdk.errors import SlackApiError\n\nfrom eave.stdlib.exceptions import HTTPException\nfrom .base import BaseTestCase\n\n\nclass CommunicationMixinTest(BaseTestCase):\n    async def asyncSetUp(self) -> None:\n        await super().asyncSetUp()\n\n    async def test_send_response(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        await self.sut.send_response(\n            text=self.anystring(\"text\"),\n            eave_message_purpose=self.anystring(\"purpose\"),\n            opaque_params=self.anydict(\"params\"),\n        )\n\n        assert mock.call_count == 1\n        assert mock.call_args.kwargs[\"text\"] == f\"<@{self._data_message.user}> {self.getstr('text')}\"\n        assert mock.call_args.kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args.kwargs[\"thread_ts\"] == self.getstr(\"message.thread_ts\")\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_message_purpose\": self.getstr(\"purpose\"),\n                \"eave_message_content\": self.getstr(\"text\"),\n                **self.getdict(\"params\"),\n            },\n        )\n\n    async def test_send_response_no_params(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        await self.sut.send_response(text=self.anystring(\"text\"), eave_message_purpose=self.anystring(\"purpose\"))\n\n        assert mock.call_count == 1\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_message_purpose\": self.getstr(\"purpose\"),\n                \"eave_message_content\": self.getstr(\"text\"),\n            },\n        )\n\n    async def test_notify_failure(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        exc = HTTPException(status_code=500, request_id=self.anystring(\"request id\"))\n        await self.sut.notify_failure(e=exc)\n\n        assert mock.call_count == 1\n        assert re.search(\"technical issue\", mock.call_args.kwargs[\"text\"])\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_request_id\": self.getstr(\"request id\"),\n            },\n        )\n\n    async def test_notify_failure_other_exception(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        exc = ValueError(\"test error\")\n        await self.sut.notify_failure(e=exc)\n\n        assert mock.call_count == 1\n        assert re.search(\"technical issue\", mock.call_args.kwargs[\"text\"])\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_request_id\": None,\n            },\n        )\n\n    async def test_acknowledge_receipt_with_eave_emoji(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        assert mock.call_count == 0\n\n        await self.sut.acknowledge_receipt()\n\n        assert mock.call_count == 2  # Once for message, once for parent\n        assert mock.call_args_list[0].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[0].kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args_list[0].kwargs[\"timestamp\"] == self.getstr(\"message.ts\")\n\n        assert mock.call_args_list[1].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[1].kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args_list[1].kwargs[\"timestamp\"] == self.getstr(\"message.thread_ts\")\n\n        assert self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"eave\",\n            },\n        )\n\n    async def test_acknowledge_receipt_with_no_eave_emoji(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        mock_response = {\"error\": \"invalid_name\"}\n        mock.side_effect = [SlackApiError(message=self.anystring(), response=mock_response), None, None]\n        assert mock.call_count == 0\n\n        await self.sut.acknowledge_receipt()\n\n        assert mock.call_count == 3  # Once for message, second for message re-try, third for parent.\n        assert mock.call_args_list[0].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[1].kwargs[\"name\"] == \"large_purple_circle\"\n\n        assert self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"large_purple_circle\",\n            },\n        )\n\n        assert not self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"eave\",\n            },\n        )\n\n    async def test_acknowledge_receipt_with_some_other_error(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        mock_response = {\"error\": self.anystring()}\n        mock.side_effect = SlackApiError(message=self.anystring(), response=mock_response)\n\n        await self.sut.acknowledge_receipt()\n        # error not raised\n\n!!!"
    }
  ],
  "temperature": 0,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

---

