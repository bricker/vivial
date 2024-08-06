## Sensitive Variables
You need to create a `.auto.tfvars` file in each project directory (`eave-production`, etc). Run `terraform plan` and it will tell you which variables are missing.

### Using the 1Password CLI

**Note**: There is no shared Eave vault in 1Password. You can still do this with your personal 1Password account, but you'll need to get the values from somewhere else.

The 1Password CLI can be used to inject the vales into the `.auto.tfvars` file:

```sh
echo "{{ op://Eave Shared/tfvars - eave-staging/content }}" | op inject -o .auto.tfvars
```

The above shows the vault, item, and content names for better readability; however, it's recommended to use the IDs for each one, which can be retrieved via the 1Password CLI (`op item get`), so that the command isn't affected by renames.

## Slack Notification Channel Auth Token

The variable `GCP_MONITORING_SLACK_AUTH_TOKEN` is used by GCP Monitoring for the Slack notification channel(s). It can be obtained by going through the flow to add a Slack channel in the GCP console, going through the flow the install the Google Cloud Monitoring Slack app into Slack, and looking at the dev tools network tab to find a request containing this token. As of writing, the request is to a path "ALERTING_O_AUTH_TOKEN_EXCHANGE_ENTITY_SERVICE_GQL_TRANSPORT", and the auth token is in the response. You do _not_ need to actually add the slack notification channel - you can cancel after you have the auth token, and let Terraform add the channel.
