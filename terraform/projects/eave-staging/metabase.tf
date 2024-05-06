locals {
  metabase_instances = toset([])
}

module "metabase_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.metabaseApp"
  title       = "Metabase App"
  description = "Permissions needed by the Metabase apps"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

# Create app service accounts
module "metabase_service_accounts" {
  for_each = local.metabase_instances

  source         = "../../modules/gke_app_service_account"
  project_id     = local.project_id
  app            = "metabase-${each.key}"
  kube_namespace = "metabase"
}

# Bind the custom roles to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "metabase_role_bindings" {
  project = local.project_id
  role    = module.metabase_role.role.id

  members = [
    for key, sa in module.metabase_service_accounts :
    "serviceAccount:${sa.service_account.email}"
  ]
}
