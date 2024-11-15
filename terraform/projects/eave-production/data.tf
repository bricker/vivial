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

data "google_compute_network" "primary" {
  name = module.project_base.network_name
}

data "google_compute_subnetwork" "primary" {
  self_link = module.project_base.subnetwork_self_link
}

data "google_service_account" "app_service_accounts" {
  for_each = toset([
    module.core_api_app.service_account_id,
    module.dashboard_app.service_account_id,
  ])
  account_id = each.value
}
