locals {
  eave_apps = toset([
    "core-api"
  ])
}

# Create app service accounts
module "eave_apps_service_accounts" {
  for_each = local.eave_apps

  source = "../../modules/gke_app_service_account"
  project_id = local.project_id
  app = each.value
  kube_namespace = "eave-apps"
}

# Define the base app role
module "eave_app_base_role" {
  source = "../../modules/custom_role"
  role_id     = "eave.eaveApp"
  title       = "Eave App"
  description = "Standard permissions needed by all Eave apps"
  base_roles = [
    "roles/logging.logWriter",
    "roles/cloudkms.signerVerifier",
    "roles/secretmanager.secretAccessor",
    "roles/pubsub.publisher",
  ]
}

# Bind the base app role to all app service accounts. This is authoritative.
resource "google_project_iam_binding" "eave_app_base_role_bindings" {
  project = local.project_id
  role    = module.eave_app_base_role.role.id
  members = [
    for _, sa in module.eave_apps_service_accounts:
      "serviceAccount:${sa.service_account.email}"
  ]
}

# Define CloudSQL IAM role
module "eave_cloudsql_iam_role" {
  source = "../../modules/custom_role"
  role_id     = "eave.eaveAppCloudsqlIamClient"
  title       = "Eave App CloudSQL IAM Client"
  description = "Eave App that needs to connect/use Cloud SQL via IAM"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

# Bind the custom CloudSQL IAM role. This is authoritative.
resource "google_project_iam_binding" "eave_cloudsql_iam_role_bindings" {
  project = local.project_id
  role    = module.eave_cloudsql_iam_role.role.id
  members = [
    "serviceAccount:${module.eave_apps_service_accounts["core-api"].service_account.email}"
  ]
}

# Create core Eave CloudSQL Instance
module "cloudsql_eave_core" {
  source = "../../modules/cloud_sql"
  project_id = local.project_id
  region = local.region
  zone = local.zone
  instance_name = "eave-pg-core"
  environment = local.environment

  databases = [
    "eave"
  ]

  users = {
    "core-api" = {
      email = module.eave_apps_service_accounts["core-api"].service_account.email,
      user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
    }
  }
}