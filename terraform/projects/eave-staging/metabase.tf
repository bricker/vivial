locals {
  metabase_instances = toset([
    "metabase-01",
  ])
}

# Create service accounts for Metabase apps
module "metabase_apps_service_accounts" {
  for_each = local.metabase_instances

  source = "../../modules/gke_app_service_account"
  project_id = local.project_id
  app = each.value
  k8s_namespace = "metabase"
}

# Create custom role for Metabase apps
module "metabase_app_base_role" {
  source = "../../modules/gcp/custom_role"
  role_id     = "eave.metabaseApp"
  title       = "Metabase App"
  description       = "Permissions needed by the Metabase app"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
    "roles/logging.logWriter"
  ]
}

# Bind the base metabase app role to all metabase app service accounts. This is authoritative.
resource "google_project_iam_binding" "metabase_app_base_role_bindings" {
  project = local.project_id
  role    = module.metabase_app_base_role.role.id
  members = [
    for _, sa in module.metabase_apps_service_accounts:
      "serviceAccount:${sa.service_account.email}"
  ]
}

module "cloudsql_metabase" {
  source = "../../modules/gcp/cloud_sql"
  project_id = local.project_id
  region = local.region
  zone = local.zone
  instance_name = "metabase"
  environment = local.environment

  databases = [ for name, _ in local.metabase_instances : "${name}-db" ]

  users = {
    for name in local.metabase_instances:
      name => {
        email = module.metabase_apps_service_accounts[name].service_account.email,
        user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
      }
  }
}

# https://cloud.google.com/sql/docs/mysql/iam-conditions#allow_users_to_connect_to_specific_instances
# data "google_iam_policy" "sql_iam_policy" {
#   binding {
#     role = "roles/cloudsql.client"
#     members = [
#       "serviceAccount:${google_project_service_identity.gcp_sa_cloud_sql.email}",
#     ]
#     condition {
#       expression  = "resource.name == 'projects/${data.google_project.project.project_id}/instances/${google_sql_database_instance.default.name}' && resource.type == 'sqladmin.googleapis.com/Instance'"
#       title       = "created"
#       description = "Cloud SQL instance creation"
#     }
#   }
# }

# resource "google_project_iam_policy" "project" {
#   project     = data.google_project.project.project_id
#   policy_data = data.google_iam_policy.sql_iam_policy.policy_data
# }