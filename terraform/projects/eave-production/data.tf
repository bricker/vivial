# Configure kubernetes provider with Oauth2 access token.
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/client_config
# This fetches a new token, which will expire in 1 hour.
data "google_client_config" "default" {}

data "google_project" "default" {}

data "google_project" "staging" {
  # This is needed for granting the Staging Thoropass Integration service account the org thoropass role.
  # Because the organization configuration is managed by the
  project_id = "eave-staging"
}
