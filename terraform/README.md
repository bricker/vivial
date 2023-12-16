## Sensitive Variables
You need to create a `.auto.tfvars` file in each project directory (`eave-production`, etc). Run `terraform plan` and it will tell you which variables are missing. Get the values from GCP secret manager (the keys match).

## Slack Notification Channel Auth Token

The variable `GCP_MONITORING_SLACK_AUTH_TOKEN` is used by GCP Monitoring for the Slack notification channel(s). The value is available in GCP secret manager under the same key. If it needs to be obtained again (eg if it changes), it can be obtained by goinging through the flow to add a Slack channel in the GCP console, and looking at the dev tools network tab to find a request containing this token. As of writing, the request is to a path "ALERTING_O_AUTH_TOKEN_EXCHANGE_ENTITY_SERVICE_GQL_TRANSPORT".