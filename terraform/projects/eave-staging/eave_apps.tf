locals {
  apps = {
    "core-api" = {
      domain_prefix = "api"
      custom_roles = [
        "eave.eaveApp",
        "eave.eaveAppCloudsqlIamClient"
      ]
    }

    "dashboard" = {
      domain_prefix = "dashboard"
      custom_roles = [
        "eave.eaveApp"
      ]
    }

    "metabase" = {
      domain_prefix = "metabase"
      custom_roles = [
        "eave.metabaseApp"
      ]
    }
  }
}

# Define the base app role
module "eave_app_base_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.eaveApp"
  title       = "Eave App"
  description = "Standard permissions needed by all Eave apps"
  base_roles = [
    "roles/logging.logWriter",
    "roles/cloudkms.signerVerifier",
    "roles/secretmanager.secretAccessor",
  ]
}

# Define CloudSQL IAM role
module "eave_cloudsql_iam_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.eaveAppCloudsqlIamClient"
  title       = "Eave App CloudSQL IAM Client"
  description = "Eave App that needs to connect/use Cloud SQL via IAM"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

# Create custom role for Metabase app
module "metabase_app_base_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.metabaseApp"
  title       = "Metabase App"
  description = "Permissions needed by the Metabase apps"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
    "roles/logging.logWriter",
  ]
}

# Create app service accounts
module "apps_service_accounts" {
  for_each = local.apps

  source         = "../../modules/gke_app_service_account"
  project_id     = local.project_id
  app            = each.key
  kube_namespace = "eave"
}

# Bind the eave.eaveApp role to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "eave_app_base_role_bindings" {
  project = local.project_id
  role    = module.eave_app_base_role.role.id
  members = [
    for app, props in local.apps :
    "serviceAccount:${module.apps_service_accounts[app].service_account.email}"
    if contains(props.custom_roles, module.eave_app_base_role.role.role_id)
  ]
}

# Bind the eave.eaveAppCloudsqlIamClient role to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "eave_cloudsql_iam_role_bindings" {
  project = local.project_id
  role    = module.eave_cloudsql_iam_role.role.id
  members = [
    for app, props in local.apps :
    "serviceAccount:${module.apps_service_accounts[app].service_account.email}"
    if contains(props.custom_roles, module.eave_cloudsql_iam_role.role.role_id)
  ]
}

# Bind the eave.metabaseApp role to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "eave_metabase_role_bindings" {
  project = local.project_id
  role    = module.metabase_app_base_role.role.id
  members = [
    for app, props in local.apps :
    "serviceAccount:${module.apps_service_accounts[app].service_account.email}"
    if contains(props.custom_roles, module.metabase_app_base_role.role.role_id)
  ]
}

module "dns_apps" {
  for_each = local.apps

  source        = "../../modules/dns"
  domain_prefix = each.value.domain_prefix
  zone          = module.dns_zone_base_domain.zone
}
